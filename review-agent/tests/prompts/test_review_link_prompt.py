import unittest

from app.prompts.review.review_link import build_review_link_messages


class ReviewLinkPromptTests(unittest.TestCase):
    def test_review_link_prompt_uses_sorted_history_contract(self):
        messages = build_review_link_messages(
            current_code="int main() { return 0; }",
            batch_candidates=[
                {
                    "current_issue": "The negative case is still not handled.",
                    "current_code_snippet": "if (x > 0) { cout << \"positive\"; }",
                    "comparison_mode": "persistent",
                    "history_matches": [
                        {
                            "submission_index": 1,
                            "testcase_status": "failed",
                            "code": "if (x > 0) { cout << \"positive\"; }",
                        },
                        {
                            "submission_index": 2,
                            "testcase_status": "passed",
                            "code": "if (x >= 0) { cout << \"non-negative\"; }",
                        },
                    ],
                }
            ],
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("sorted testcase history", system_prompt)
        self.assertIn("Matching history entries for this testcase", user_prompt)
        self.assertIn("Comparison mode: persistent", user_prompt)
        self.assertIn("Use the newest matching history entry as the main comparison anchor", user_prompt)


if __name__ == "__main__":
    unittest.main()
