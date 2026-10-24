"""Google Sheet export: mapping, rows, formatting requests, OAuth refresh, and the publish flow (Google faked)."""

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from helpers import valid_analysis, valid_suite

from slack_bot import google_sheets as G
from slack_bot.modal import TestCaseRequest, build_modal
from slack_bot.summary import result_blocks


class MappingTests(unittest.TestCase):
    def test_types_and_priorities(self):
        self.assertEqual(G.doc_test_type({"test_type": "Error Handling"}), "Negative")
        self.assertEqual(G.doc_test_type({"test_type": "Compatibility"}), "UI/UX")
        self.assertEqual(G.doc_test_type({"test_type": "Authorization"}), "Security")
        self.assertEqual(G.doc_test_type({"test_type": "Positive", "steps": ["Send `POST /orders` with body"]}), "API")
        self.assertEqual(G.doc_test_type({"test_type": "Validation", "steps": ["Send POST /orders"]}), "Validation")
        self.assertTrue(set(G._TYPE_MAP.values()) <= set(G.TYPE_OPTIONS))
        self.assertEqual([G.doc_priority({"priority": p}) for p in ("Critical", "High", "Medium", "Low")], ["P0", "P1", "P2", "P3"])

    def test_description_fallback(self):
        self.assertEqual(G.test_description({"description": "Checks X.", "scenario": "s"}), "Checks X.")
        self.assertIn("Covers AC1", G.test_description({"scenario": "Log in", "source_refs": ["AC1"]}))


class RowTests(unittest.TestCase):
    def test_one_row_per_test_case(self):
        rows = G.test_case_rows(valid_suite())
        self.assertEqual(rows[0], G.COLUMNS)
        self.assertEqual(len(rows), 4)
        first = dict(zip(G.COLUMNS, rows[1]))
        self.assertEqual(first["Test ID"], "TC-LOGIN-001")
        self.assertEqual((first["Test type"], first["Priority"]), ("Positive", "P0"))
        self.assertTrue(first["Test steps"].startswith("1. Open the login page\n2. "))
        self.assertTrue(first["Preconditions"].startswith("• "))
        self.assertIn("email: user@example.com", first["Test data"])
        self.assertEqual(first["Traces to"], "AC-1.1")
        self.assertEqual(dict(zip(G.COLUMNS, rows[3]))["Priority"], "P1")

    def test_change_column(self):
        rows = G.test_case_rows(valid_suite(), {"TC-LOGIN-001": "New", "TC-LOGIN-002": "Updated"})
        self.assertEqual(rows[0][:3], ["Test ID", "Change", "Test title"])
        self.assertEqual([r[1] for r in rows[1:]], ["New", "Updated", "Unchanged"])
        reqs = G.format_requests(1, 2, len(rows), rows[0])
        prio = next(r["setDataValidation"] for r in reqs if "setDataValidation" in r
                    and r["setDataValidation"]["rule"]["condition"]["values"][0]["userEnteredValue"] == "P0")
        self.assertEqual(prio["range"]["startColumnIndex"], rows[0].index("Priority"))
        self.assertEqual(sum("addConditionalFormatRule" in r for r in reqs), 4 + len(G.CHANGE_COLORS))
        self.assertEqual(sum(1 for r in reqs if "updateDimensionProperties" in r
                             and r["updateDimensionProperties"]["range"]["sheetId"] == 1), len(rows[0]))

    def test_summary(self):
        rows = G.summary_rows(valid_suite(), valid_analysis(), "Login")
        flat = {r[0]: r[1] for r in rows if len(r) == 2 and r[0]}
        self.assertEqual(flat["Total test cases"], "3")
        self.assertEqual(flat["Acceptance criteria covered"], "2/2")
        self.assertIn(["", "How long does the lock last?"], rows)

    def test_format_requests(self):
        reqs = G.format_requests(sheet_id=11, summary_id=22, n_rows=4)
        validations = [r["setDataValidation"] for r in reqs if "setDataValidation" in r]
        self.assertEqual(len(validations), 2)
        by_col = {v["range"]["startColumnIndex"]: v for v in validations}
        prio = by_col[G.PRIORITY_COL]
        self.assertEqual(prio["rule"]["condition"]["type"], "ONE_OF_LIST")
        self.assertEqual([x["userEnteredValue"] for x in prio["rule"]["condition"]["values"]], ["P0", "P1", "P2", "P3"])
        self.assertTrue(prio["rule"]["strict"] and prio["rule"]["showCustomUi"])
        self.assertEqual((prio["range"]["startRowIndex"], prio["range"]["endRowIndex"]), (1, 4))  # header excluded
        self.assertEqual(len(by_col[G.TYPE_COL]["rule"]["condition"]["values"]), len(G.TYPE_OPTIONS))
        self.assertEqual(sum("addConditionalFormatRule" in r for r in reqs), 4)
        self.assertTrue(any("setBasicFilter" in r for r in reqs))
        widths = [r for r in reqs if "updateDimensionProperties" in r and r["updateDimensionProperties"]["range"]["sheetId"] == 11]
        self.assertEqual(len(widths), len(G.COLUMNS))


class AuthAndPublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        secret = self.tmp / "client.json"
        secret.write_text(json.dumps({"installed": {"client_id": "cid", "client_secret": "cs", "token_uri": "https://t"}}))
        mock.patch.object(G, "CLIENT_SECRET_FILE", secret).start()
        mock.patch.object(G, "TOKEN_FILE", self.tmp / "token.json").start()
        self.addCleanup(mock.patch.stopall)

    def test_not_connected(self):
        self.assertFalse(G.is_configured())
        with self.assertRaises(G.GoogleSheetsError) as ctx:
            G.access_token()
        self.assertIn("google_sheets auth", str(ctx.exception))

    def test_refresh_and_cache(self):
        G._save_token({"refresh_token": "r1"})
        with mock.patch.object(G, "_post_form", return_value={"access_token": "a1", "expires_in": 3600}) as post:
            self.assertEqual(G.access_token(), "a1")
            self.assertEqual(G.access_token(), "a1")
        post.assert_called_once()
        self.assertEqual(oct((self.tmp / "token.json").stat().st_mode & 0o777), "0o600")

    def test_revoked_token_message(self):
        G._save_token({"refresh_token": "r1", "access_token": "old", "expires_at": time.time() - 10})
        with mock.patch.object(G, "_post_form", side_effect=G.GoogleSheetsError("invalid_grant: Token has been revoked")):
            with self.assertRaises(G.GoogleSheetsError) as ctx:
                G.access_token()
        self.assertIn("expired or was revoked", str(ctx.exception))

    def test_publish(self):
        G._save_token({"refresh_token": "r"})
        calls = []

        def api(method, url, body=None, raw=None, content_type="application/json"):
            calls.append((method, url, body))
            if method == "POST" and url == G.SHEETS_API:
                self.assertEqual(body["sheets"][0]["properties"]["gridProperties"]["frozenRowCount"], 1)
                return {"spreadsheetId": "S1", "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/S1/edit",
                        "sheets": [{"properties": {"sheetId": 0}}, {"properties": {"sheetId": 77}}]}
            if url.endswith("/S1/values:batchUpdate"):
                self.assertEqual(body["valueInputOption"], "RAW")
                self.assertEqual(len(body["data"][0]["values"]), 4)
                return {}
            if url.endswith("/S1:batchUpdate"):
                return {}
            if body and body.get("mimeType", "").endswith("folder"):
                return {"id": "F1"}
            if method == "GET" and url.endswith("/S1?fields=parents"):
                return {"parents": ["root"]}
            if method == "PATCH" and "/S1?" in url:
                self.assertIn("addParents=F1", url)
                self.assertIn("removeParents=root", url)
                return {"id": "S1"}
            raise AssertionError(url)

        with mock.patch.object(G, "_api", side_effect=api):
            url = G.create_test_case_sheet(valid_suite(), valid_analysis(), "Login", self.tmp)
        self.assertEqual(url, "https://docs.google.com/spreadsheets/d/S1/edit")
        self.assertEqual((self.tmp / "google-sheet.txt").read_text().strip(), url)
        self.assertTrue(any(c[1].endswith("/S1:batchUpdate") for c in calls))

    def test_publish_survives_folder_failure(self):
        G._save_token({"refresh_token": "r"})

        def api(method, url, body=None, raw=None, content_type="application/json"):
            if method == "POST" and url == G.SHEETS_API:
                return {"spreadsheetId": "S1", "spreadsheetUrl": "https://x/S1",
                        "sheets": [{"properties": {"sheetId": 0}}, {"properties": {"sheetId": 1}}]}
            if "batchUpdate" in url:
                return {}
            raise G.GoogleSheetsError("Google API 403: insufficient permissions")

        with mock.patch.object(G, "_api", side_effect=api):
            self.assertEqual(G.create_test_case_sheet(valid_suite(), None, "Login"), "https://x/S1")


class SlackIntegrationTests(unittest.TestCase):
    def test_gsheet_format_only_when_connected(self):
        def options(view):
            radio = next(b for b in view["blocks"] if b["block_id"] == "output_format")["element"]
            return [o["value"] for o in radio["options"]], radio["initial_option"]["value"]
        self.assertEqual(options(build_modal("C", "U")), (["md", "csv", "json"], "md"))
        self.assertEqual(options(build_modal("C", "U", allow_gsheet=True)), (["gsheet", "md", "csv", "json"], "gsheet"))

    def test_result_blocks_with_sheet_link(self):
        req = TestCaseRequest("C", "U", "Login", "ctx", "gsheet")
        text = json.dumps(result_blocks(req, valid_suite(), valid_analysis(), sheet_url="https://docs.google.com/spreadsheets/d/X/edit"))
        self.assertIn("Open the test cases in Google Sheets", text)
        self.assertNotIn("attached in the thread", text)
        failed = json.dumps(result_blocks(req, valid_suite(), valid_analysis(), sheet_note="Couldn't create the Google Sheet (x)"))
        self.assertIn("Markdown report attached", failed)


if __name__ == "__main__":
    unittest.main()
