import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsRequest,
    BatchSyncExercisesToVectorRequest,
    BatchUpsertExercisesRequest,
    PatchExerciseRelationsRequest,
    UpsertExerciseRequest,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.services.knowledge_graph_service import (
    KnowledgeGraphService,
)


class KnowledgeGraphServiceTests(unittest.TestCase):
    def _make_service(self):
        repository = MagicMock()
        embedding_service = MagicMock()
        vector_service = MagicMock()
        scoring_service = MagicMock()
        prerequisite_agent = MagicMock()
        service = KnowledgeGraphService(
            neo4j_repository=repository,
            exercise_embedding_service=embedding_service,
            exercise_vector_service=vector_service,
            exercise_relation_scoring_service=scoring_service,
            prerequisite_weight_agent=prerequisite_agent,
        )
        return service, repository, embedding_service, vector_service, scoring_service

    def test_batch_upsert_exercises_syncs_vector_index(self):
        service, repository, embedding_service, vector_service, scoring_service = (
            self._make_service()
        )
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [SimpleNamespace(concept_id="concept-arrays", slug="arrays")]
        }
        hydrated_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
            embedding=[0.1, 0.2],
            embedding_model="fireworks/qwen3-embedding-8b",
        )
        embedding_service.hydrate_exercises.return_value = [hydrated_exercise]
        repository.upsert_exercises.return_value = [hydrated_exercise]
        scoring_service.evaluate_exercise_concepts.return_value = (
            {"concept-arrays": 1.0},
            {"concept-arrays": 1.0},
        )

        response = service.batch_upsert_exercises(
            BatchUpsertExercisesRequest(
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
            )
        )

        self.assertEqual(response, [hydrated_exercise])
        vector_service.upsert_exercises.assert_called_once_with([hydrated_exercise])

    def test_upsert_exercise_syncs_vector_index(self):
        service, repository, embedding_service, vector_service, scoring_service = (
            self._make_service()
        )
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [SimpleNamespace(concept_id="concept-arrays", slug="arrays")]
        }
        hydrated_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
            embedding=[0.1, 0.2],
            embedding_model="fireworks/qwen3-embedding-8b",
        )
        embedding_service.hydrate_exercises.return_value = [hydrated_exercise]
        repository.upsert_exercises.return_value = [hydrated_exercise]
        scoring_service.evaluate_exercise_concepts.return_value = (
            {"concept-arrays": 1.0},
            {"concept-arrays": 1.0},
        )

        response = service.upsert_exercise(
            "exercise-1",
            UpsertExerciseRequest(
                slug="two-sum",
                title="Two Sum",
                description="Add two numbers",
                content="Read and print the sum",
                difficulty="easy",
                concept_slugs=["arrays"],
            ),
        )

        self.assertEqual(response, hydrated_exercise)
        vector_service.upsert_exercises.assert_called_once_with([hydrated_exercise])

    def test_sync_exercises_to_vector_syncs_requested_ids(self):
        service, repository, embedding_service, vector_service, _scoring_service = (
            self._make_service()
        )
        stored_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        hydrated_exercise = stored_exercise.model_copy(
            update={"embedding": [0.1, 0.2], "embedding_model": "fireworks/qwen3-embedding-8b"}
        )
        repository.get_exercises_by_ids.return_value = {"exercise-1": stored_exercise}
        embedding_service.hydrate_exercises.return_value = [hydrated_exercise]

        response = service.sync_exercises_to_vector(
            BatchSyncExercisesToVectorRequest(exercise_ids=["exercise-1"])
        )

        self.assertEqual(response, [hydrated_exercise])
        vector_service.upsert_exercises.assert_called_once_with([hydrated_exercise])

    def test_batch_patch_exercise_relations_adds_concept_slugs_and_replaces_related_exercises(self):
        service, repository, _embedding_service, _vector_service, scoring_service = (
            self._make_service()
        )
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="three-sum",
            title="Three Sum",
            description="Add three numbers",
            content="Read and print the total",
            difficulty="medium",
            concept_slugs=["arrays", "loops"],
        )
        repository.get_exercises_by_ids.return_value = {"exercise-1": main_exercise}
        repository.get_exercises_by_slugs.return_value = {"three-sum": [related_exercise]}
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [SimpleNamespace(concept_id="concept-arrays", slug="arrays")],
            "math": [SimpleNamespace(concept_id="concept-math", slug="math")],
        }
        scoring_service.evaluate.return_value = (
            {"concept-arrays": 0.7, "concept-math": 1.0},
            {
                "concept-arrays": [{"path": "IMPROVE", "weight": 0.7}],
                "concept-math": [{"path": "REINFORCE", "weight": 1.0}],
            },
            {
                "exercise-2": {
                    "weight": 0.7,
                    "relation_type": "NEXT_STEP",
                    "difficulty_gap": 1.0,
                    "progression_score": 0.7,
                    "similarity_score": 0.7,
                }
            },
        )

        response = service.batch_patch_exercise_relations(
            BatchPatchExerciseRelationsRequest(
                exercises=[
                    {
                        "exercise_id": "exercise-1",
                        "concept_slugs": ["math"],
                        "related_exercise_slugs": ["three-sum"],
                    }
                ]
            )
        )

        self.assertEqual(response[0].concept_slugs, ["arrays", "math"])
        repository.upsert_exercises.assert_called_once()
        repository.replace_exercise_related_exercises_batch.assert_called_once()

    def test_patch_exercise_relations_delegates_to_batch_logic(self):
        service, repository, _embedding_service, _vector_service, scoring_service = (
            self._make_service()
        )
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        repository.get_exercises_by_ids.return_value = {"exercise-1": main_exercise}
        repository.get_exercises_by_slugs.return_value = {}
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [SimpleNamespace(concept_id="concept-arrays", slug="arrays")],
            "math": [SimpleNamespace(concept_id="concept-math", slug="math")],
        }
        scoring_service.evaluate.return_value = (
            {"concept-arrays": 0.7, "concept-math": 1.0},
            {
                "concept-arrays": [{"path": "IMPROVE", "weight": 0.7}],
                "concept-math": [{"path": "REINFORCE", "weight": 1.0}],
            },
            {},
        )

        response = service.patch_exercise_relations(
            "exercise-1",
            PatchExerciseRelationsRequest(concept_slugs=["math"]),
        )

        self.assertEqual(response.exercise_id, "exercise-1")


if __name__ == "__main__":
    unittest.main()
