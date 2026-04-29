import unittest

try:
    from code_review_ai.config import build_env_config
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    build_env_config = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@unittest.skipIf(build_env_config is None, f"missing runtime dependency: {_IMPORT_ERROR}")
class ModelConfigOverrideTests(unittest.TestCase):
    def test_review_stage_defaults_are_split_by_role(self):
        config = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
            }
        )

        logic_stage = config.get_stage_config("review", "logic")
        fix_hint_stage = config.get_stage_config("review", "fix_hint")
        review_link_stage = config.get_stage_config("review", "review_link")
        scoring_stage = config.get_stage_config("review", "scoring")

        self.assertEqual(logic_stage.model_name, "fireworks/deepseek-v3p2")
        self.assertEqual(logic_stage.temperature, 0.1)
        self.assertEqual(logic_stage.max_tokens, 2200)

        self.assertEqual(fix_hint_stage.model_name, "fireworks/deepseek-v3p2")
        self.assertEqual(fix_hint_stage.temperature, 0.25)
        self.assertEqual(fix_hint_stage.max_tokens, 900)

        self.assertEqual(review_link_stage.model_name, "fireworks/deepseek-v3p2")
        self.assertEqual(review_link_stage.temperature, 0.1)
        self.assertEqual(review_link_stage.max_tokens, 1000)

        self.assertEqual(scoring_stage.model_name, "fireworks/deepseek-v3p2")
        self.assertEqual(scoring_stage.temperature, 0.05)
        self.assertEqual(scoring_stage.max_tokens, 1800)

    def test_stage_specific_recommendation_model_override(self):
        config = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "RECOMMENDATION_CONTEXT_PLANNER_MODEL": "fireworks/test-context-planner",
                "RECOMMENDATION_CONTEXT_PLANNER_TEMPERATURE": "0.05",
                "RECOMMENDATION_CONTEXT_PLANNER_MAX_TOKENS": "777",
            }
        )

        stage = config.get_stage_config("recommendation", "context_planner")
        self.assertEqual(stage.model_name, "fireworks/test-context-planner")
        self.assertEqual(stage.temperature, 0.05)
        self.assertEqual(stage.max_tokens, 777)

    def test_feature_level_model_override_applies_to_other_stages(self):
        config = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "REVIEW_MODEL": "fireworks/test-review-model",
            }
        )

        logic_stage = config.get_stage_config("review", "logic")
        scoring_stage = config.get_stage_config("review", "scoring")

        self.assertEqual(logic_stage.model_name, "fireworks/test-review-model")
        self.assertEqual(scoring_stage.model_name, "fireworks/test-review-model")
        self.assertEqual(logic_stage.max_tokens, 2200)
        self.assertEqual(scoring_stage.max_tokens, 1800)

    def test_stage_specific_override_wins_over_feature_level_model(self):
        config = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "RECOMMENDATION_MODEL": "fireworks/recommendation-default",
                "RECOMMENDATION_ROADMAP_BUILDER_MODEL": "fireworks/roadmap-builder-override",
            }
        )

        roadmap_stage = config.get_stage_config("recommendation", "roadmap_builder")
        explanation_stage = config.get_stage_config(
            "recommendation", "explanation_builder"
        )

        self.assertEqual(roadmap_stage.model_name, "fireworks/roadmap-builder-override")
        self.assertEqual(explanation_stage.model_name, "fireworks/recommendation-default")

    def test_recommendation_candidate_reranker_stage_can_be_overridden(self):
        config = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "RECOMMENDATION_CANDIDATE_RERANKER_MODEL": "fireworks/test-reranker",
                "RECOMMENDATION_CANDIDATE_RERANKER_TEMPERATURE": "0.0",
                "RECOMMENDATION_CANDIDATE_RERANKER_MAX_TOKENS": "555",
            }
        )

        stage = config.get_stage_config("recommendation", "candidate_reranker")
        self.assertEqual(stage.model_name, "fireworks/test-reranker")
        self.assertEqual(stage.temperature, 0.0)
        self.assertEqual(stage.max_tokens, 555)

if __name__ == "__main__":
    unittest.main()
