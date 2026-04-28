import unittest

from code_review_ai.agents.exercise_weight_agent import ExerciseWeightAgent


class ExerciseWeightAgentTests(unittest.TestCase):
    def test_compute_concept_weight_prefers_core_required_concepts(self):
        agent = ExerciseWeightAgent(client=None, model_name="test-model")

        weight = agent._compute_concept_weight(
            centrality_score=0.95,
            solution_dependency_score=0.9,
            explicit_usage_score=0.85,
            difficulty_alignment_score=0.8,
        )

        self.assertEqual(weight, 1.0)

    def test_compute_concept_weight_downgrades_background_concepts(self):
        agent = ExerciseWeightAgent(client=None, model_name="test-model")

        weight = agent._compute_concept_weight(
            centrality_score=0.25,
            solution_dependency_score=0.2,
            explicit_usage_score=0.3,
            difficulty_alignment_score=0.4,
        )

        self.assertEqual(weight, 0.3)

    def test_compute_related_weight_prefers_high_similarity_progression_pairs(self):
        agent = ExerciseWeightAgent(client=None, model_name="test-model")

        weight = agent._compute_related_weight(
            solution_pattern_score=0.9,
            difficulty_alignment_score=0.8,
            progression_score=0.9,
            similarity_score=0.95,
            relation_type="NEXT_STEP",
        )

        self.assertEqual(weight, 1.0)

    def test_compute_related_weight_downgrades_weak_pairs(self):
        agent = ExerciseWeightAgent(client=None, model_name="test-model")

        weight = agent._compute_related_weight(
            solution_pattern_score=0.3,
            difficulty_alignment_score=0.4,
            progression_score=0.25,
            similarity_score=0.3,
            relation_type="SIMILAR_PRACTICE",
        )

        self.assertEqual(weight, 0.3)


if __name__ == "__main__":
    unittest.main()
