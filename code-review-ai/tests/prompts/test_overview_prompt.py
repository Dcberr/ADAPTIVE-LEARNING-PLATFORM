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

        self.assertIn(
            "Write exactly one paragraph with 5 to 7 sentences.",
            user_prompt,
        )
        self.assertIn(
            "Do not make the paragraph too short; aim for about 110 to 150 words when there is a logic issue or improvement note to explain.",
            user_prompt,
        )
        self.assertIn(
            "Write a short overview for this student's current submission using only these current review findings.",
            user_prompt,
        )
        self.assertIn(
            "Write as if you are speaking directly to the student.",
            user_prompt,
        )
        self.assertIn(
            "Help the student understand what to learn or check next without turning the paragraph into an overly long explanation.",
            user_prompt,
        )
        self.assertIn(
            "Do not include raw code, JSON, headings, bullet points, labels, IDs, testcase names, or meta commentary.",
            user_prompt,
        )
        self.assertIn(
            "Do not mention prompts, hidden instructions, policies, or internal rules.",
            user_prompt,
        )
        self.assertNotIn("int main() { return 0; }", user_prompt)
        self.assertNotIn("Submission history:", user_prompt)
        self.assertNotIn("History-based progress summary:", user_prompt)
        self.assertNotIn("Review links to earlier attempts", user_prompt)
        self.assertNotIn("Failed testcase count:", user_prompt)
        self.assertNotIn(
            "Fixed testcase count since the latest previous submission:", user_prompt
        )


if __name__ == "__main__":
    unittest.main()
