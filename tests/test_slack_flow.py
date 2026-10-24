"""End-to-end Slack flow with Slack and the agent mocked: submit -> check links -> (paste missing content) -> run."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401  (project root on sys.path)

try:
    import slack_bolt  # noqa: F401
except ImportError:  # the bot's dependencies live in .venv; plain `python3 -m unittest` skips this file
    slack_bolt = None

if slack_bolt is not None:
    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
    os.environ.setdefault("SLACK_CLIENT_ID", "1.2")  # must NOT switch Bolt into multi-workspace OAuth mode
    os.environ.setdefault("SLACK_CLIENT_SECRET", "x")
    with mock.patch("slack_sdk.web.client.WebClient.auth_test",
                    return_value=mock.Mock(headers={"x-oauth-scopes": "commands,chat:write"},
                                           **{"get.return_value": None, "__getitem__": lambda s, k: "U"})):
        from slack_bot import app as bot

from slack_bot.modal import TestCaseRequest
from slack_bot.sources import Source


@unittest.skipIf(slack_bolt is None, "slack_bolt not installed (run with .venv/bin/python)")
class SlackFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run_dir = self.tmp / "run"
        self.run_dir.mkdir()
        self.input_path = self.run_dir / "input.md"
        self.req = TestCaseRequest("C1", "U1", "Create Listing", "https://acme.atlassian.net/wiki/x/AQAL",
                                   "md", ["https://acme.atlassian.net/wiki/x/AQAL", "https://www.figma.com/design/K/x"])
        patches = [
            mock.patch.object(bot, "prepare_run", return_value=(self.run_dir, self.input_path)),
            mock.patch.object(bot.app.client, "views_update"),
            mock.patch.object(bot.executor, "submit"),
        ]
        self.prepare, self.views_update, self.submit = [p.start() for p in patches]
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(shutil.rmtree, self.tmp)
        bot.PENDING.clear()

    def _sources(self, confluence_ok: bool, figma_ok: bool):
        return [Source("link", self.req.reference_links[0], self.tmp / "c.md" if confluence_ok else None,
                       note="" if confluence_ok else "page not found"),
                Source("link", self.req.reference_links[1], self.tmp / "f.png" if figma_ok else None,
                       note="" if figma_ok else "Figma links need FIGMA_TOKEN")]

    def test_single_workspace_mode_even_with_client_credentials_in_env(self):
        self.assertIsNone(bot.app.oauth_flow)
        self.assertNotIn("SLACK_CLIENT_ID", os.environ)

    def test_submit_with_links_keeps_modal_open(self):
        ack = mock.Mock()
        view = {"id": "V1", "private_metadata": '{"channel_id": "C1", "user_id": "U1"}', "state": {"values": {
            "feature_name": {"value": {"value": "Create Listing"}},
            "feature_context": {"value": {"value": "https://acme.atlassian.net/wiki/x/AQAL"}},
            "output_format": {"value": {"selected_option": {"value": "md"}}}}}}
        with mock.patch.object(bot.link_checker, "submit") as check:
            bot.on_submit(ack, {"user": {"id": "U1"}}, view)
        self.assertEqual(ack.call_args.kwargs["response_action"], "update")
        self.assertIn("Opening 1 link", str(ack.call_args.kwargs["view"]))
        check.assert_called_once()
        self.assertEqual(check.call_args.args[1], "V1")
        self.assertEqual(check.call_args.args[2].reference_links, ["https://acme.atlassian.net/wiki/x/AQAL"])

    def test_all_links_readable_starts_run(self):
        with mock.patch.object(bot, "gather_sources", return_value=self._sources(True, True)):
            bot.check_sources("V1", self.req)
        self.assertIn("Generating test cases", str(self.views_update.call_args.kwargs["view"]))
        self.assertIs(self.submit.call_args.args[0], bot.process_request)
        self.assertEqual(bot.PENDING, {})

    def test_unreadable_link_asks_for_content_then_runs_with_it(self):
        with mock.patch.object(bot, "gather_sources", return_value=self._sources(True, False)):
            bot.check_sources("V1", self.req)
        asked = self.views_update.call_args.kwargs["view"]
        self.assertEqual(asked["callback_id"], bot.MANUAL_CALLBACK_ID)
        self.assertIn("manual_1", str(asked["blocks"]))
        self.submit.assert_not_called()
        self.assertEqual(len(bot.PENDING), 1)

        asked["state"] = {"values": {"manual_1": {"value": {"value": "Screen 1: type picker with 5 listing types"}}}}
        ack = mock.Mock()
        bot.on_manual_submit(ack, asked)
        self.assertEqual(ack.call_args.kwargs["response_action"], "update")
        self.assertIn("1 read, 1 pasted", str(ack.call_args.kwargs["view"]))
        sources = self.submit.call_args.args[5]
        self.assertTrue(all(s.ok for s in sources))
        self.assertIn("type picker", sources[1].path.read_text())
        self.assertEqual(bot.PENDING, {})

    def test_nothing_readable_and_nothing_pasted_is_rejected_in_modal(self):
        with mock.patch.object(bot, "gather_sources", return_value=self._sources(False, False)):
            bot.check_sources("V1", self.req)
        asked = self.views_update.call_args.kwargs["view"]
        asked["state"] = {"values": {}}
        ack = mock.Mock()
        bot.on_manual_submit(ack, asked)
        self.assertEqual(ack.call_args.kwargs["response_action"], "errors")
        self.assertIn("manual_0", ack.call_args.kwargs["errors"])
        self.submit.assert_not_called()
        self.assertEqual(len(bot.PENDING), 1)  # still answerable

    def test_closed_modal_continues_with_readable_sources(self):
        self.views_update.side_effect = [bot.SlackApiError("closed", {"ok": False, "error": "not_found"}), None]
        with mock.patch.object(bot, "gather_sources", return_value=self._sources(True, False)):
            bot.check_sources("V1", self.req)
        self.assertIs(self.submit.call_args.args[0], bot.process_request)
        self.assertEqual(bot.PENDING, {})

    def test_expired_request(self):
        ack = mock.Mock()
        bot.on_manual_submit(ack, {"private_metadata": '{"key": "gone"}', "state": {"values": {}}})
        self.assertIn("expired", str(ack.call_args.kwargs["view"]))


if __name__ == "__main__":
    unittest.main()
