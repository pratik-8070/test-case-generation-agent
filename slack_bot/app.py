"""Slack Bolt app (Socket Mode): /test-case -> modal -> agent run -> results in channel.

Run from the project root:  python3 -m slack_bot.app
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import certifi
from dotenv import load_dotenv

# python.org builds on macOS ship without root certificates; use certifi's bundle
# unless the environment already points somewhere (must happen before any HTTPS call).
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from slack_bolt import App  # noqa: E402
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from . import google_sheets
from .kb import flow as kb_flow
from .net import prefer_ipv4
from .modal import (CALLBACK_ID, FORMATS, MANUAL_CALLBACK_ID, TestCaseRequest, build_modal, channel_allowed,
                    checking_view, expired_view, manual_content_view, parse_allowed_channels, parse_manual_content,
                    parse_submission, starting_view, validate_request)
from .runner import (AgentSettings, apply_manual_content, gather_sources, has_enough_input, needs_manual_content,
                     prepare_run, run_generation)
from .slack_tokens import AppTokenManager, TokenError
from .sources import Credentials, Source
from .summary import failure_text, progress_text, result_blocks

load_dotenv()
prefer_ipv4()  # some networks publish unreachable IPv6 routes; Python would hang trying them first
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("slack_bot")

# Bolt switches to multi-workspace OAuth (and ignores the bot token) if these are set; this bot is single-workspace.
for _name in ("SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET"):
    if os.environ.pop(_name, None):
        log.warning("%s is set but unused; renamed to SLACK_APP_%s for token renewal", _name, _name.removeprefix("SLACK_"))
app = App(token=os.environ["SLACK_BOT_TOKEN"])
# Agent runs take minutes; run them off Bolt's handler threads and cap parallel runs (cost + CPU).
executor = ThreadPoolExecutor(max_workers=int(os.environ.get("MAX_CONCURRENT_RUNS", "2")))
# Link checks are quick; keep them off the agent pool so the modal never waits behind a long run.
link_checker = ThreadPoolExecutor(max_workers=4)
# Channel names or IDs where /test-case may be used; empty = every channel.
ALLOWED_CHANNELS = parse_allowed_channels(os.environ.get("ALLOWED_CHANNELS"))
CREDENTIALS = Credentials.from_env()


def _has_scope(scope: str) -> bool:
    try:
        granted = app.client.auth_test().headers.get("x-oauth-scopes", "")
    except SlackApiError:
        return False
    return scope in {s.strip() for s in granted.split(",")}


# Slack rejects a modal with a file field unless the app has files:read (also needed to download uploads).
ALLOW_UPLOADS = _has_scope("files:read")


def _channel_list(channels: set[str]) -> str:
    """Render as Slack channel links: IDs (C0123ABC) as <#ID>, names as #name."""
    return ", ".join(f"<#{c}>" if re.fullmatch(r"[CG][A-Z0-9]{6,}", c) else f"#{c}" for c in sorted(channels))


@app.command("/test-case")
def open_modal(ack, body, client):
    if not channel_allowed(body["channel_id"], body.get("channel_name", ""), ALLOWED_CHANNELS):
        ack(f":no_entry_sign: `/test-case` is only available in {_channel_list(ALLOWED_CHANNELS)}.")  # ephemeral: only the caller sees it
        log.info("rejected /test-case from %s (#%s)", body["channel_id"], body.get("channel_name"))
        return
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=build_modal(body["channel_id"], body["user_id"], body.get("text", ""), allow_uploads=ALLOW_UPLOADS,
                         allow_gsheet=google_sheets.is_configured()),
    )


@dataclass
class PendingRun:
    """A request waiting for the user to paste content for links the bot couldn't open."""
    req: TestCaseRequest
    run_dir: Path
    input_path: Path
    sources: list[Source]
    created: float = field(default_factory=time.time)


PENDING: dict[str, PendingRun] = {}
PENDING_LOCK = threading.Lock()
PENDING_TTL = 3600  # seconds a "paste missing content" screen stays answerable


def _remember(pending: PendingRun) -> str:
    key = uuid.uuid4().hex
    with PENDING_LOCK:
        now = time.time()
        for k in [k for k, p in PENDING.items() if now - p.created > PENDING_TTL]:
            del PENDING[k]
        PENDING[key] = pending
    return key


@app.view(CALLBACK_ID)
def on_submit(ack, body, view):
    req = parse_submission(view, body["user"]["id"])
    errors = validate_request(req)
    if errors:
        ack(response_action="errors", errors=errors)
        return
    if req.reference_links or req.file_ids:
        # Keep the modal open while the links are opened, so unreadable ones can be pasted in.
        ack(response_action="update", view=checking_view(len(req.reference_links), len(req.file_ids)))
        link_checker.submit(check_sources, view["id"], req)
    else:
        ack()  # closes the modal; Slack requires this within 3 seconds
        executor.submit(start_run, req)


def _fetch_uploads(client, req: TestCaseRequest) -> list[dict]:
    uploads = []
    for file_id in req.file_ids:
        try:
            uploads.append(client.files_info(file=file_id)["file"])
        except SlackApiError as exc:
            log.warning("files.info %s failed: %s", file_id, exc.response.get("error"))
            uploads.append({"id": file_id, "name": file_id})  # reported back as unreadable
    return uploads


def _update_view(view_id: str, view: dict) -> bool:
    try:
        app.client.views_update(view_id=view_id, view=view)
        return True
    except SlackApiError as exc:  # e.g. the user closed the modal
        log.info("views.update %s failed: %s", view_id, exc.response.get("error"))
        return False


def check_sources(view_id: str, req: TestCaseRequest) -> None:
    """Open every link/file; ask for the content of unreadable ones in the same modal, else start the run."""
    try:
        run_dir, input_path = prepare_run(req)
        sources = gather_sources(req, run_dir, _fetch_uploads(app.client, req), os.environ["SLACK_BOT_TOKEN"], CREDENTIALS)
    except Exception:
        log.exception("source check crashed")
        _update_view(view_id, expired_view())
        return

    missing = needs_manual_content(sources)
    read = sum(s.ok for s in sources)
    log.info("sources for %s: %d read, %d unreadable", run_dir.name, read, len(missing))
    if missing:
        key = _remember(PendingRun(req, run_dir, input_path, sources))
        view = manual_content_view(key, [(i, sources[i].label, sources[i].note) for i in missing], read)
        if _update_view(view_id, view):
            return
        # Modal closed before we could ask: carry on with what was readable (the reply lists the gaps).
        with PENDING_LOCK:
            PENDING.pop(key, None)
    _update_view(view_id, starting_view(req, read=read))
    executor.submit(process_request, app.client, req, run_dir, input_path, sources)


@app.view(MANUAL_CALLBACK_ID)
def on_manual_submit(ack, view):
    key, pasted = parse_manual_content(view)
    with PENDING_LOCK:
        pending = PENDING.pop(key, None)
    if pending is None:
        ack(response_action="update", view=expired_view())
        return
    sources = apply_manual_content(pending.run_dir, pending.sources, pasted)
    if not has_enough_input(pending.req, sources):
        with PENDING_LOCK:
            PENDING[key] = pending  # keep it answerable
        first = next(iter(needs_manual_content(sources)), None)
        ack(response_action="errors", errors={f"manual_{first}": "The feature context has no other details, so paste the "
                                              "content of at least one link (or Cancel and describe the feature)."})
        return
    ack(response_action="update", view=starting_view(pending.req, read=sum(s.ok for s in pending.sources), pasted=len(pasted)))
    executor.submit(process_request, app.client, pending.req, pending.run_dir, pending.input_path, sources)


def start_run(req: TestCaseRequest) -> None:
    """No links or files: nothing to check."""
    run_dir, input_path = prepare_run(req)
    process_request(app.client, req, run_dir, input_path, [])


def _post(client, req: TestCaseRequest, **kwargs) -> dict:
    """Post to the request's channel; if the bot can't post there, DM the user instead."""
    try:
        return client.chat_postMessage(channel=req.channel_id, **kwargs)
    except SlackApiError as exc:
        if exc.response.get("error") not in ("not_in_channel", "channel_not_found"):
            raise
        log.warning("cannot post in %s (%s); falling back to DM", req.channel_id, exc.response.get("error"))
        req.channel_id = req.user_id
        dm = client.chat_postMessage(
            channel=req.user_id,
            text=":information_source: I couldn't post in that channel. Invite me with `/invite @Test Case Generator` "
                 "to get results there. Sending them here instead.")
        return client.chat_postMessage(channel=dm["channel"], **kwargs)


def process_request(client, req: TestCaseRequest, run_dir: Path, input_path: Path, sources: list[Source]) -> None:
    status = _post(client, req, text=progress_text(req))
    channel, ts = status["channel"], status["ts"]
    kb_session, kb_note = None, ""
    if kb_flow.enabled():
        try:
            kb_session, sources = kb_flow.prepare(req.feature_name, req.feature_context, req.reference_links, sources, run_dir)
        except Exception as exc:  # the knowledge base must never block a run
            log.warning("kb prepare failed for %s: %s", run_dir.name, exc)
            kb_note = f"Knowledge base unavailable ({exc})"
    try:
        result = run_generation(req, run_dir, input_path, sources)
    except Exception as exc:  # never leave the progress message hanging
        log.exception("run crashed")
        client.chat_update(channel=channel, ts=ts, text=failure_text(req, str(exc), []))
        return

    log.info("run %s ok=%s cost=%s error=%s", result.run_dir.name, result.ok, result.cost_usd, result.error)
    if not result.ok:
        client.chat_update(channel=channel, ts=ts, text=failure_text(req, result.error, result.check_errors))
        return

    kb_record = None
    if kb_session is not None:
        try:
            kb_record = kb_flow.record(kb_session, req.feature_name, result.analysis, result.suite, result.run_dir, result.sources)
        except Exception as exc:
            log.warning("kb record failed for %s: %s", result.run_dir.name, exc)
            kb_note = f"Couldn't save to the knowledge base ({exc})"

    sheet_url, sheet_note, file_path = None, kb_note, result.file_path
    if req.output_format == "gsheet" and kb_record is None:
        try:
            sheet_url = google_sheets.create_test_case_sheet(result.suite, result.analysis, req.feature_name, result.run_dir)
        except google_sheets.GoogleSheetsError as exc:
            log.warning("google sheet failed for %s: %s", result.run_dir.name, exc)
            sheet_note = f"Couldn't create the Google Sheet ({exc})"
            file_path = result.run_dir / FORMATS["md"][1]

    blocks = result_blocks(req, result.suite, result.analysis, result.sources, sheet_url, sheet_note, kb_record)
    client.chat_update(channel=channel, ts=ts, text=f"Test cases for {req.feature_name}", blocks=blocks)
    if sheet_url or (kb_record and req.output_format == "gsheet"):
        return
    client.files_upload_v2(
        channel=channel,
        thread_ts=ts,
        file=str(file_path),
        filename=f"{result.run_dir.name}-{file_path.name}",
        title=f"{req.feature_name} — {FORMATS['md' if req.output_format == 'gsheet' else req.output_format][0]}",
        initial_comment=f"Run folder: `output/{result.run_dir.name}/`",
    )


def main() -> None:
    log.info("Test Case Generator bot starting (Socket Mode); ai: %s; google sheets: %s; channels: %s; uploads: %s; confluence: %s; figma: %s",
             AgentSettings.from_env().describe(),
             "on" if google_sheets.is_configured() else "off (run: .venv/bin/python -m slack_bot.google_sheets auth)",
             sorted(ALLOWED_CHANNELS) or "all", "on" if ALLOW_UPLOADS else "OFF (add files:read scope and reinstall)",
             f"on ({', '.join(sorted(CREDENTIALS.confluence_sites)) or '*.atlassian.net'})" if CREDENTIALS.confluence_enabled
             else "off (set CONFLUENCE_EMAIL + CONFLUENCE_API_TOKEN)",
             "on" if CREDENTIALS.figma_token else "off (set FIGMA_TOKEN)")
    tokens = AppTokenManager.from_env()
    try:
        app_token = tokens.current()
    except TokenError as exc:
        log.error("Slack app token problem: %s", exc)
        raise SystemExit(1) from exc
    handler = SocketModeHandler(app, app_token)

    def use_new_token(token: str) -> None:
        handler.client.app_token = token  # read on every reconnect

    def alert(reason: str) -> None:
        """The bot token never expires, so it can still warn people when the connection token can't be renewed."""
        text = (f":rotating_light: *Test Case Generator will go offline soon:* its Slack connection token couldn't be "
                f"renewed ({reason}). To fix: Slack app settings → Basic Information → App-Level Tokens → generate a new "
                "token with `connections:write`, copy the token *and* refresh token into `.env` "
                "(SLACK_APP_TOKEN, SLACK_APP_REFRESH_TOKEN), then restart the bot.")
        for channel in sorted(ALLOWED_CHANNELS) or []:
            try:
                app.client.chat_postMessage(channel=channel, text=text)
            except SlackApiError as exc:
                log.warning("token alert to %s failed: %s", channel, exc.response.get("error"))
    if tokens.start_auto_refresh(use_new_token, alert):
        log.info("Slack app token: rotating, renewed automatically every ~11 hours")
    handler.start()


if __name__ == "__main__":
    main()
