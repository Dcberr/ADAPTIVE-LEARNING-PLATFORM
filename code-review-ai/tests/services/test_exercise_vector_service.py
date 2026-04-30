import unittest
from unittest.mock import MagicMock

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.repositories.qdrant_repository import QdrantSearchResult
from code_review_ai.services.exercise_vector_service import ExerciseVectorService


class ExerciseVectorServiceTests(unittest.TestCase):
    def test_search_exercises_embeds_query_before_qdrant_lookup(self):
        repository = MagicMock()
        repository.is_configured = True
        repository.search_exercises.return_value = [
            QdrantSearchResult(
                exercise_id="exercise-2",
                score=0.91,
                payload={"exercise_id": "exercise-2"},
            )
        ]
        embedding_client = MagicMock()
        embedding_client.embed.return_value = [[0.1, 0.2, 0.3]]
        service = ExerciseVectorService(
            repository=repository,
            embedding_client=embedding_client,
            model_name="fireworks/qwen3-embedding-8b",
        )

        results = service.search_exercises(query_text="needs hashmap practice", limit=5)

        self.assertEqual(len(results), 1)
        embedding_client.embed.assert_called_once_with(
            model_name="fireworks/qwen3-embedding-8b",
            inputs=["needs hashmap practice"],
        )
        repository.search_exercises.assert_called_once_with(
            query_vector=[0.1, 0.2, 0.3],
            limit=5,
        )

    def test_upsert_exercises_noops_when_no_embedding(self):
        repository = MagicMock()
        repository.is_configured = True
        embedding_client = MagicMock()
        service = ExerciseVectorService(
            repository=repository,
            embedding_client=embedding_client,
            model_name="fireworks/qwen3-embedding-8b",
        )

        service.upsert_exercises(
            [
                ExerciseRecord(
                    exercise_id="exercise-1",
                    slug="two-sum",
                    title="Two Sum",
                    description="Add two numbers",
                    content="Read and print the sum",
                    difficulty="easy",
                    concept_slugs=["arrays"],
                )
            ]
        )

        repository.upsert_exercises.assert_called_once()


if __name__ == "__main__":
    unittest.main()
