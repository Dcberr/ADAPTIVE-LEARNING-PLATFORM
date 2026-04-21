import unittest

from app.prompts.review.json_repair import (
    build_review_json_repair_prompt,
    build_review_json_repair_system_prompt,
)


class ReviewJsonRepairPromptTests(unittest.TestCase):
    def test_review_json_repair_prompt_mentions_single_json_object_rules(self):
        system_prompt = build_review_json_repair_system_prompt()
        user_prompt = build_review_json_repair_prompt("not json")

        self.assertIn("valid JSON for the review flow", system_prompt)
        self.assertIn("Return exactly one JSON object.", system_prompt)
        self.assertIn("review-agent output", user_prompt)
        self.assertIn("Raw model output:", user_prompt)


if __name__ == "__main__":
    unittest.main()
