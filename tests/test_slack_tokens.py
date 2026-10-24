"""Rotating Slack app-level token renewal (Slack faked)."""

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401

from slack_bot.slack_tokens import AppTokenManager, TokenError, is_rotating


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.state = self.tmp / "state.json"

    def _mgr(self, **kw):
        args = dict(client_id="cid", client_secret="sec", static_token="xoxe.xapp-1-old", initial_refresh_token="xoxe-1-r0",
                    state_file=self.state)
        args.update(kw)
        return AppTokenManager(**args)

    def test_static_token_when_renewal_not_configured(self):
        m = self._mgr(client_id=None, initial_refresh_token=None, static_token="xapp-1-forever")
        self.assertFalse(m.can_refresh)
        self.assertEqual(m.current(), "xapp-1-forever")
        self.assertIsNone(m.start_auto_refresh(lambda t: None))
        with self.assertLogs("slack_bot.tokens", "WARNING"):
            self._mgr(client_id=None, initial_refresh_token=None).current()  # rotating token without renewal
        with self.assertRaises(TokenError):
            self._mgr(client_id=None, initial_refresh_token=None, static_token=None).current()

    def test_first_use_refreshes_and_persists_single_use_pair(self):
        m = self._mgr()
        reply = {"ok": True, "access_token": "xoxe.xapp-1-new", "refresh_token": "xoxe-1-r1", "expires_in": 43200, "token_type": "app_level"}
        with mock.patch.object(m, "_post", return_value=reply) as post:
            self.assertEqual(m.current(), "xoxe.xapp-1-new")
            self.assertEqual(m.current(), "xoxe.xapp-1-new")  # cached, still fresh
        post.assert_called_once()
        self.assertEqual(post.call_args.args[0], {"client_id": "cid", "client_secret": "sec",
                                                  "grant_type": "refresh_token", "refresh_token": "xoxe-1-r0"})
        saved = json.loads(self.state.read_text())
        self.assertEqual(saved["refresh_token"], "xoxe-1-r1")
        self.assertEqual(oct(self.state.stat().st_mode & 0o777), "0o600")

    def test_renews_near_expiry_with_latest_refresh_token(self):
        self.state.write_text(json.dumps({"access_token": "a1", "refresh_token": "xoxe-1-r5", "expires_at": time.time() + 600}))
        m = self._mgr(initial_refresh_token=None)
        with mock.patch.object(m, "_post", return_value={"ok": True, "access_token": "a2", "refresh_token": "xoxe-1-r6"}) as post:
            self.assertEqual(m.current(), "a2")
        self.assertEqual(post.call_args.args[0]["refresh_token"], "xoxe-1-r5")

    def test_refresh_due_uses_wall_clock(self):
        now = time.time()
        self.state.write_text(json.dumps({"access_token": "a", "refresh_token": "r", "expires_at": now + 5 * 3600, "seed": "xoxe-1-r0"}))
        m = self._mgr()
        self.assertFalse(m.refresh_due(now))
        self.assertTrue(m.refresh_due(now + 4.5 * 3600))   # e.g. the Mac slept for hours
        self.assertTrue(m.refresh_due(now + 9 * 3600))     # already expired: renew straight away

    def test_new_pair_in_env_replaces_spent_saved_pair(self):
        self.state.write_text(json.dumps({"access_token": "dead", "refresh_token": "spent", "expires_at": time.time() - 3600,
                                          "seed": "xoxe-1-old-seed"}))
        m = self._mgr(initial_refresh_token="xoxe-1-new-seed")
        with mock.patch.object(m, "_post", return_value={"ok": True, "access_token": "fresh", "refresh_token": "r2"}) as post:
            self.assertEqual(m.current(), "fresh")
        self.assertEqual(post.call_args.args[0]["refresh_token"], "xoxe-1-new-seed")  # not the spent one
        self.assertEqual(json.loads(self.state.read_text())["seed"], "xoxe-1-new-seed")
        with mock.patch.object(m, "_post", return_value={"ok": True, "access_token": "a3", "refresh_token": "r3"}) as post:
            m.refresh()
        self.assertEqual(post.call_args.args[0]["refresh_token"], "r2")  # same seed: keep rotating from the saved pair

    def test_permanent_failure_alerts_once(self):
        m = self._mgr()
        calls, alerts = [], []
        sleeps = iter([None, None, StopIteration])

        def fake_sleep(_):
            nxt = next(sleeps)
            if nxt is StopIteration:
                raise SystemExit
        with mock.patch("slack_bot.slack_tokens.time.sleep", side_effect=fake_sleep), \
                mock.patch.object(m, "refresh_due", return_value=True), \
                mock.patch.object(m, "refresh", side_effect=TokenError("invalid_refresh_token")), \
                mock.patch("slack_bot.slack_tokens.threading.Thread") as thread:
            m.start_auto_refresh(calls.append, alerts.append)
            loop = thread.call_args.kwargs["target"]
            with self.assertRaises(SystemExit):
                loop()
        self.assertEqual(alerts, ["invalid_refresh_token"])
        self.assertEqual(calls, [])

    def test_error_reply(self):
        m = self._mgr()
        with mock.patch.object(m, "_post", side_effect=TokenError("invalid_refresh_token")):
            with self.assertRaises(TokenError):
                m.refresh()
        self.assertFalse(self.state.exists())

    def test_is_rotating(self):
        self.assertTrue(is_rotating("xoxe.xapp-1-x"))
        self.assertFalse(is_rotating("xapp-1-x"))


if __name__ == "__main__":
    unittest.main()
