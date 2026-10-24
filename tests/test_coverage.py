import unittest

from helpers import valid_analysis, valid_suite

from qa_tools.coverage import compute_coverage, coverage_report, write_coverage


class CoverageTests(unittest.TestCase):
    def test_counts_and_rollup(self):
        cov = compute_coverage(valid_suite(), valid_analysis())
        self.assertEqual(cov["total_test_cases"], 3)
        self.assertEqual((cov["positive"], cov["negative"], cov["boundary"]), (1, 1, 1))
        self.assertEqual(cov["requirements_covered"], 1)  # US-1 covered through its ACs/BR
        self.assertEqual(cov["acceptance_criteria_covered"], 2)
        self.assertEqual(cov["uncovered"], {"requirements": [], "acceptance_criteria": [], "business_rules": []})
        self.assertEqual(cov["assumption_based"], 1)

    def test_uncovered_ac_is_error(self):
        suite = valid_suite()
        suite["test_cases"] = [tc for tc in suite["test_cases"] if "AC-1.2" not in tc["source_refs"]]
        report = coverage_report(suite, valid_analysis())
        self.assertFalse(report.ok)
        self.assertIn("uncovered", report.codes())

    def test_documented_gap_downgrades_to_warning(self):
        suite = valid_suite()
        suite["test_cases"] = [tc for tc in suite["test_cases"] if "BR-1" not in tc["source_refs"]]
        suite["coverage_summary"]["gaps"] = [{"ref": "BR-1", "description": "Lockout", "reason": "Needs backend reset tooling"}]
        report = coverage_report(suite, valid_analysis())
        self.assertTrue(report.ok, report.render())
        self.assertIn("accepted-gap", report.codes())

    def test_requirement_without_negative(self):
        suite = valid_suite()
        suite["test_cases"] = suite["test_cases"][:1]
        cov = compute_coverage(suite, valid_analysis())
        self.assertEqual(cov["requirements_without_negative"], ["US-1"])

    def test_write_preserves_gaps(self):
        suite = valid_suite()
        suite["coverage_summary"]["gaps"] = [{"description": "Performance not specified"}]
        write_coverage(suite, valid_analysis())
        self.assertIn("computed", suite["coverage_summary"])
        self.assertEqual(len(suite["coverage_summary"]["gaps"]), 1)


if __name__ == "__main__":
    unittest.main()
