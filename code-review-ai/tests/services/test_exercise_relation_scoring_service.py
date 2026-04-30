import unittest

from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.models.exercise_record import ExerciseRecord


class ExerciseRelationScoringServiceTests(unittest.TestCase):
    def test_compute_concept_weight_prefers_core_required_concepts(self):
        agent = ExerciseRelationScoringService()

        weight = agent._compute_concept_weight(
            centrality_score=0.95,
            solution_dependency_score=0.9,
            explicit_usage_score=0.85,
            difficulty_alignment_score=0.8,
        )

        self.assertEqual(weight, 1.0)

    def test_compute_concept_weight_downgrades_background_concepts(self):
        agent = ExerciseRelationScoringService()

        weight = agent._compute_concept_weight(
            centrality_score=0.25,
            solution_dependency_score=0.2,
            explicit_usage_score=0.3,
            difficulty_alignment_score=0.4,
        )

        self.assertEqual(weight, 0.3)

    def test_relation_evaluation_is_deterministic_for_same_inputs(self):
        agent = ExerciseRelationScoringService()
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays", "addition"],
            embedding=[1.0, 0.0, 0.0],
            content_hash="hash-1",
        )
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="sum-three",
            title="Sum Three",
            description="Add three numbers",
            content="Read and print the total",
            difficulty="easy",
            concept_slugs=["arrays", "addition"],
            embedding=[0.98, 0.02, 0.0],
            content_hash="hash-2",
        )

        first_result = agent.evaluate(
            main_exercise=main_exercise,
            concepts=[],
            related_exercises=[related_exercise],
            main_concept_slugs=["arrays", "addition"],
            related_concept_slugs_by_exercise={"exercise-2": ["arrays", "addition"]},
        )
        second_result = agent.evaluate(
            main_exercise=main_exercise,
            concepts=[],
            related_exercises=[related_exercise],
            main_concept_slugs=["arrays", "addition"],
            related_concept_slugs_by_exercise={"exercise-2": ["arrays", "addition"]},
        )

        self.assertEqual(first_result[2], second_result[2])

    def test_relation_evaluation_scores_multiple_related_exercises(self):
        agent = ExerciseRelationScoringService()
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays", "addition"],
            embedding=[1.0, 0.0, 0.0],
            content_hash="hash-1",
        )
        cached_related = ExerciseRecord(
            exercise_id="exercise-2",
            slug="sum-three",
            title="Sum Three",
            description="Add three numbers",
            content="Read and print the total",
            difficulty="easy",
            concept_slugs=["arrays", "addition"],
            embedding=[0.98, 0.02, 0.0],
            content_hash="hash-2",
        )
        new_related = ExerciseRecord(
            exercise_id="exercise-3",
            slug="sum-four",
            title="Sum Four",
            description="Add four numbers",
            content="Read and print the total",
            difficulty="medium",
            concept_slugs=["arrays", "addition", "loops"],
            embedding=[0.85, 0.15, 0.0],
            content_hash="hash-3",
        )

        agent.evaluate(
            main_exercise=main_exercise,
            concepts=[],
            related_exercises=[cached_related],
            main_concept_slugs=["arrays", "addition"],
            related_concept_slugs_by_exercise={"exercise-2": ["arrays", "addition"]},
        )
        result = agent.evaluate(
            main_exercise=main_exercise,
            concepts=[],
            related_exercises=[cached_related, new_related],
            main_concept_slugs=["arrays", "addition"],
            related_concept_slugs_by_exercise={
                "exercise-2": ["arrays", "addition"],
                "exercise-3": ["arrays", "addition", "loops"],
            },
        )

        self.assertIn("exercise-2", result[2])
        self.assertIn("exercise-3", result[2])
        self.assertEqual(result[2]["exercise-3"]["relation_type"], "SAME_CONCEPT_HARDER")

    def test_compute_related_weight_prefers_high_similarity_progression_pairs(self):
        agent = ExerciseRelationScoringService()

        weight = agent._compute_related_weight(
            solution_pattern_score=0.9,
            difficulty_alignment_score=0.8,
            progression_score=0.9,
            similarity_score=0.95,
            relation_type="NEXT_STEP",
        )

        self.assertEqual(weight, 1.0)

    def test_compute_related_weight_downgrades_weak_pairs(self):
        agent = ExerciseRelationScoringService()

        weight = agent._compute_related_weight(
            solution_pattern_score=0.3,
            difficulty_alignment_score=0.4,
            progression_score=0.25,
            similarity_score=0.3,
            relation_type="SIMILAR_PRACTICE",
        )

        self.assertEqual(weight, 0.3)

    def test_relation_scoring_uses_embeddings_and_concept_overlap(self):
        agent = ExerciseRelationScoringService()
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Use an array and simple addition",
            content="int main() { return 0; }",
            difficulty="easy",
            concept_slugs=["arrays", "addition"],
            embedding=[1.0, 0.0],
        )
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="three-sum",
            title="Three Sum",
            description="Use arrays and addition with one extra step",
            content="int main() { return 1; }",
            difficulty="medium",
            concept_slugs=["arrays", "addition"],
            embedding=[0.95, 0.05],
        )

        result = agent.evaluate(
            main_exercise=main_exercise,
            concepts=[],
            related_exercises=[related_exercise],
            main_concept_slugs=["arrays", "addition"],
            related_concept_slugs_by_exercise={"exercise-2": ["arrays", "addition"]},
        )

        metadata = result[2]["exercise-2"]
        self.assertEqual(metadata["relation_type"], "SAME_CONCEPT_HARDER")
        self.assertEqual(metadata["weight"], 1.0)
        self.assertGreaterEqual(metadata["similarity_score"], 0.8)

    def test_concept_scoring_uses_exercise_text_and_tags(self):
        from code_review_ai.models.knowledge_graph import ConceptRecord

        agent = ExerciseRelationScoringService()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="array-sum",
            title="Array Sum",
            description="Use an array to add values",
            content="Read n numbers into an array and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        concept = ConceptRecord(
            concept_id="arrays",
            slug="arrays",
            name="Arrays",
            description="Store and traverse values in arrays",
            difficulty=1,
        )

        weight = agent._score_concept_weight(
            main_exercise=exercise,
            concept=concept,
        )
        recommended_weight = agent._score_recommended_weight(
            concept=concept,
            concept_weight=weight,
            main_exercise=exercise,
        )

        self.assertIn(weight, {0.3, 0.7, 1.0})
        self.assertEqual(recommended_weight, weight)


if __name__ == "__main__":
    unittest.main()
