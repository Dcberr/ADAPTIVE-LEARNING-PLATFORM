import os
import unittest

from code_review_ai.prompts.recommendation.context_planner import (
    build_context_planner_prompt,
    build_context_planner_system_prompt,
)

try:
    from openai import OpenAI

    from code_review_ai.config import clear_env_config_cache, get_env_config
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    OpenAI = None
    clear_env_config_cache = None
    get_env_config = None
    _LIVE_IMPORT_ERROR = exc
else:
    _LIVE_IMPORT_ERROR = None


RUN_LIVE_PROMPT_TESTS = os.getenv("RUN_PROMPT_LIVE_TESTS", "").lower() == "true"


class ContextPlannerPromptTests(unittest.TestCase):
    @staticmethod
    def _build_sample_prompt() -> str:
        return build_context_planner_prompt(
            student_id="student-001",
            exercise_id="exercise-two-sum",
            current_concept="input-output",
            critical_errors=2,
            review_summary="The student still mishandles numeric input.",
            review_detail="The code keeps values as strings and prints the wrong result.",
            tested_concepts=[
                {"concept_id": "input-output", "weight": 1.0},
                {"concept_id": "arithmetic", "weight": 0.7},
            ],
            recommended_paths=[
                {"concept_id": "input-output", "path": "IMPROVE", "weight": 0.9}
            ],
            has_latest_submission=True,
            concept_mastery=0.55,
            debugging_independence=0.42,
            concept_transfer=0.48,
            learning_velocity=0.51,
        )

    def test_system_prompt_contains_decision_policy_and_block_meanings(self):
        prompt = build_context_planner_system_prompt()

        self.assertIn("minimum additional context needed", prompt)
        self.assertIn("Prefer the smallest sufficient set of blocks.", prompt)
        self.assertIn("Meaning of each block:", prompt)
        self.assertIn("- review_trend", prompt)
        self.assertIn("- concept_progression", prompt)
        self.assertIn("Contrastive rules:", prompt)

    def test_user_prompt_contains_reasoning_checklist_examples_and_json_schema(self):
        prompt = self._build_sample_prompt()

        self.assertIn("Reasoning checklist:", prompt)
        self.assertIn("What is the strongest current signal", prompt)
        self.assertIn("Few-shot guidance:", prompt)
        self.assertIn("Example 1:", prompt)
        self.assertIn("Negative example:", prompt)
        self.assertIn('"need_review_trend": true,', prompt)
        self.assertIn('"priority_signal": "current_review_issue"', prompt)
        self.assertNotIn("true|false", prompt)
        self.assertIn("Current exercise: exercise-two-sum", prompt)
        self.assertIn("Anchor concept: input-output", prompt)

    @unittest.skipUnless(
        RUN_LIVE_PROMPT_TESTS,
        "Set RUN_PROMPT_LIVE_TESTS=true to call the configured model and print its response.",
    )
    @unittest.skipIf(
        OpenAI is None or get_env_config is None or clear_env_config_cache is None,
        f"missing runtime dependency: {_LIVE_IMPORT_ERROR}",
    )
    def test_live_context_planner_prints_model_response(self):
        clear_env_config_cache()
        config = get_env_config()
        stage = config.get_stage_config("recommendation", "context_planner")
        client = OpenAI(
            api_key=config.fireworks_api_key,
            base_url=config.fireworks_base_url,
        )

        response = client.chat.completions.create(
            model=stage.model_name,
            messages=[
                {
                    "role": "system",
                    "content": build_context_planner_system_prompt(),
                },
                {
                    "role": "user",
                    "content": self._build_sample_prompt(),
                },
            ],
            temperature=stage.temperature,
            max_tokens=stage.max_tokens,
        )

        content = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason
        usage = getattr(response, "usage", None)
        print("\n=== Context Planner Model ===")
        print(stage.model_name)
        print("=== Context Planner Max Tokens ===")
        print(stage.max_tokens)
        print("=== Context Planner Finish Reason ===")
        print(finish_reason)
        print("=== Context Planner Usage ===")
        print(usage)
        print("=== Context Planner Response ===")
        print(content)
        self.assertTrue(content.strip())


if __name__ == "__main__":
    unittest.main()
