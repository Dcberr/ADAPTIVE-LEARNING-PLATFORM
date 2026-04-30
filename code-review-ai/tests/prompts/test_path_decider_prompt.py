import unittest

from code_review_ai.prompts.recommendation.path_decider import (
    build_path_decider_prompt,
    build_path_decider_system_prompt,
)


class PathDeciderPromptTests(unittest.TestCase):
    def test_system_prompt_contains_reasoning_protocol(self):
        prompt = build_path_decider_system_prompt()

        self.assertIn("Decision policy:", prompt)
        self.assertIn("Reasoning protocol:", prompt)
        self.assertIn("Path definitions:", prompt)
        self.assertIn("Explain why the chosen path beats the strongest alternative.", prompt)
        self.assertIn("student history", prompt)
        self.assertIn("PREREQUISITE_REVIEW", prompt)
        self.assertIn("HARDER", prompt)
        self.assertIn("TRANSFER", prompt)

    def test_user_prompt_appends_only_validated_trend_blocks(self):
        prompt = build_path_decider_prompt(
            anchor_concept="arrays",
            suggested_focus_concept="arrays",
            critical_errors=2,
            latest_review_summary="The student still misuses loop bounds.",
            review_trend_summary={
                "previous_review_id": "review-1",
                "previous_review_summary": "Earlier work had the same off-by-one issue.",
                "previous_review_concept": "arrays",
                "previous_submission_id": "submission-1",
                "history_count": 2,
            },
            submission_trend_summary=None,
            student_history_summary={
                "attempted_exercise_count": 4,
                "assigned_exercise_count": 2,
                "recent_attempted_exercise_ids": ["e1", "e2"],
                "recent_assigned_exercise_ids": ["e3"],
            },
            exercise_graph={"best_recommended_weight": 1.0},
            valid_focus_concepts=["arrays", "loops"],
        )

        self.assertIn("Validated review trend:", prompt)
        self.assertNotIn("Validated submission trend:", prompt)
        self.assertIn("Validated student history:", prompt)
        self.assertIn("Exercise graph summary:", prompt)
        self.assertIn("Decision checklist:", prompt)

    def test_user_prompt_omits_optional_sections_when_missing(self):
        prompt = build_path_decider_prompt(
            anchor_concept="input-output",
            suggested_focus_concept="input-output",
            critical_errors=0,
            latest_review_summary="The student is improving on formatting output.",
            review_trend_summary=None,
            submission_trend_summary=None,
            student_history_summary=None,
            exercise_graph=None,
            valid_focus_concepts=["input-output"],
        )

        self.assertNotIn("Validated review trend:", prompt)
        self.assertNotIn("Validated submission trend:", prompt)
        self.assertNotIn("Validated student history:", prompt)
        self.assertNotIn("Exercise graph summary:", prompt)
        self.assertIn("Latest review summary:", prompt)


if __name__ == "__main__":
    unittest.main()
