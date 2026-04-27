import unittest

from code_review_ai.utils.history_matcher import (
    find_first_failed_history_match,
    summarize_history_progress,
)


class HistoryMatcherTests(unittest.TestCase):
    def test_find_first_failed_history_match_returns_newest_failed_match(self):
        match = find_first_failed_history_match(
            [
                {
                    "submission_id": "111",
                    "code": "newest failed",
                    "failed_test_case_ids": ["tc-1"],
                    "passed_test_case_ids": [],
                },
                {
                    "submission_id": "222",
                    "code": "older failed",
                    "failed_test_case_ids": ["tc-1"],
                    "passed_test_case_ids": [],
                },
            ],
            "tc-1",
        )

        self.assertEqual(
            match,
            {
                "submission_id": "111",
                "code": "newest failed",
            },
        )

    def test_summarize_history_progress_formats_key_lists(self):
        summary = summarize_history_progress(
            previous_failed_test_case_ids=["a"],
            persistent_failed_test_case_ids=["b"],
            fixed_test_case_ids=["c"],
            regressed_test_case_ids=["d"],
        )

        self.assertIn("Latest previous failed testcase IDs: ['a']", summary)
        self.assertIn("Persistent failed testcase IDs: ['b']", summary)
        self.assertIn("Fixed testcase IDs: ['c']", summary)
        self.assertIn("Regressed testcase IDs: ['d']", summary)


if __name__ == "__main__":
    unittest.main()
