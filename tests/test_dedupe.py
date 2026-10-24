import copy
import unittest

from helpers import valid_suite

from qa_tools.dedupe import find_duplicates


class DedupeTests(unittest.TestCase):
    def test_valid_fixture_has_no_duplicates(self):
        report = find_duplicates(valid_suite())
        self.assertEqual(report.issues, [], report.render())

    def test_exact_duplicate_is_error(self):
        suite = valid_suite()
        clone = copy.deepcopy(suite["test_cases"][0])
        clone["id"] = "TC-LOGIN-004"
        clone["scenario"] = "Successful login with correct credentials"  # reworded title, same content
        suite["test_cases"].append(clone)
        report = find_duplicates(suite)
        self.assertIn("exact-duplicate", report.codes())
        self.assertFalse(report.ok)

    def test_near_duplicate_is_warning(self):
        suite = valid_suite()
        clone = copy.deepcopy(suite["test_cases"][1])
        clone["id"] = "TC-LOGIN-004"
        clone["steps"][2] = "Click the 'Log in' button"
        suite["test_cases"].append(clone)
        report = find_duplicates(suite)
        self.assertIn("near-duplicate", report.codes())
        self.assertTrue(report.ok)

    def test_distinct_boundaries_with_different_data_and_types_not_flagged(self):
        suite = valid_suite()
        clone = copy.deepcopy(suite["test_cases"][0])
        clone.update(id="TC-LOGIN-004", test_type="Validation", scenario="Email field rejects missing @",
                     test_data={"email": "userexample.com"},
                     steps=["Open the login page", "Enter an email without '@'", "Click 'Log in'"],
                     expected_result="Inline error 'Enter a valid email address' appears under the email field")
        suite["test_cases"].append(clone)
        self.assertEqual(find_duplicates(suite).issues, [])

    def test_data_variants_reported_once_per_group(self):
        suite = valid_suite()
        base = suite["test_cases"][1]
        for n, pw in enumerate(["short1", "x" * 65, "nodigits"], start=4):
            clone = copy.deepcopy(base)
            clone.update(id=f"TC-LOGIN-{n:03d}", test_data={"email": "user@example.com", "password": pw})
            suite["test_cases"].append(clone)
        report = find_duplicates(suite)
        variants = [i for i in report.issues if i.code == "data-variants"]
        self.assertEqual(len(variants), 1)
        self.assertIn("TC-LOGIN-002", variants[0].ref)
        self.assertIn("TC-LOGIN-006", variants[0].ref)
        self.assertNotIn("near-duplicate", report.codes())

    def test_overlapping_scenario_titles(self):
        suite = valid_suite()
        clone = copy.deepcopy(suite["test_cases"][1])
        clone.update(id="TC-LOGIN-004", scenario="Log in with a wrong password.",
                     test_type="Error Handling",
                     steps=["Navigate to /login", "Type a password with a typo", "Press Enter"],
                     expected_result="Message 'Invalid email or password' is shown; password field is cleared")
        suite["test_cases"].append(clone)
        self.assertIn("overlapping-scenario", find_duplicates(suite).codes())


if __name__ == "__main__":
    unittest.main()
