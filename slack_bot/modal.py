"""The /test-case modal: Block Kit view definition and submission parsing."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .sources import UPLOAD_FILETYPES, parse_links

CALLBACK_ID = "test_case_modal"
MANUAL_CALLBACK_ID = "test_case_manual_content"
TITLE = {"type": "plain_text", "text": "Generate test cases"}
MAX_INPUT_CHARS = 3000  # Slack's limit for a plain_text_input

# value -> (radio label, file the bot uploads from the run folder)
FORMATS = {
    "gsheet": ("Google Sheet (link)", "test-suite.json"),  # only offered once Google Sheets is connected
    "md": ("Markdown report", "test-suite.md"),
    "csv": ("CSV (Excel / test tools)", "test-suite.csv"),
    "json": ("JSON (automation)", "test-suite.json"),
}
DEFAULT_FORMAT = "md"


@dataclass
class TestCaseRequest:
    channel_id: str
    user_id: str
    feature_name: str
    feature_context: str
    output_format: str
    reference_links: list[str] = field(default_factory=list)
    file_ids: list[str] = field(default_factory=list)


def parse_allowed_channels(raw: str | None) -> set[str]:
    """ALLOWED_CHANNELS env value -> set of channel names/IDs ('#alpha, C0123' -> {'alpha', 'C0123'}). Empty = all."""
    return {c.strip().lstrip("#") for c in (raw or "").split(",") if c.strip().lstrip("#")}


def channel_allowed(channel_id: str, channel_name: str, allowed: set[str]) -> bool:
    if not allowed:
        return True
    return channel_id in allowed or channel_name.lstrip("#").lower() in {a.lower() for a in allowed}


def _option(value: str) -> dict:
    return {"text": {"type": "plain_text", "text": FORMATS[value][0]}, "value": value}


def build_modal(channel_id: str, user_id: str, prefill_name: str = "", allow_uploads: bool = True,
                allow_gsheet: bool = False) -> dict:
    """Modal view. channel/user travel in private_metadata so the submit handler knows where to post.

    allow_uploads=False drops the file field (Slack rejects file_input unless the app has files:read).
    """
    name_element = {
        "type": "plain_text_input",
        "action_id": "value",
        "max_length": 150,
        "placeholder": {"type": "plain_text", "text": "e.g. Add to Cart"},
    }
    if prefill_name.strip():
        name_element["initial_value"] = prefill_name.strip()[:150]

    return {
        "type": "modal",
        "callback_id": CALLBACK_ID,
        "private_metadata": json.dumps({"channel_id": channel_id, "user_id": user_id}),
        "title": TITLE,
        "submit": {"type": "plain_text", "text": "Generate"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "feature_name",
                "label": {"type": "plain_text", "text": "Feature name"},
                "element": name_element,
            },
            {
                "type": "input",
                "block_id": "feature_context",
                "label": {"type": "plain_text", "text": "Feature context"},
                "hint": {"type": "plain_text", "text": "Describe the feature (story, acceptance criteria, rules, limits, exact messages, roles) and paste "
                                                      "every reference link here too: Figma designs, Confluence pages, PRDs, RFCs, Google Docs, API docs. "
                                                      "Links are opened automatically; if one can't be opened you'll be asked to paste its content."},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "value",
                    "multiline": True,
                    "max_length": MAX_INPUT_CHARS,
                    "placeholder": {"type": "plain_text", "text": "Requirement, acceptance criteria and links, e.g.\nhttps://yoursite.atlassian.net/wiki/x/AbC\nhttps://www.figma.com/design/..."},
                },
            },
            *([{
                "type": "input",
                "block_id": "attachments",
                "optional": True,
                "label": {"type": "plain_text", "text": "Attachments"},
                "hint": {"type": "plain_text", "text": "Optional files instead of links: PRD / RFC exports, design screenshots, API specs, existing test cases "
                                                      "(PDF, PNG, JPG, DOCX, MD, TXT, CSV, JSON, YAML). Up to 10 files."},
                "element": {"type": "file_input", "action_id": "value", "filetypes": UPLOAD_FILETYPES, "max_files": 10},
            }] if allow_uploads else []),
            {
                "type": "input",
                "block_id": "output_format",
                "label": {"type": "plain_text", "text": "Test case format"},
                "element": {
                    "type": "radio_buttons",
                    "action_id": "value",
                    "options": [_option(v) for v in FORMATS if v != "gsheet" or allow_gsheet],
                    "initial_option": _option("gsheet" if allow_gsheet else DEFAULT_FORMAT),
                },
            },
        ],
    }


def parse_submission(view: dict, fallback_user_id: str = "") -> TestCaseRequest:
    values = view["state"]["values"]
    meta = json.loads(view.get("private_metadata") or "{}")

    def text(block: str) -> str:
        return (values.get(block, {}).get("value", {}).get("value") or "").strip()

    # file_input submissions carry file objects; only the ids are relied on (details come from files.info).
    files = values.get("attachments", {}).get("value", {}).get("files") or []
    file_ids = [f["id"] if isinstance(f, dict) else str(f) for f in files if f]

    selected = values.get("output_format", {}).get("value", {}).get("selected_option") or {}
    fmt = selected.get("value", DEFAULT_FORMAT)
    return TestCaseRequest(
        channel_id=meta.get("channel_id", ""),
        user_id=meta.get("user_id") or fallback_user_id,
        feature_name=text("feature_name"),
        feature_context=text("feature_context"),
        output_format=fmt if fmt in FORMATS else DEFAULT_FORMAT,
        # Every link in Feature context is fetched; duplicates removed, order kept.
        reference_links=parse_links(text("feature_context")),
        file_ids=file_ids,
    )


def validate_request(req: TestCaseRequest) -> dict[str, str]:
    """Field errors in Slack's response_action=errors shape (block_id -> message)."""
    errors = {}
    if not req.feature_name:
        errors["feature_name"] = "Give the feature a name."
    if len(req.feature_context) < 20:
        errors["feature_context"] = "Add the feature context (at least a sentence describing the expected behaviour)."
    return errors


# ---------------------------------------------------------------- follow-up screens (same modal, updated in place)

def _section(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text[:3000]}}


def checking_view(n_links: int, n_files: int) -> dict:
    what = " and ".join(x for x in (f"{n_links} link{'s' * (n_links != 1)}" if n_links else "",
                                    f"{n_files} file{'s' * (n_files != 1)}" if n_files else "") if x)
    return {"type": "modal", "title": TITLE, "close": {"type": "plain_text", "text": "Close"},
            "blocks": [_section(f":hourglass_flowing_sand: Opening {what}… this usually takes a few seconds.")]}


def starting_view(req: TestCaseRequest, read: int = 0, pasted: int = 0) -> dict:
    lines = [f":rocket: Generating test cases for *{req.feature_name}*."]
    if read or pasted:
        lines.append(f"Reference material: {read} read" + (f", {pasted} pasted" if pasted else "") + ".")
    lines.append(f"Results will be posted in <#{req.channel_id}> in a few minutes. You can close this window.")
    return {"type": "modal", "title": TITLE, "close": {"type": "plain_text", "text": "Close"},
            "blocks": [_section("\n".join(lines))]}


def manual_content_view(key: str, missing: list[tuple[int, str, str]], read_count: int) -> dict:
    """One optional paste box per unreadable source. missing = [(source index, label, reason)]."""
    intro = (f":warning: I couldn't open *{len(missing)}* of your links/files"
             + (f" (the other {read_count} were read)" if read_count else "") + ".\n"
             "Paste their content below so the test cases are based on it — the relevant requirements, acceptance "
             "criteria or a description of the design is enough. Leave a box empty to continue without it.")
    blocks = [_section(intro)]
    for index, label, reason in missing:
        blocks.append({
            "type": "input",
            "block_id": f"manual_{index}",
            "optional": True,
            "label": {"type": "plain_text", "text": (label if len(label) <= 140 else label[:139] + "…")},
            "hint": {"type": "plain_text", "text": f"Couldn't open: {reason}"[:1900]},
            "element": {"type": "plain_text_input", "action_id": "value", "multiline": True, "max_length": MAX_INPUT_CHARS,
                        "placeholder": {"type": "plain_text", "text": "Paste the page content or describe the design"}},
        })
    return {"type": "modal", "callback_id": MANUAL_CALLBACK_ID, "private_metadata": json.dumps({"key": key}),
            "title": TITLE, "submit": {"type": "plain_text", "text": "Generate"},
            "close": {"type": "plain_text", "text": "Cancel"}, "blocks": blocks}


def parse_manual_content(view: dict) -> tuple[str, dict[int, str]]:
    key = json.loads(view.get("private_metadata") or "{}").get("key", "")
    pasted = {}
    for block_id, actions in view["state"]["values"].items():
        if block_id.startswith("manual_"):
            text = (actions.get("value", {}).get("value") or "").strip()
            if text:
                pasted[int(block_id.split("_", 1)[1])] = text
    return key, pasted


def expired_view() -> dict:
    return {"type": "modal", "title": TITLE, "close": {"type": "plain_text", "text": "Close"},
            "blocks": [_section(":hourglass: This request expired (the bot was restarted). Please run `/test-case` again.")]}
