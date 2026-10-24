"""Knowledge base: model, feature matching, version merge rules, search, briefing, sheet parsing and the run flow."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import valid_analysis, valid_suite

from slack_bot.kb import context as C
from slack_bot.kb import flow as F
from slack_bot.kb import merge as M
from slack_bot.kb import store as S
from slack_bot.kb.model import (ACTIVE, NEEDS_REVIEW, OBSOLETE, REVIEWED, Feature, KBTest, KnowledgeBase)
from slack_bot.kb.search import search
from slack_bot.modal import TestCaseRequest
from slack_bot import runner
from slack_bot.sources import Source
from slack_bot.summary import result_blocks

LINKS = ["https://acme.atlassian.net/wiki/spaces/SD/pages/720897/Create+Listing", "https://www.figma.com/design/K1/Flow?node-id=0-1"]


def _v1(kb=None, **kw):
    kb = kb or KnowledgeBase()
    res = M.apply_run(kb, name="Login", keys=["confluence:720897"], links=LINKS, analysis=valid_analysis(),
                      suite=valid_suite(), run_name="run-1", today="2026-10-13", **kw)
    return kb, res


class ModelTests(unittest.TestCase):
    def test_row_round_trip_and_fingerprint(self):
        t = KBTest("F-001", "Login", "TC-LOGIN-001", title="Log in", steps="1. Open\n2. Click", priority="P0")
        again = KBTest.from_row(dict(zip(KBTest.COLUMNS, t.to_row())))
        self.assertEqual(again, t)
        self.assertEqual(t.fingerprint(), KBTest("F-001", "Login", "TC-LOGIN-001", title=" Log  in ", steps="1. Open\n2. Click", priority="P0").fingerprint())
        f = Feature("F-002", "Cart", ["figma:K1"], ["https://x"], 3, "2026-10-13", 5, "https://s")
        self.assertEqual(Feature.from_row(dict(zip(Feature.COLUMNS, f.to_row()))), f)

    def test_human_edits_become_reviewed(self):
        kb, _ = _v1()
        kb.stamp()
        self.assertEqual(kb.mark_human_edits(), [])
        kb.tests[0].expected = "Edited by QA"
        self.assertEqual(kb.mark_human_edits(), ["TC-LOGIN-001"])
        self.assertEqual(kb.tests[0].origin, REVIEWED)
        self.assertEqual(kb.next_feature_id(), "F-002")


class MatchTests(unittest.TestCase):
    def test_keys(self):
        self.assertEqual(M.link_key("https://acme.atlassian.net/wiki/spaces/SD/pages/720897/Title"), "confluence:720897")
        self.assertEqual(M.link_key("https://www.figma.com/design/K1/App?node-id=1-2"), "figma:K1")
        self.assertEqual(M.link_key("https://docs.google.com/document/d/AbC_1/edit"), "gdoc:AbC_1")
        self.assertEqual(M.link_key("https://Example.com/specs/prd/"), "url:example.com/specs/prd")
        srcs = [Source("link", "x", Path("/a/confluence-753666-PRD.md")), Source("link", "y", note="failed")]
        self.assertEqual(M.source_keys(["https://acme.atlassian.net/wiki/x/AQAL"], srcs),
                         ["url:acme.atlassian.net/wiki/x/AQAL", "confluence:753666"])

    def test_find_feature_prefers_shared_sources_then_name(self):
        kb = KnowledgeBase(features=[Feature("F-001", "Login", ["confluence:1"]), Feature("F-002", "Checkout", ["figma:K1", "confluence:2"])])
        self.assertEqual(M.find_feature(kb, ["confluence:2"], "Something else").feature_id, "F-002")
        self.assertEqual(M.find_feature(kb, [], "  login!! ").feature_id, "F-001")
        self.assertIsNone(M.find_feature(kb, ["confluence:9"], "New"))


class MergeTests(unittest.TestCase):
    def test_first_version(self):
        kb, res = _v1()
        self.assertTrue(res.is_new_feature)
        self.assertEqual((res.version, len(res.added)), (1, 3))
        self.assertEqual(res.summary(), "v1 (new feature): 3 test cases added")
        self.assertEqual({t.added_in for t in kb.tests}, {"v1"})
        self.assertEqual(kb.features[0].active_tests, 3)
        self.assertEqual(len(kb.requirements), 4)
        self.assertEqual(kb.changelog[0].added, 3)

    def _v2(self, kb, analysis, suite):
        return M.apply_run(kb, name="Login renamed", keys=["confluence:720897"], links=LINKS, analysis=analysis, suite=suite,
                           run_name="run-2", feature=kb.features[0], today="2026-10-14")

    def test_second_version_reuse_update_add_and_retire(self):
        kb, _ = _v1()
        analysis, suite = valid_analysis(), valid_suite()
        analysis["acceptance_criteria"][1]["text"] = "Invalid credentials show 'Wrong email or password'"   # AC-1.2 changed
        analysis["business_rules"] = []                                                                  # BR-1 removed
        suite["test_cases"] = suite["test_cases"][:2]                                                    # drop BR-1 test
        suite["test_cases"][1]["expected_result"] = "Error 'Wrong email or password' is displayed"       # updated
        new = copy.deepcopy(suite["test_cases"][0])
        new.update(id="TC-LOGIN-004", scenario="Log in with uppercase email", source_refs=["AC-1.1"])
        suite["test_cases"].append(new)                                                                  # added
        res = self._v2(kb, analysis, suite)
        self.assertEqual((res.unchanged, res.updated, res.added, res.obsolete), (["TC-LOGIN-001"], ["TC-LOGIN-002"], ["TC-LOGIN-004"], ["TC-LOGIN-003"]))
        self.assertEqual(res.requirement_changes, {"new": [], "changed": ["AC-1.2"], "removed": ["BR-1"]})
        self.assertEqual(kb.features[0].name, "Login")  # existing name kept
        t3 = next(t for t in kb.tests if t.test_id == "TC-LOGIN-003")
        self.assertEqual((t3.status, t3.changed_in), (OBSOLETE, "v2"))
        t2 = next(t for t in kb.tests if t.test_id == "TC-LOGIN-002")
        self.assertEqual((t2.added_in, t2.changed_in), ("v1", "v2"))
        self.assertEqual(kb.features[0].active_tests, 3)
        self.assertIn("removed: BR-1", kb.changelog[-1].requirement_changes)
        self.assertIn("v2: 1 unchanged · 1 updated · 1 added · 1 obsolete", res.summary())

    def test_change_map_for_the_fresh_sheet(self):
        kb, res = _v1()
        self.assertEqual(set(res.changes().values()), {"New"})
        suite = valid_suite()
        suite["test_cases"][1]["expected_result"] = "Error 'Wrong email or password' is displayed"
        suite["test_cases"] = suite["test_cases"][:2]
        res2 = self._v2(kb, valid_analysis(), suite)
        self.assertEqual(res2.changes(), {"TC-LOGIN-001": "Unchanged", "TC-LOGIN-002": "Updated", "TC-LOGIN-003": "Unchanged"})

    def test_dropped_test_with_existing_requirement_is_kept(self):
        kb, _ = _v1()
        suite = valid_suite()
        suite["test_cases"] = suite["test_cases"][:1]
        res = self._v2(kb, valid_analysis(), suite)
        self.assertEqual(sorted(res.kept), ["TC-LOGIN-002", "TC-LOGIN-003"])
        self.assertEqual(kb.features[0].active_tests, 3)

    def test_reviewed_tests_are_flagged_not_overwritten(self):
        kb, _ = _v1()
        reviewed = next(t for t in kb.tests if t.test_id == "TC-LOGIN-002")
        reviewed.origin, reviewed.expected = REVIEWED, "QA wording"
        analysis = valid_analysis()
        analysis["acceptance_criteria"][1]["text"] = "Changed criterion text"
        res = self._v2(kb, analysis, valid_suite())
        self.assertEqual(res.needs_review, ["TC-LOGIN-002"])
        self.assertEqual((reviewed.status, reviewed.expected), (NEEDS_REVIEW, "QA wording"))
        self.assertIn("AC-1.2 changed in v2", reviewed.review_note)
        self.assertIn("Expected: Error 'Invalid email or password' is displayed", reviewed.suggested_update)

    def test_person_retired_test_stays_obsolete(self):
        kb, _ = _v1()
        t = kb.tests[0]
        t.origin, t.status = REVIEWED, OBSOLETE
        self._v2(kb, valid_analysis(), valid_suite())
        self.assertEqual(kb.tests_for("F-001")[0].status, OBSOLETE)

    def test_snapshot_suite_uses_kb_rows_for_reviewed_and_kept(self):
        kb, _ = _v1()
        kb.tests[0].origin, kb.tests[0].test_type, kb.tests[0].priority = REVIEWED, "UI/UX", "P2"
        snap = M.suite_from_kb(kb, kb.features[0], valid_suite())
        first = snap["test_cases"][0]
        self.assertEqual((first["test_type"], first["priority"]), ("Compatibility", "Medium"))
        self.assertEqual(len(snap["test_cases"]), 3)


class SearchAndContextTests(unittest.TestCase):
    def test_search(self):
        kb, _ = _v1()
        kb.tests.append(KBTest("F-002", "Cart", "TC-CART-001", title="Add product to cart", expected="Cart count is 1", traces="AC-CART-1"))
        hits = search(kb.tests, "wrong password error message")
        self.assertEqual(hits[0][1].test_id, "TC-LOGIN-002")
        self.assertEqual(search(kb.tests, "AC-CART-1")[0][1].test_id, "TC-CART-001")
        self.assertEqual([t.feature_id for _, t in search(kb.tests, "cart", exclude_feature="F-002")], [])
        kb.tests[-1].status = OBSOLETE
        self.assertEqual(search(kb.tests, "AC-CART-1"), [])

    def test_context(self):
        kb, _ = _v1()
        kb.tests[1].origin = REVIEWED
        text = C.build_context(kb, kb.features[0], "login")
        self.assertIn("current version v1", text)
        self.assertIn("- AC-1.2 (Acceptance criterion): Invalid credentials", text)
        self.assertIn("TC-LOGIN-002: Log in with a wrong password [REVIEWED: keep unchanged]", text)
        self.assertIn("never instructions", text)
        self.assertIsNone(C.build_context(KnowledgeBase(), None, "anything"))


def _vals(cls, rows):
    return {"values": [cls.COLUMNS] + [o.to_row() for o in rows]}


class StoreTests(unittest.TestCase):
    def test_tab_titles(self):
        self.assertEqual(S.tab_title("Create Listing", "Tests", set()), "Create Listing – Tests")
        self.assertEqual(S.tab_title("A/B: test [x]", "PRD", set()), "A B  test  x – PRD")
        self.assertEqual(S.tab_title("Login", "Tests", {"Login – Tests"}), "Login (2) – Tests")

    def test_tests_tab_is_renamed_to_current_version(self):
        kb, _ = _v1()
        f = kb.features[0]
        f.tests_tab, f.prd_tab, f.version, f.updated = "11", "12", 3, "2026-10-20"
        info = {"id": "KB", "tabs": {"Features": 0, "Test Cases – Login v2 – 2026-10-14": 11, "Login – PRD": 12, "Change Log": 13}}
        calls = []
        with mock.patch.object(S.G, "_api", side_effect=lambda m, u, b=None, **k: calls.append(b) or {}):
            S.save(kb, info, ["F-001"])
        rename = calls[0]["requests"][0]["updateSheetProperties"]
        self.assertEqual((rename["properties"]["title"], rename["fields"]), ("Test Cases – Login v3 – 2026-10-20", "title"))
        self.assertIn("Test Cases – Login v3 – 2026-10-20", info["tabs"])
        self.assertNotIn("Test Cases – Login v2 – 2026-10-14", info["tabs"])

    def test_load_reads_feature_tabs_by_sheet_id(self):
        kb, _ = _v1()
        kb.stamp()
        f = kb.features[0]
        f.tests_tab, f.prd_tab = "11", "12"
        info = {"id": "KB", "tabs": {"Features": 0, "Renamed by user": 11, "Login – PRD": 12, "Change Log": 13}}
        tc_rows = [list(reversed(KBTest.COLUMNS))] + [list(reversed(t.to_row())) for t in kb.tests]  # columns reordered
        manual = dict.fromkeys(KBTest.COLUMNS, "")
        manual.update({"Test title": "QA-added edge case", "Status": "weird"})
        tc_rows.append(list(reversed([manual[c] for c in KBTest.COLUMNS])))
        calls = []

        def batch_get(sid, tabs):
            calls.append(tabs)
            if tabs == ["Features", "Change Log"]:
                return [_vals(Feature, kb.features), _vals(S.ChangeEntry, kb.changelog)]
            return [{"values": tc_rows}, _vals(S.KBRequirement, kb.requirements)]

        with mock.patch.object(S, "_batch_get", side_effect=batch_get):
            loaded, info, edited = S.load(info)
        self.assertEqual(calls[1], ["Renamed by user", "Login – PRD"])  # found by sheetId, not title
        self.assertEqual((len(loaded.tests), len(loaded.requirements), len(loaded.changelog)), (4, 4, 1))
        self.assertTrue(all(t.feature_id == "F-001" for t in loaded.tests))
        self.assertEqual((loaded.tests[-1].test_id, loaded.tests[-1].status), ("TC-MANUAL-001", ACTIVE))
        self.assertEqual(edited, ["TC-MANUAL-001"])
        self.assertEqual(info["migrate"], [])

    def test_load_reads_old_per_feature_spreadsheet_for_migration(self):
        kb, _ = _v1()
        kb.stamp()
        kb.features[0].sheet_id = "OLDFILE"
        info = {"id": "KB", "tabs": {"Features": 0}}

        def batch_get(sid, tabs):
            if sid == "KB":
                return [_vals(Feature, kb.features)]
            self.assertEqual((sid, tabs), ("OLDFILE", ["Test Cases", "Requirements", "Change Log"]))
            return [_vals(KBTest, kb.tests), _vals(S.KBRequirement, kb.requirements), _vals(S.ChangeEntry, kb.changelog)]

        with mock.patch.object(S, "_batch_get", side_effect=batch_get):
            loaded, info, edited = S.load(info)
        self.assertEqual((len(loaded.tests), len(loaded.changelog), edited, info["migrate"]), (3, 1, [], ["F-001"]))

    def test_save_creates_tabs_writes_and_trashes_old_file(self):
        kb, _ = _v1()
        kb.features[0].sheet_id = "OLDFILE"
        info = {"id": "KB", "tabs": {"Features": 0}, "migrate": ["F-001"]}
        calls = []

        def api(method, url, body=None, **kw):
            calls.append((method, url, body))
            if url.endswith(":batchUpdate") and body and "addSheet" in json.dumps(body):
                return {"replies": [{"addSheet": {"properties": {"sheetId": 100 + i}}} for i, _ in enumerate(body["requests"])]}
            return {}

        with mock.patch.object(S.G, "_api", side_effect=api):
            S.save(kb, info, ["F-001"])
        f = kb.features[0]
        self.assertEqual((f.tests_tab, f.prd_tab), ("100", "101"))
        self.assertEqual(info["tabs"]["Test Cases – Login v1 – 2026-10-13"], 100)
        self.assertEqual(info["tabs"]["Change Log"], 102)
        self.assertEqual(f.tests_url, "https://docs.google.com/spreadsheets/d/KB/edit#gid=100")
        written = next(b for m, u, b in calls if u.endswith("/values:batchUpdate") and len(b["data"]) == 4)
        self.assertEqual([d["range"] for d in written["data"]],
                         ["'Features'!A1", "'Change Log'!A1", "'Test Cases – Login v1 – 2026-10-13'!A1", "'Login – PRD'!A1"])
        self.assertEqual(len(written["data"][2]["values"]), 4)  # header + 3 tests
        order = [r["updateSheetProperties"]["properties"] for b in [c[2] for c in calls if c[2]] for r in b.get("requests", [])
                 if "updateSheetProperties" in r and r["updateSheetProperties"]["fields"] == "index,hidden"]
        self.assertEqual([(o["sheetId"], o["hidden"]) for o in order], [(100, False), (0, True), (101, True), (102, True)])
        self.assertIn(("PATCH", f"{S.G.DRIVE_FILES}/OLDFILE", {"trashed": True}), calls)
        self.assertEqual((f.sheet_id, info["migrate"]), ("", []))
        self.assertTrue(all(t.sync == t.fingerprint() for t in kb.tests))

    def test_format_requests(self):
        reqs = S.format_requests(5, KBTest)
        dropdowns = [r["setDataValidation"] for r in reqs if "setDataValidation" in r]
        self.assertEqual(len(dropdowns), 3)
        status = next(d for d in dropdowns if d["range"]["startColumnIndex"] == KBTest.COLUMNS.index("Status"))
        self.assertEqual([v["userEnteredValue"] for v in status["rule"]["condition"]["values"]], [ACTIVE, NEEDS_REVIEW, OBSOLETE])
        feats = S.format_requests(0, Feature)
        hidden = [r["updateDimensionProperties"]["range"]["startIndex"] for r in feats
                  if "updateDimensionProperties" in r and r["updateDimensionProperties"]["properties"].get("hiddenByUser")]
        self.assertEqual(hidden, [Feature.COLUMNS.index(c) for c in ("Source keys", "Tab IDs", "Sheet ID")])
        self.assertFalse(any("setDataValidation" in r for r in feats))


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "attachments").mkdir()
        (self.tmp / "attachments" / "confluence-720897-PRD.md").write_text("Users log in with email and password.")

    def test_prepare_adds_briefing_for_known_feature(self):
        kb, _ = _v1()
        sources = [Source("link", LINKS[0], self.tmp / "attachments" / "confluence-720897-PRD.md")]
        with mock.patch.object(F.store, "load", return_value=(kb, {}, [])):
            session, new_sources = F.prepare("Login v2", "see PRD", LINKS[:1], sources, self.tmp)
        self.assertEqual((session.feature_id, session.version), ("F-001", 1))
        self.assertEqual(new_sources[-1].kind, "kb")
        self.assertIn("Knowledge base: Login v1", new_sources[-1].label)
        self.assertTrue((self.tmp / "attachments" / "kb-context.md").exists())

    def test_record_saves_version_and_snapshot(self):
        kb, _ = _v1()
        session = F.KBSession("F-001", "Login", 1, ["confluence:720897"], LINKS)
        kb.features[0].tests_url = "https://feature-tests-tab"
        info = {"id": "KB1", "url": "u", "tabs": {"Features": 9}}
        with mock.patch.object(F.store, "load", return_value=(kb, info, [])), \
                mock.patch.object(F.store, "save") as save, \
                mock.patch.object(F.G, "create_test_case_sheet", return_value="https://snap") as snap:
            rec = F.record(session, "Login", valid_analysis(), valid_suite(), self.tmp, [])
        self.assertEqual(rec.result.version, 2)
        self.assertEqual(rec.snapshot_url, "https://snap")
        self.assertEqual(rec.kb_url, "https://feature-tests-tab")
        self.assertEqual(rec.index_url, "https://docs.google.com/spreadsheets/d/KB1/edit#gid=9")
        self.assertEqual(kb.changelog[-1].snapshot, "https://snap")
        self.assertIn("Login v2", snap.call_args.args[2])
        self.assertEqual(snap.call_args.kwargs["changes"], {"TC-LOGIN-001": "Unchanged", "TC-LOGIN-002": "Unchanged", "TC-LOGIN-003": "Unchanged"})
        save.assert_called_once()
        self.assertEqual(save.call_args.args[2], ["F-001"])

    def test_reply_and_input_checks(self):
        kb, res = _v1()
        rec = F.KBRecord(res, "https://kb", "https://snap", "https://index")
        req = TestCaseRequest("C", "U", "Login", "ctx", "gsheet")
        text = json.dumps(result_blocks(req, valid_suite(), valid_analysis(), kb_record=rec), ensure_ascii=False)
        self.assertIn("Open the test cases (Google Sheet)", text)
        self.assertIn("https://snap", text)
        self.assertIn("Saved to the knowledge base as *Login v1 (new feature)", text)
        self.assertNotIn("https://kb", text)        # the knowledge base is never linked
        self.assertNotIn("https://index", text)
        self.assertNotIn("attached in the thread", text)
        kb_only = [Source("kb", "Knowledge base", self.tmp / "x.md")]
        link_only = TestCaseRequest("C", "U", "X", "https://a.example/prd", "md", ["https://a.example/prd"])
        self.assertFalse(runner.has_enough_input(link_only, kb_only))


if __name__ == "__main__":
    unittest.main()
