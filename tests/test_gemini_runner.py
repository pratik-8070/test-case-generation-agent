"""Gemini provider (Interactions REST API): draft -> qa_tools checks -> fix rounds -> export, with HTTP faked."""

import json
import shutil
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import ROOT, valid_analysis, valid_suite

from slack_bot import gemini_runner as G
from slack_bot import net, runner
from slack_bot.modal import TestCaseRequest
from slack_bot.sources import Source


def _reply(payload, status="completed", rid="int-1"):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return {"id": rid, "status": status, "usage": {"total_input_tokens": 10, "total_output_tokens": 5},
            "steps": [{"type": "thought", "signature": "x"}, {"type": "model_output", "content": [{"type": "text", "text": text}]}]}


def _payload(suite=None):
    return {"input_analysis": valid_analysis(), "test_suite": suite or valid_suite()}


class GeminiRunnerTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "output").mkdir(exist_ok=True)
        self.run_dir = Path(tempfile.mkdtemp(prefix="gemini-test-", dir=ROOT / "output"))
        self.addCleanup(shutil.rmtree, self.run_dir)
        self.input_path = self.run_dir / "input.md"
        self.input_path.write_text("# Feature: Login\n\n## Feature context\n\nUser logs in.\n")
        self.post = mock.patch.object(G, "_post").start()
        mock.patch.object(G.time, "sleep").start()
        mock.patch.object(G, "prefer_ipv4").start()
        self.addCleanup(mock.patch.stopall)

    def _run(self, sources=(), model="gemini-main"):
        return G.generate_suite(self.run_dir, self.input_path, list(sources), model, "key", ("gemini-lite",))

    def _bodies(self):
        return [c.args[0] for c in self.post.call_args_list]

    def test_first_draft_passes_and_is_exported(self):
        self.post.return_value = _reply(_payload())
        self.assertEqual(self._run(), "")
        for name in ("input-analysis.json", "test-suite.json", "test-suite.md", "test-suite.csv"):
            self.assertTrue((self.run_dir / name).exists(), name)
        saved = json.loads((self.run_dir / "test-suite.json").read_text())
        self.assertEqual(saved["coverage_summary"]["computed"]["total_test_cases"], 3)
        body = self._bodies()[0]
        self.assertEqual(body["model"], "gemini-main")
        self.assertEqual(body["response_format"], {"type": "text", "mime_type": "application/json"})
        self.assertIn("test-suite.schema.json", body["system_instruction"])
        self.assertIn(self.run_dir.name, body["system_instruction"])
        self.assertEqual(body["input"][0]["type"], "user_input")

    def test_check_errors_are_sent_back_in_the_same_conversation(self):
        bad = valid_suite()
        bad["test_cases"][0]["expected_result"] = "Login works as expected for the user"
        self.post.side_effect = [_reply(_payload(bad), rid="int-1"), _reply(_payload(), rid="int-2")]
        self.assertEqual(self._run(), "")
        follow = self._bodies()[1]
        self.assertEqual(follow["previous_interaction_id"], "int-1")
        self.assertEqual(follow["model"], "gemini-main")
        self.assertIn("vague-expected-result", follow["input"][0]["content"][0]["text"])

    def test_fenced_json_is_accepted_and_bad_json_retried(self):
        fenced = "```json\n" + json.dumps(_payload()) + "\n```"
        self.post.side_effect = [_reply("Here you go!"), _reply(fenced)]
        self.assertEqual(self._run(), "")
        self.assertIn("not a JSON object", self._bodies()[1]["input"][0]["content"][0]["text"])

    def test_incomplete_reply_asks_for_concise_output(self):
        self.post.side_effect = [_reply('{"input_analysis": {', status="incomplete"), _reply(_payload())]
        self.assertEqual(self._run(), "")
        self.assertIn("cut off", self._bodies()[1]["input"][0]["content"][0]["text"])

    def test_quality_gaps_requested_then_accepted_when_rounds_run_out(self):
        self.input_path.write_text("# Feature: Login\n\nFR-7: the user can log in. FR-8: lockout after 5 failures.\n")
        self.post.return_value = _reply(_payload())  # valid but keeps US-1 ids, thin, no FR-7/FR-8
        self.assertEqual(self._run(), "")
        self.assertEqual(self.post.call_count, 4)  # draft + 3 improvement requests, then accepted
        msg = self._bodies()[1]["input"][0]["content"][0]["text"]
        self.assertIn("quality bar", msg)
        self.assertIn("FR-7, FR-8", msg)
        self.assertTrue((self.run_dir / "test-suite.md").exists())

    def test_quality_problems(self):
        analysis, suite = valid_analysis(), valid_suite()
        self.assertEqual(G.quality_problems(analysis, suite, {"US-1", "AC-1.1"}, []), [])  # ids kept, 3 tests for 1 req
        problems = G.quality_problems(analysis, suite, {"FR-2", "FR-10"}, ["figma-01.png"])
        self.assertIn("FR-2, FR-10", problems[0])
        self.assertIn("figma-01.png", problems[1])
        analysis["requirements"].append({"id": "US-2", "feature": "LOGIN", "text": "x", "source_ref": "s", "origin": "stated"})
        self.assertTrue(any("thin" in p for p in G.quality_problems(analysis, suite, set(), [])))

    def test_source_ids_are_found_in_text_inputs_only(self):
        att = self.run_dir / "attachments"
        att.mkdir()
        (att / "prd.md").write_text("FR-1 Choose type. FR-1.2 sub. AC-3 shown. Not an id: FR-x, PREFR-9")
        (att / "screen.png").write_bytes(b"FR-99")
        self.input_path.write_text("see BR-4")
        ids = G.source_ids(self.input_path, [Source("link", "p", att / "prd.md"), Source("link", "s", att / "screen.png")])
        self.assertEqual(ids, {"FR-1", "FR-1.2", "AC-3", "BR-4"})

    def test_gives_up_after_fix_rounds(self):
        bad = valid_suite()
        bad["test_cases"][1]["id"] = "TC-LOGIN-001"
        self.post.return_value = _reply(_payload(bad))
        self.assertIn("failed checks after 3 fix rounds", self._run())
        self.assertEqual(self.post.call_count, 4)
        self.assertFalse((self.run_dir / "test-suite.md").exists())

    def test_busy_model_is_retried_then_falls_back(self):
        busy = G.GeminiError(503, "service_unavailable", "high demand")
        self.post.side_effect = [busy, busy, busy, _reply(_payload())]  # main: 1 + 2 retries, then fallback
        self.assertEqual(self._run(), "")
        self.assertEqual([b["model"] for b in self._bodies()], ["gemini-main"] * 3 + ["gemini-lite"])

    def test_quota_falls_back_and_reports_when_all_exhausted(self):
        quota = G.GeminiError(429, "too_many_requests", "Your project has exceeded a quota.")
        self.post.side_effect = [quota, _reply(_payload())]
        self.assertEqual(self._run(), "")
        self.post.reset_mock()
        self.post.side_effect = [quota, quota]
        error = self._run()
        self.assertIn("free-tier quota used up for gemini-main, gemini-lite", error)

    def test_timeout_falls_back_to_next_model(self):
        timeout = G.GeminiError(0, "network", "The read operation timed out")
        self.post.side_effect = [timeout, _reply(_payload())]
        self.assertEqual(self._run(), "")
        self.assertEqual([b["model"] for b in self._bodies()], ["gemini-main", "gemini-lite"])
        self.post.reset_mock()
        self.post.side_effect = [timeout, timeout]
        self.assertIn("Gemini didn't respond (gemini-main, gemini-lite", self._run())

    def test_rejected_key_does_not_try_other_models(self):
        self.post.side_effect = [G.GeminiError(403, "permission_denied", "API key not valid")]
        self.assertIn("GEMINI_API_KEY was rejected", self._run())
        self.assertEqual(self.post.call_count, 1)

    def test_input_content_includes_text_images_and_pdfs(self):
        att = self.run_dir / "attachments"
        att.mkdir()
        (att / "confluence-1-PRD.md").write_text("FR-1: Title is required")
        (att / "figma-01.png").write_bytes(b"\x89PNG fake")
        (att / "rfc.pdf").write_bytes(b"%PDF-1.7")
        sources = [Source("link", "https://c", att / "confluence-1-PRD.md"), Source("link", "https://f", att / "figma-01.png"),
                   Source("upload", "rfc.pdf", att / "rfc.pdf"), Source("link", "https://x", note="needs sign-in")]
        content = G.build_input_content(self.input_path, sources)
        self.assertTrue(any("FR-1: Title is required" in c.get("text", "") for c in content))
        self.assertTrue(any(c["type"] == "image" and c["mime_type"] == "image/png" for c in content))
        self.assertTrue(any(c["type"] == "document" and c["mime_type"] == "application/pdf" for c in content))
        self.assertFalse(any("https://x" in c.get("text", "") for c in content))

    def test_output_text_skips_thoughts(self):
        self.assertEqual(G.output_text(_reply("{}")), "{}")
        self.assertEqual(G.output_text({"steps": [{"type": "thought"}]}), "")


class ErrorParsingTests(unittest.TestCase):
    def _http_error(self, code, body: bytes):
        import io
        import urllib.error
        return urllib.error.HTTPError("u", code, "Reason", {}, io.BytesIO(body))

    def test_error_body_shapes(self):
        cases = [
            (b'{"error": {"code": "too_many_requests", "message": "quota"}}', ("too_many_requests", "quota")),
            (b'[{"error": {"code": 401, "message": "API key expired", "status": "UNAUTHENTICATED"}}]', ("401", "API key expired")),
            (b'"plain string"', ("", "plain string")),
            (b"not json", ("", "Reason")),
            (b"[]", ("", "Reason")),
        ]
        for body, expected in cases:
            self.assertEqual(G._error_fields(self._http_error(401, body)), expected, body)

    def test_post_raises_gemini_error_for_list_bodies(self):
        err = self._http_error(401, b'[{"error": {"code": 401, "message": "API key not valid"}}]')
        with mock.patch.object(G.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(G.GeminiError) as ctx:
                G._post({"model": "m"}, "k")
        self.assertEqual(ctx.exception.status, 401)
        self.assertIn("GEMINI_API_KEY was rejected", G._friendly(ctx.exception, ["m"]))


class NetTests(unittest.TestCase):
    def test_ipv4_sorted_first(self):
        infos = [(socket.AF_INET6, 1, 6, "", ("2001::1", 443, 0, 0)), (socket.AF_INET, 1, 6, "", ("1.2.3.4", 443))]
        with mock.patch.object(net, "_original_getaddrinfo", return_value=infos):
            self.assertEqual(net._ipv4_first("h", 443)[0][0], socket.AF_INET)


class ProviderSwitchTests(unittest.TestCase):
    def test_settings_from_env(self):
        env = {"LLM_PROVIDER": "Gemini", "GEMINI_API_KEY": "k", "GEMINI_FALLBACK_MODELS": "a, b"}
        with mock.patch.dict("os.environ", env, clear=False):
            s = runner.AgentSettings.from_env()
        self.assertEqual((s.provider, s.gemini_api_key, s.gemini_fallback_models), ("gemini", "k", ("a", "b")))
        self.assertIn("free tier", s.describe())
        with mock.patch.dict("os.environ", {"LLM_PROVIDER": "nonsense"}, clear=False):
            self.assertEqual(runner.AgentSettings.from_env().provider, "claude")

    def test_gemini_without_key_fails_fast(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        req = TestCaseRequest("C", "U", "Login", "A registered user logs in with email and password; 5 failures lock it.", "md")
        res = runner.run_generation(req, tmp, tmp / "input.md", [], runner.AgentSettings(provider="gemini"))
        self.assertFalse(res.ok)
        self.assertIn("GEMINI_API_KEY is not set", res.error)


if __name__ == "__main__":
    unittest.main()
