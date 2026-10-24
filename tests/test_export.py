import contextlib
import csv
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import FIXTURES, valid_analysis, valid_suite

from qa_tools.__main__ import main
from qa_tools.export import CSV_COLUMNS, export, render_markdown


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_markdown_has_all_sections_and_cases(self):
        md = render_markdown(valid_suite(), valid_analysis())
        for heading in ("## QA Summary", "## Traceability Matrix", "## Test Case Index", "## Clarifications & Assumptions"):
            self.assertIn(heading, md)
        for tc_id in ("TC-LOGIN-001", "TC-LOGIN-002", "TC-LOGIN-003"):
            self.assertIn(f"### {tc_id}", md)
        self.assertNotIn("{{", md)
        self.assertIn("Assumption-based (A-1)", md)

    def test_csv_round_trip(self):
        export(valid_suite(), valid_analysis(), self.tmp)
        with open(self.tmp / "test-suite.csv", newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 3)
        self.assertEqual(list(rows[0].keys()), CSV_COLUMNS)
        self.assertTrue(rows[0]["Test Steps"].startswith("1. Open the login page\n2. "))
        self.assertEqual(rows[2]["Assumption"], "Yes")

    def test_finalize_refuses_on_errors_and_exports_when_clean(self):
        run = self.tmp / "run"
        shutil.copytree(FIXTURES / "valid", run)
        bad = json.loads((run / "test-suite.json").read_text())
        bad["test_cases"][0]["expected_result"] = "It works correctly for the user"
        (run / "test-suite.json").write_text(json.dumps(bad))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["finalize", str(run / "test-suite.json")]), 1)
        self.assertFalse((run / "test-suite.md").exists())

        (run / "test-suite.json").write_text(json.dumps(valid_suite()))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["finalize", str(run / "test-suite.json")]), 0)
        self.assertTrue((run / "test-suite.md").exists())
        self.assertTrue((run / "test-suite.csv").exists())
        saved = json.loads((run / "test-suite.json").read_text())
        self.assertEqual(saved["coverage_summary"]["computed"]["total_test_cases"], 3)


if __name__ == "__main__":
    unittest.main()
