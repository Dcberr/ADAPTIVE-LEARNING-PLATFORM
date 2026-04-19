import unittest

from app.prompts.review.review_link import build_review_link_messages


class ReviewLinkPromptTests(unittest.TestCase):
    def test_review_link_prompt_uses_first_failed_submission_contract(self):
        messages = build_review_link_messages(
            current_code="int main() { return 0; }",
            batch_candidates=[
                {
                    "issue": {
                        "issue": "The negative case is still not handled.",
                    },
                    "current_code_snippet": "if (x > 0) { cout << \"positive\"; }",
                    "comparison_mode": "persistent",
                    "previous_submission": {
                        "submission_id": "11111111-1111-1111-1111-111111111111",
                        "code": "if (x > 0) { cout << \"positive\"; }",
                    },
                }
            ],
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("first earlier submission where", system_prompt)
        self.assertIn("the same testcase also failed", system_prompt)
        self.assertIn("First earlier failed submission for this testcase", user_prompt)
        self.assertIn("Comparison mode: persistent", user_prompt)
        self.assertIn("Use only the first earlier submission where the testcase failed.", user_prompt)
        self.assertIn("previous_submission_id", user_prompt)
        self.assertIn("previous_code_snippets", user_prompt)


if __name__ == "__main__":
    unittest.main()
