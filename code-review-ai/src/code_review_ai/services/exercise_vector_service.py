from __future__ import annotations

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.repositories.qdrant_repository import (
    QdrantRepository,
    QdrantSearchResult,
)
from code_review_ai.utils.fireworks_embedding_client import FireworksEmbeddingClient


class ExerciseVectorService:
    def __init__(
        self,
        *,
        repository: QdrantRepository,
        embedding_client: FireworksEmbeddingClient,
        model_name: str,
    ):
        self.repository = repository
        self.embedding_client = embedding_client
        self.model_name = model_name

    @property
    def is_enabled(self) -> bool:
        return self.repository.is_configured

    def upsert_exercises(self, exercises: list[ExerciseRecord]) -> None:
        self.repository.upsert_exercises(exercises)

    def search_exercises(
        self,
        *,
        query_text: str,
        limit: int,
    ) -> list[QdrantSearchResult]:
        if not self.is_enabled or not query_text.strip():
            return []

        query_vector = self.embedding_client.embed(
            model_name=self.model_name,
            inputs=[query_text],
        )[0]
        return self.repository.search_exercises(query_vector=query_vector, limit=limit)
