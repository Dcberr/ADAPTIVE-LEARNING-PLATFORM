import unittest

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.prompts.knowledge_graph.exercise_concept_weight import (
    build_exercise_concept_weight_messages,
)
from code_review_ai.prompts.knowledge_graph.exercise_relation_weight import (
    build_exercise_relation_weight_messages,
)


class ExerciseWeightPromptTests(unittest.TestCase):
    def test_concept_prompt_only_requests_concept_output(self):
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            tags=["math"],
        )
        concepts = [
            ConceptRecord(
                concept_id="concept-1",
                slug="arrays",
                name="Arrays",
                description="Array basics",
                difficulty=1,
            )
        ]

        messages = build_exercise_concept_weight_messages(exercise, concepts)
        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn('"concept_id": "string"', user_prompt)
        self.assertNotIn('"exercise_id": "string"', user_prompt)
        self.assertNotIn('"related_exercises"', user_prompt)
        self.assertIn('"centrality_score": 0.7', user_prompt)
        self.assertIn('"solution_dependency_score": 0.7', user_prompt)
        self.assertIn('"explicit_usage_score": 0.7', user_prompt)
        self.assertIn('"difficulty_alignment_score": 0.7', user_prompt)
        self.assertNotIn('"weight": 1.0', user_prompt)
        self.assertNotIn('"reason"', user_prompt)
        self.assertIn("Think in this order before writing the JSON", system_prompt)
        self.assertIn("Do not inflate scores", user_prompt)

    def test_relation_prompt_only_requests_related_exercise_output(self):
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            tags=["math"],
        )
        concepts = [
            ConceptRecord(
                concept_id="concept-1",
                slug="arrays",
                name="Arrays",
                description="Array basics",
                difficulty=1,
            )
        ]
        related_exercises = [
            ExerciseRecord(
                exercise_id="exercise-2",
                slug="sum-three",
                title="Sum Three",
                description="Add three numbers",
                content="Read and print the total",
                difficulty="easy",
                tags=["math"],
            )
        ]

        messages = build_exercise_relation_weight_messages(
            exercise,
            concepts,
            related_exercises,
        )
        user_prompt = messages[1]["content"]

        self.assertIn('"related_exercises"', user_prompt)
        self.assertIn('"exercise_id": "string"', user_prompt)
        self.assertNotIn('"recommended_paths"', user_prompt)
        self.assertIn('"solution_pattern_score": 0.7', user_prompt)
        self.assertIn('"difficulty_alignment_score": 0.7', user_prompt)
        self.assertNotIn('"concept_overlap_score"', user_prompt)
        self.assertNotIn('"target_concept_id"', user_prompt)
        self.assertNotIn('"shared_concept_ids"', user_prompt)
        self.assertNotIn('"reason"', user_prompt)
        self.assertIn("Think in this order before writing the JSON", messages[0]["content"])
        self.assertIn("Do not inflate similarity_score", user_prompt)
        self.assertIn("If the candidate adds one clean new twist", user_prompt)


if __name__ == "__main__":
    unittest.main()
