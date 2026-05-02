import unittest

from code_review_ai.prompts.review.overview import build_overview_messages


class OverviewPromptTests(unittest.TestCase):
    def test_overview_prompt_uses_only_current_submission_context(self):
        state = {
            "code": "int main() { return 0; }",
            "history": [
                {
                    "failed_test_case_ids": ["tc-1", "tc-2"],
                    "passed_test_case_ids": ["tc-3"],
                    "code": "int main() { return 1; }",
                }
            ],
            "previous_failed_test_case_ids": ["tc-1", "tc-2"],
            "persistent_failed_test_case_ids": ["tc-2"],
            "fixed_test_case_ids": ["tc-1"],
            "regressed_test_case_ids": ["tc-4"],
            "logic_issues": {},
            "review_links": [],
            "improvement_notes": [],
        }

        messages = build_overview_messages(state)
        user_prompt = messages[1]["content"]

        self.assertIn("Generate only 3 to 5 sentences in one paragraph.", user_prompt)
        self.assertIn(
            "Focus only on what the student improved and what the student needs to avoid next.",
            user_prompt,
        )
        self.assertIn(
            "Do NOT list test cases, test case IDs, testcase names, or any identifier-like labels.",
            user_prompt,
        )
        self.assertIn(
            "If you mention an example failure, describe it using the testcase text or behavior, not any ID.",
            user_prompt,
        )
        self.assertIn(
            "Do not mention submission history, progress tracking, persistence, regression, or earlier attempts.",
            user_prompt,
        )
        self.assertNotIn("Submission history:", user_prompt)
        self.assertNotIn("History-based progress summary:", user_prompt)
        self.assertNotIn("Review links to earlier attempts", user_prompt)
        self.assertNotIn("Failed testcase count:", user_prompt)
        self.assertNotIn("Fixed testcase count since the latest previous submission:", user_prompt)


if __name__ == "__main__":
    unittest.main()
