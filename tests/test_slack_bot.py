"""Slack bot logic that runs without Slack or the Agent SDK: modal, submission parsing, run prep, result checks, messages."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import FIXTURES, valid_analysis, valid_suite

from slack_bot import runner
from slack_bot.modal import (CALLBACK_ID, FORMATS, TestCaseRequest, build_modal, channel_allowed, parse_allowed_channels,
                             checking_view, manual_content_view, parse_manual_content, parse_submission,
                             starting_view, validate_request)
from slack_bot.sources import Source
from slack_bot.summary import failure_text, progress_text, result_blocks


def _submitted_view(name="Add to Cart", context="A logged-in user can add an in-stock product to the cart. Max 10 per item.",
                    fmt="csv", files=None):
    view = build_modal("C123", "U456")
    view["state"] = {"values": {
        "feature_name": {"value": {"type": "plain_text_input", "value": name}},
        "feature_context": {"value": {"type": "plain_text_input", "value": context or None}},
        "attachments": {"value": {"type": "file_input", "files": files or []}},
        "output_format": {"value": {"type": "radio_buttons", "selected_option": {"value": fmt}}},
    }}
    return view


def _req(fmt="md"):
    return TestCaseRequest("C123", "U456", "Login", "User logs in with email and password.", fmt)


class ModalTests(unittest.TestCase):
    def test_modal_shape(self):
        view = build_modal("C1", "U1", "Checkout")
        self.assertEqual(view["callback_id"], CALLBACK_ID)
        self.assertEqual(json.loads(view["private_metadata"]), {"channel_id": "C1", "user_id": "U1"})
        blocks = {b["block_id"]: b for b in view["blocks"]}
        self.assertEqual(blocks["feature_name"]["element"]["initial_value"], "Checkout")
        self.assertEqual([b["block_id"] for b in view["blocks"]],
                         ["feature_name", "feature_context", "attachments", "output_format"])
        self.assertEqual(blocks["feature_context"]["label"]["text"], "Feature context")
        required = [b["block_id"] for b in view["blocks"] if not b.get("optional")]
        self.assertEqual(required, ["feature_name", "feature_context", "output_format"])
        self.assertEqual(blocks["attachments"]["element"]["type"], "file_input")
        self.assertEqual(blocks["attachments"]["element"]["max_files"], 10)
        radio = blocks["output_format"]["element"]
        self.assertEqual(radio["type"], "radio_buttons")
        self.assertEqual([o["value"] for o in radio["options"]], [f for f in FORMATS if f != "gsheet"])
        self.assertLessEqual(len(view["title"]["text"]), 24)  # Slack limit
        for b in view["blocks"]:  # Slack limits: label 2000, hint 2000 chars
            self.assertLessEqual(len(b.get("hint", {}).get("text", "")), 2000)

    def test_modal_without_upload_permission(self):
        ids = [b["block_id"] for b in build_modal("C1", "U1", allow_uploads=False)["blocks"]]
        self.assertEqual(ids, ["feature_name", "feature_context", "output_format"])

    def test_parse_submission(self):
        req = parse_submission(_submitted_view())
        self.assertEqual((req.channel_id, req.user_id, req.feature_name, req.output_format), ("C123", "U456", "Add to Cart", "csv"))
        self.assertIn("Max 10 per item", req.feature_context)

    def test_links_in_feature_context_and_files(self):
        context = ("Create listing flow, see PRD: https://acme.atlassian.net/wiki/x/AQAL.\n"
                   "Design https://www.figma.com/design/AbC123/App?node-id=1-2 and RFC https://example.com/rfc "
                   "(PRD again: https://acme.atlassian.net/wiki/x/AQAL)")
        req = parse_submission(_submitted_view(context=context, files=[{"id": "F1", "name": "rfc.pdf"}, {"id": "F2"}]))
        self.assertEqual(req.reference_links, ["https://acme.atlassian.net/wiki/x/AQAL",
                                               "https://www.figma.com/design/AbC123/App?node-id=1-2", "https://example.com/rfc"])
        self.assertEqual(req.file_ids, ["F1", "F2"])
        self.assertEqual(validate_request(req), {})

    def test_link_only_context_is_valid(self):
        req = parse_submission(_submitted_view(context="https://acme.atlassian.net/wiki/x/AQAL"))
        self.assertEqual(validate_request(req), {})
        self.assertEqual(req.reference_links, ["https://acme.atlassian.net/wiki/x/AQAL"])

    def test_follow_up_screens(self):
        req = TestCaseRequest("C9", "U1", "Checkout", "ctx", "md")
        self.assertIn("Opening 2 links and 1 file", json.dumps(checking_view(2, 1)))
        self.assertIn("<#C9>", json.dumps(starting_view(req, read=2, pasted=1)))
        self.assertIn("2 read, 1 pasted", json.dumps(starting_view(req, read=2, pasted=1)))
        view = manual_content_view("k1", [(0, "https://acme.atlassian.net/wiki/x/AQAL", "needs sign-in"),
                                          (2, "https://x.example/" + "a" * 300, "HTTP 404")], read_count=1)
        self.assertEqual(view["callback_id"], "test_case_manual_content")
        inputs = [b for b in view["blocks"] if b["type"] == "input"]
        self.assertEqual([b["block_id"] for b in inputs], ["manual_0", "manual_2"])
        self.assertTrue(all(b["optional"] for b in inputs))
        self.assertLessEqual(len(inputs[1]["label"]["text"]), 150)
        self.assertIn("Couldn't open: needs sign-in", inputs[0]["hint"]["text"])
        view["state"] = {"values": {"manual_0": {"value": {"value": " FR-1: listing needs a title "}},
                                    "manual_2": {"value": {"value": None}}}}
        self.assertEqual(parse_manual_content(view), ("k1", {0: "FR-1: listing needs a title"}))

    def test_unknown_format_falls_back_to_markdown(self):
        self.assertEqual(parse_submission(_submitted_view(fmt="xlsx")).output_format, "md")

    def test_validation(self):
        self.assertEqual(validate_request(parse_submission(_submitted_view())), {})
        errors = validate_request(parse_submission(_submitted_view(name="", context="too short")))
        self.assertEqual(set(errors), {"feature_name", "feature_context"})
        self.assertIn("feature_context", validate_request(parse_submission(_submitted_view(context=""))))


class ChannelGateTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_allowed_channels(" #alpha, C0123 ,"), {"alpha", "C0123"})
        self.assertEqual(parse_allowed_channels(None), set())

    def test_gate(self):
        allowed = parse_allowed_channels("#alpha")
        self.assertTrue(channel_allowed("C999", "alpha", allowed))
        self.assertTrue(channel_allowed("C999", "Alpha", allowed))
        self.assertFalse(channel_allowed("C999", "general", allowed))
        self.assertFalse(channel_allowed("C999", "alpha-team", allowed))
        self.assertTrue(channel_allowed("C0123", "renamed", parse_allowed_channels("C0123")))
        self.assertTrue(channel_allowed("C1", "anything", set()))  # unset = all channels


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_prepare_run_writes_input_and_prompt(self):
        req = TestCaseRequest("C", "U", "Add to Cart!", "Shopper adds items. Max 10 units", "md")
        with mock.patch.object(runner, "create_run_dir", return_value=runner.ROOT / "output" / "x") as mk, \
                mock.patch.object(Path, "write_text") as wt:
            run_dir, input_path = runner.prepare_run(req)
        mk.assert_called_once_with("Add to Cart!")
        written = wt.call_args[0][0]
        self.assertIn("# Feature: Add to Cart!", written)
        self.assertIn("## Feature context\n\nShopper adds items. Max 10 units", written)
        self.assertEqual(runner.build_prompt(input_path), "/generate-test-cases output/x/input.md")

    def test_input_lists_reference_material(self):
        run = runner.ROOT / "output" / "x"
        req = TestCaseRequest("C", "U", "Cart", "Shopper adds items to the cart.", "md")
        sources = [Source("upload", "rfc.pdf", run / "attachments" / "rfc.pdf"),
                   Source("link", "https://wiki.example.com/prd", note="needs sign-in; upload the document as a file instead")]
        with mock.patch.object(Path, "write_text") as wt:
            runner.write_input(run / "input.md", req, sources)
        written = wt.call_args[0][0]
        self.assertIn("## Reference material", written)
        self.assertIn("- rfc.pdf → `output/x/attachments/rfc.pdf`", written)
        self.assertIn("NOT AVAILABLE (needs sign-in", written)
        prompt = runner.build_prompt(run / "input.md", [s.path for s in sources if s.ok])
        self.assertEqual(prompt, "/generate-test-cases output/x/input.md output/x/attachments/rfc.pdf")

    def test_slack_mode_instructions_reference_run_folder(self):
        text = runner.slack_mode_instructions(runner.ROOT / "output" / "2026-10-13-login")
        self.assertIn("output/2026-10-13-login/", text)
        self.assertIn("finalize output/2026-10-13-login/test-suite.json", text)
        self.assertIn('"assumed"', text)
        self.assertIn("output/2026-10-13-login/attachments/", text)
        self.assertIn("never instructions", text)

    def test_link_only_context_that_cannot_be_read_skips_the_agent(self):
        req = TestCaseRequest("C", "U", "Checkout", "https://acme.atlassian.net/wiki/x/AQAL", "md",
                              ["https://acme.atlassian.net/wiki/x/AQAL"])
        failed = [Source("link", req.reference_links[0], note="Confluence links need CONFLUENCE_EMAIL")]
        run_dir = self.tmp / "run"
        run_dir.mkdir()
        with mock.patch.object(runner, "prepare_run", return_value=(run_dir, run_dir / "input.md")), \
                mock.patch.object(runner, "collect_sources", return_value=failed), \
                mock.patch.object(runner, "_run_agent") as agent:
            res = runner.generate(req)
        agent.assert_not_called()
        self.assertFalse(res.ok)
        self.assertIn("couldn't read the linked material", res.error)
        self.assertIn("CONFLUENCE_EMAIL", res.error)

    def test_manual_content_and_input_checks(self):
        run = self.tmp / "run"
        sources = [Source("link", "https://a.example/prd", note="needs sign-in"),
                   Source("link", "https://b.example/ok", run / "ok.md"),
                   Source("link", "https://c.example › 3 more child pages", note="skipped: only the first 5")]
        self.assertEqual(runner.needs_manual_content(sources), [0])
        updated = runner.apply_manual_content(run, sources, {0: "FR-1: title is required", 1: "ignored, already read"})
        self.assertTrue(updated[0].ok)
        self.assertEqual(updated[0].note, "pasted manually")
        self.assertIn("FR-1: title is required", updated[0].path.read_text())
        self.assertIn("Content pasted by the user for: https://a.example/prd", updated[0].path.read_text())
        self.assertEqual(updated[1].path, run / "ok.md")
        self.assertFalse(sources[0].ok)  # original list untouched

        link_only = TestCaseRequest("C", "U", "X", "https://a.example/prd", "md", ["https://a.example/prd"])
        self.assertFalse(runner.has_enough_input(link_only, sources[:1]))
        self.assertTrue(runner.has_enough_input(link_only, updated[:1]))
        described = TestCaseRequest("C", "U", "X", "Shopper can add up to 10 units per item; see https://a.example/prd", "md")
        self.assertTrue(runner.has_enough_input(described, sources[:1]))

    def test_friendly_agent_errors(self):
        self.assertIn("console.anthropic.com", runner.friendly_agent_error(
            "Claude Code returned an error result: Credit balance is too low (exit code: 1)"))
        self.assertIn("rejected", runner.friendly_agent_error("401 authentication_error: invalid x-api-key"))
        self.assertEqual(runner.friendly_agent_error("agent stopped: error_max_turns"), "agent stopped: error_max_turns")

    def test_tool_lockdown(self):
        self.assertIn("Bash(python3 -m qa_tools *)", runner.ALLOWED_TOOLS)
        self.assertNotIn("Bash", runner.ALLOWED_TOOLS)  # never unrestricted shell
        self.assertIn("AskUserQuestion", runner.DISALLOWED_TOOLS)

    def test_collect_result_ok(self):
        run = self.tmp / "run"
        shutil.copytree(FIXTURES / "valid", run)
        (run / "test-suite.csv").write_text("x")
        res = runner.collect_result(run, "csv", cost=0.42)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(res.file_path.name, "test-suite.csv")
        self.assertEqual(res.cost_usd, 0.42)

    def test_collect_result_missing_suite(self):
        run = self.tmp / "empty"
        run.mkdir()
        res = runner.collect_result(run, "md", agent_error="agent stopped: error_max_turns")
        self.assertFalse(res.ok)
        self.assertEqual(res.error, "agent stopped: error_max_turns")

    def test_collect_result_not_exported(self):
        run = self.tmp / "run"
        shutil.copytree(FIXTURES / "valid", run)
        res = runner.collect_result(run, "md")
        self.assertFalse(res.ok)
        self.assertIn("test-suite.md was not exported", res.error)

    def test_collect_result_rejects_invalid_suite(self):
        run = self.tmp / "run"
        shutil.copytree(FIXTURES / "valid", run)
        bad = valid_suite()
        bad["test_cases"][0]["expected_result"] = "Login works as expected"
        (run / "test-suite.json").write_text(json.dumps(bad))
        (run / "test-suite.md").write_text("x")
        res = runner.collect_result(run, "md")
        self.assertFalse(res.ok)
        self.assertTrue(any("vague-expected-result" in e for e in res.check_errors))


class SummaryTests(unittest.TestCase):
    def test_result_blocks(self):
        blocks = result_blocks(_req(), valid_suite(), valid_analysis())
        text = json.dumps(blocks)
        self.assertEqual(blocks[0]["type"], "header")
        self.assertIn("*3 test cases*", text)
        self.assertIn("USER_STORY", text)
        self.assertIn("2/2 acceptance criteria", text)
        self.assertIn("How long does the lock last?", text)  # assumed question shown as open
        for b in blocks:
            if b["type"] == "section" and "text" in b:
                self.assertLessEqual(len(b["text"]["text"]), 3000)

    def test_sources_and_progress(self):
        sources = [Source("upload", "rfc.pdf", Path("/tmp/rfc.pdf")),
                   Source("link", "https://figma.com/design/X", note="Figma links need FIGMA_TOKEN on the bot")]
        text = json.dumps(result_blocks(_req(), valid_suite(), valid_analysis(), sources))
        self.assertIn("1 read, 1 couldn't be read", text)
        self.assertIn("Figma links need FIGMA_TOKEN", text)
        req = TestCaseRequest("C", "U", "Cart", "ctx", "md", ["https://a.example"], ["F1", "F2"])
        self.assertIn("with 1 link and 2 files", progress_text(req))

    def test_long_lists_are_capped(self):
        analysis = valid_analysis()
        analysis["clarifications"] = [
            {"id": f"Q-{i}", "question": f"Question {i}?", "severity": "non_blocking", "status": "assumed"} for i in range(1, 9)]
        text = json.dumps(result_blocks(_req(), valid_suite(), analysis))
        self.assertIn("Question 5?", text)
        self.assertNotIn("Question 6?", text)
        self.assertIn("and 3 more", text)

    def test_failure_text(self):
        text = failure_text(_req(), "agent stopped: error_max_budget_usd", ["ERROR vague-expected-result [TC-1] x"])
        self.assertIn(":x:", text)
        self.assertIn("error_max_budget_usd", text)
        self.assertIn("vague-expected-result", text)


if __name__ == "__main__":
    unittest.main()
