import unittest
from unittest.mock import MagicMock

from code_review_ai.api.knowledge_graph_route import (
    batch_upsert_exercises,
    batch_patch_exercise_relations,
    patch_exercise_relations,
    upsert_exercise,
)
from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsRequest,
    BatchUpsertExercisesRequest,
    PatchExerciseRelationsRequest,
    UpsertExerciseRequest,
)
from code_review_ai.models.exercise_record import ExerciseRecord


class KnowledgeGraphRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_batch_upsert_exercises_delegates_to_domain_service(self):
        knowledge_graph_service = MagicMock()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        knowledge_graph_service.batch_upsert_exercises.return_value = [exercise]

        response = await batch_upsert_exercises(
            request=BatchUpsertExercisesRequest(
                exercises=[
                    {
                        "exercise_id": "exercise-1",
                        "slug": "two-sum",
                        "title": "Two Sum",
                        "description": "Add two numbers",
                        "content": "Read and print the sum",
                        "difficulty": "easy",
                        "concept_slugs": ["arrays"],
                    }
                ]
            ),
            knowledge_graph_service=knowledge_graph_service,
        )

        self.assertEqual(response.exercises, [exercise])
        knowledge_graph_service.batch_upsert_exercises.assert_called_once()

    async def test_upsert_exercise_delegates_to_domain_service(self):
        knowledge_graph_service = MagicMock()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        knowledge_graph_service.upsert_exercise.return_value = exercise

        response = await upsert_exercise(
            exercise_id="exercise-1",
            request=UpsertExerciseRequest(
                slug="two-sum",
                title="Two Sum",
                description="Add two numbers",
                content="Read and print the sum",
                difficulty="easy",
                concept_slugs=["arrays"],
            ),
            knowledge_graph_service=knowledge_graph_service,
        )

        self.assertEqual(response.exercise, exercise)
        knowledge_graph_service.upsert_exercise.assert_called_once()

    async def test_batch_patch_exercise_relations_delegates_to_domain_service(self):
        knowledge_graph_service = MagicMock()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays", "math"],
        )
        knowledge_graph_service.batch_patch_exercise_relations.return_value = [exercise]

        response = await batch_patch_exercise_relations(
            request=BatchPatchExerciseRelationsRequest(
                exercises=[
                    {
                        "exercise_id": "exercise-1",
                        "concept_slugs": ["math"],
                        "related_exercise_slugs": ["three-sum"],
                    }
                ]
            ),
            knowledge_graph_service=knowledge_graph_service,
        )

        self.assertEqual(response.exercises, [exercise])
        knowledge_graph_service.batch_patch_exercise_relations.assert_called_once()

    async def test_patch_exercise_relations_delegates_to_domain_service(self):
        knowledge_graph_service = MagicMock()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        knowledge_graph_service.patch_exercise_relations.return_value = exercise

        response = await patch_exercise_relations(
            exercise_id="exercise-1",
            request=PatchExerciseRelationsRequest(
                concept_slugs=["math"],
                related_exercise_slugs=["similar-two-sum"],
            ),
            knowledge_graph_service=knowledge_graph_service,
        )

        self.assertEqual(response.exercise, exercise)
        knowledge_graph_service.patch_exercise_relations.assert_called_once()


if __name__ == "__main__":
    unittest.main()
