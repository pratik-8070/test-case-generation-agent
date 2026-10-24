import unittest

from helpers import valid_analysis, valid_suite

from qa_tools.validate import validate_analysis, validate_suite


class ValidateSuiteTests(unittest.TestCase):
    def test_valid_fixture_passes_clean(self):
        report = validate_suite(valid_suite(), valid_analysis())
        self.assertTrue(report.ok, report.render())
        self.assertEqual(report.warnings, [])

    def test_missing_required_field(self):
        suite = valid_suite()
        del suite["test_cases"][0]["expected_result"]
        report = validate_suite(suite, valid_analysis())
        self.assertIn("schema-required", report.codes())

    def test_bad_enum_and_id_pattern(self):
        suite = valid_suite()
        suite["test_cases"][0]["priority"] = "P1"
        suite["test_cases"][1]["id"] = "TC-login-2"
        codes = validate_suite(suite, valid_analysis()).codes()
        self.assertIn("schema-enum", codes)
        self.assertIn("schema-pattern", codes)

    def test_duplicate_id(self):
        suite = valid_suite()
        suite["test_cases"][1]["id"] = "TC-LOGIN-001"
        self.assertIn("duplicate-id", validate_suite(suite, valid_analysis()).codes())

    def test_vague_expected_result_is_error(self):
        suite = valid_suite()
        suite["test_cases"][0]["expected_result"] = "Login works as expected for the user"
        report = validate_suite(suite, valid_analysis())
        self.assertFalse(report.ok)
        self.assertIn("vague-expected-result", report.codes())

    def test_soft_vague_expected_result_is_warning(self):
        suite = valid_suite()
        suite["test_cases"][1]["expected_result"] = "An appropriate error message is displayed to the user"
        report = validate_suite(suite, valid_analysis())
        self.assertTrue(report.ok)
        self.assertIn("soft-vague-expected-result", report.codes())

    def test_vague_step(self):
        suite = valid_suite()
        suite["test_cases"][0]["steps"] = ["Test the functionality"]
        self.assertIn("vague-step", validate_suite(suite, valid_analysis()).codes())

    def test_dangling_trace_ref(self):
        suite = valid_suite()
        suite["test_cases"][0]["source_refs"] = ["AC-9.9"]
        self.assertIn("dangling-trace-ref", validate_suite(suite, valid_analysis()).codes())

    def test_dangling_assumption_ref(self):
        suite = valid_suite()
        suite["test_cases"][2]["assumption_refs"] = ["A-7"]
        self.assertIn("dangling-assumption-ref", validate_suite(suite, valid_analysis()).codes())

    def test_inferred_item_requires_assumption_flag(self):
        analysis = valid_analysis()
        analysis["acceptance_criteria"][0]["origin"] = "inferred"
        self.assertIn("unsupported-assumption", validate_suite(valid_suite(), analysis).codes())

    def test_assumption_flag_mismatch(self):
        suite = valid_suite()
        suite["test_cases"][2]["assumption"] = False
        self.assertIn("assumption-flag-mismatch", validate_suite(suite, valid_analysis()).codes())

    def test_without_analysis_warns(self):
        report = validate_suite(valid_suite(), None)
        self.assertTrue(report.ok)
        self.assertIn("no-analysis", report.codes())


class ValidateAnalysisTests(unittest.TestCase):
    def test_valid_analysis(self):
        report = validate_analysis(valid_analysis())
        self.assertTrue(report.ok, report.render())

    def test_open_blocking_question_blocks(self):
        analysis = valid_analysis()
        analysis["clarifications"].append(
            {"id": "Q-2", "question": "What is the password policy?", "severity": "blocking", "status": "open"})
        self.assertIn("blocking-clarification-open", validate_analysis(analysis).codes())
        # and the suite gate also refuses
        self.assertIn("blocking-clarification-open", validate_suite(valid_suite(), analysis).codes())

    def test_dangling_parent_and_unknown_feature(self):
        analysis = valid_analysis()
        analysis["acceptance_criteria"][0]["requirement_id"] = "US-404"
        analysis["requirements"][0]["feature"] = "CART"
        codes = validate_analysis(analysis).codes()
        self.assertIn("dangling-parent", codes)
        self.assertIn("unknown-feature", codes)

    def test_duplicate_trace_id(self):
        analysis = valid_analysis()
        analysis["business_rules"][0]["id"] = "AC-1.1"
        self.assertIn("duplicate-trace-id", validate_analysis(analysis).codes())

    def test_invalid_input_type(self):
        analysis = valid_analysis()
        analysis["inputs"][0]["input_type"] = "STORY"
        self.assertIn("schema-enum", validate_analysis(analysis).codes())


if __name__ == "__main__":
    unittest.main()
