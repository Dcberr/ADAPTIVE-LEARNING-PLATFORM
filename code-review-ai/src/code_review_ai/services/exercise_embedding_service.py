from __future__ import annotations

import hashlib

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.utils.fireworks_embedding_client import FireworksEmbeddingClient


class ExerciseEmbeddingService:
    def __init__(self, client: FireworksEmbeddingClient, model_name: str):
        self.client = client
        self.model_name = model_name

    def hydrate_exercises(self, exercises: list[ExerciseRecord]) -> list[ExerciseRecord]:
        if not exercises:
            return []

        hydrated = list(exercises)
        indexes_to_embed: list[int] = []
        inputs_to_embed: list[str] = []

        for index, exercise in enumerate(hydrated):
            content_hash = self.build_content_hash(exercise)
            needs_embedding = (
                not exercise.embedding
                or exercise.embedding_model != self.model_name
                or exercise.content_hash != content_hash
            )
            if not needs_embedding:
                continue
            indexes_to_embed.append(index)
            inputs_to_embed.append(self.build_embedding_text(exercise))

        if inputs_to_embed:
            embeddings = self.client.embed(
                model_name=self.model_name,
                inputs=inputs_to_embed,
            )
            if len(embeddings) != len(indexes_to_embed):
                raise RuntimeError(
                    "Fireworks embedding response count did not match exercise batch size."
                )
            for embedding, index in zip(embeddings, indexes_to_embed):
                exercise = hydrated[index]
                hydrated[index] = exercise.model_copy(
                    update={
                        "embedding": embedding,
                        "embedding_model": self.model_name,
                        "content_hash": self.build_content_hash(exercise),
                    }
                )

        return hydrated

    @staticmethod
    def build_embedding_text(exercise: ExerciseRecord) -> str:
        concepts = ", ".join(
            sorted({item.strip() for item in exercise.concept_slugs if item.strip()})
        )
        return "\n".join(
            [
                f"Title: {exercise.title.strip()}",
                f"Description: {exercise.description.strip()}",
                f"Concepts: {concepts}",
                f"Starter Code: {exercise.content.strip()}",
            ]
        )

    @staticmethod
    def build_content_hash(exercise: ExerciseRecord) -> str:
        payload = "||".join(
            [
                exercise.slug.strip(),
                exercise.title.strip(),
                exercise.description.strip(),
                exercise.content.strip(),
                exercise.difficulty.strip(),
                ",".join(
                    sorted(
                        concept_slug.strip()
                        for concept_slug in exercise.concept_slugs
                        if concept_slug.strip()
                    )
                ),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
