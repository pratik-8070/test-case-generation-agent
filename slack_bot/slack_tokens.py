"""Keep a rotating Slack app-level token (xoxe.xapp-...) alive.

With token rotation enabled (it can't be turned off), Slack app-level tokens expire after 12 hours and come
with a single-use refresh token. This module trades the refresh token for a new pair via oauth.v2.access
before the token expires, persists the pair in .slack_app_token.json (mode 600), and hands the new token
to the running Socket Mode client, which reads it on every reconnect.

Needs SLACK_APP_CLIENT_ID, SLACK_APP_CLIENT_SECRET and, the first time, SLACK_APP_REFRESH_TOKEN (shown once
when the app-level token is created). Without them the static SLACK_APP_TOKEN is used as before.
Not SLACK_CLIENT_ID / SLACK_CLIENT_SECRET: Slack Bolt reads those names and switches to multi-workspace OAuth
mode, ignoring the bot token ("your installation with this app is no longer available").
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from qa_tools.common import ROOT

log = logging.getLogger("slack_bot.tokens")

STATE_FILE = Path(os.environ.get("SLACK_TOKEN_STATE_FILE", ROOT / ".slack_app_token.json"))
REFRESH_URL = "https://slack.com/api/oauth.v2.access"
REFRESH_MARGIN = 3600  # renew an hour before expiry
RETRY_AFTER = 300
DEAD_RETRY_AFTER = 1800  # after a permanent failure, retry rarely (a new .env pair needs a restart anyway)
HTTP_TIMEOUT = 60
# Errors that retrying can't fix: the refresh token was spent or the app credentials are wrong.
PERMANENT_ERRORS = ("invalid_refresh_token", "invalid_client", "invalid_client_id", "bad_client_secret", "invalid_grant")
CHECK_EVERY = 60  # poll the wall clock: timers pause while a Mac sleeps, the clock doesn't


class TokenError(Exception):
    pass


def is_rotating(token: str | None) -> bool:
    return bool(token and token.startswith("xoxe."))


class AppTokenManager:
    def __init__(self, client_id: str | None, client_secret: str | None, static_token: str | None,
                 initial_refresh_token: str | None = None, state_file: Path = STATE_FILE):
        self.client_id, self.client_secret = client_id, client_secret
        self.static_token, self.initial_refresh = static_token, initial_refresh_token
        self.state_file = state_file
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls) -> "AppTokenManager":
        return cls(os.environ.get("SLACK_APP_CLIENT_ID"), os.environ.get("SLACK_APP_CLIENT_SECRET"),
                   os.environ.get("SLACK_APP_TOKEN"), os.environ.get("SLACK_APP_REFRESH_TOKEN"))

    @property
    def can_refresh(self) -> bool:
        return bool(self.client_id and self.client_secret and (self.state_file.exists() or self.initial_refresh))

    def _load(self) -> dict:
        """Saved token pair - unless .env holds a different refresh token, which means the user supplied a new pair."""
        if not self.state_file.exists():
            return {}
        state = json.loads(self.state_file.read_text())
        if self.initial_refresh and state.get("seed") != self.initial_refresh:
            return {}
        return state

    def _save(self, state: dict) -> None:
        self.state_file.write_text(json.dumps(state, indent=2))
        self.state_file.chmod(0o600)

    def _post(self, fields: dict) -> dict:
        req = urllib.request.Request(REFRESH_URL, data=urllib.parse.urlencode(fields).encode(),
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                data = json.load(resp)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise TokenError(f"could not reach Slack ({getattr(exc, 'reason', exc)})") from exc
        if not data.get("ok"):
            raise TokenError(data.get("error", "unknown error"))
        return data

    def refresh(self) -> str:
        """Trade the current refresh token for a new access/refresh pair and persist it."""
        with self._lock:
            state = self._load()
            refresh_token = state.get("refresh_token") or self.initial_refresh
            if not refresh_token:
                raise TokenError("no refresh token; set SLACK_APP_REFRESH_TOKEN")
            data = self._post({"client_id": self.client_id, "client_secret": self.client_secret,
                               "grant_type": "refresh_token", "refresh_token": refresh_token})
            new = {"access_token": data["access_token"], "refresh_token": data["refresh_token"],
                   "expires_at": time.time() + int(data.get("expires_in", 43200)),
                   "seed": state.get("seed") or self.initial_refresh}
            self._save(new)  # refresh tokens are single-use: persist before anything else can fail
            log.info("Slack app token renewed; valid for %.1f hours", (new["expires_at"] - time.time()) / 3600)
            return new["access_token"]

    def current(self) -> str:
        """A token that is valid now: renews when rotation is set up and expiry is near."""
        if not self.can_refresh:
            if is_rotating(self.static_token):
                log.warning("SLACK_APP_TOKEN is a rotating token (expires in 12h) but automatic renewal isn't set up; "
                            "add SLACK_APP_CLIENT_ID, SLACK_APP_CLIENT_SECRET and SLACK_APP_REFRESH_TOKEN to .env")
            if not self.static_token:
                raise TokenError("SLACK_APP_TOKEN is not set")
            return self.static_token
        state = self._load()
        if state.get("access_token") and state.get("expires_at", 0) - time.time() > REFRESH_MARGIN:
            return state["access_token"]
        return self.refresh()

    def refresh_due(self, now: float | None = None) -> bool:
        return (now or time.time()) >= self._load().get("expires_at", 0) - REFRESH_MARGIN

    def start_auto_refresh(self, on_new_token, on_failure=None) -> threading.Thread | None:
        """Background thread that renews before expiry and passes each new token to on_new_token.

        on_failure(message) is called once when renewal fails permanently (e.g. a spent refresh token), so the
        bot can alert people before the token runs out.
        """
        if not self.can_refresh:
            return None

        def loop():
            alerted = False
            while True:
                time.sleep(CHECK_EVERY)
                if not self.refresh_due():
                    continue
                try:
                    on_new_token(self.refresh())
                    alerted = False
                except TokenError as exc:
                    permanent = any(code in str(exc) for code in PERMANENT_ERRORS)
                    wait = DEAD_RETRY_AFTER if permanent else RETRY_AFTER
                    log.error("Slack app token renewal failed: %s; retrying in %ss", exc, wait)
                    if permanent and not alerted and on_failure is not None:
                        alerted = True
                        try:
                            on_failure(str(exc))
                        except Exception:  # alerting must never kill the renewal loop
                            log.exception("could not send the token alert")
                    time.sleep(wait)

        thread = threading.Thread(target=loop, name="slack-token-refresh", daemon=True)
        thread.start()
        return thread
