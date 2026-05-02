from __future__ import annotations

import math
import re
from typing import Any

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord


class ExerciseRelationScoringService:
    """Deterministic scorer for exercise-concept and exercise-exercise graph edges."""

    STRONG_WEIGHT_THRESHOLD = 0.85
    MEDIUM_WEIGHT_THRESHOLD = 0.5
    DEFAULT_WEIGHT = 0.7
    DEFAULT_RELATION_METADATA = {
        "weight": DEFAULT_WEIGHT,
        "difficulty_gap": 0.0,
        "progression_score": DEFAULT_WEIGHT,
        "similarity_score": DEFAULT_WEIGHT,
    }

    def evaluate(
        self,
        *,
        main_exercise: ExerciseRecord,
        concepts: list[ConceptRecord],
        related_exercises: list[ExerciseRecord],
        main_concept_slugs: list[str] | None = None,
        related_concept_slugs_by_exercise: dict[str, list[str]] | None = None,
    ) -> tuple[
        dict[str, float],
        dict[str, float],
        dict[str, dict[str, Any]],
    ]:
        if not concepts and not related_exercises:
            return {}, {}, {}

        concept_weights = {
            concept.concept_id: self._score_concept_weight(
                main_exercise=main_exercise,
                concept=concept,
            )
            for concept in concepts
        }
        recommended_weights = {
            concept.concept_id: self._score_recommended_weight(
                concept=concept,
                concept_weight=concept_weights[concept.concept_id],
                main_exercise=main_exercise,
            )
            for concept in concepts
        }
        related_metadata = {
            exercise.exercise_id: self._score_related_exercise_pair(
                main_exercise=main_exercise,
                related_exercise=exercise,
                main_concept_slugs=self._resolved_main_concept_slugs(
                    concepts=concepts,
                    main_concept_slugs=main_concept_slugs,
                ),
                related_concept_slugs=(related_concept_slugs_by_exercise or {}).get(
                    exercise.exercise_id,
                    [],
                ),
            )
            for exercise in related_exercises
        }

        return (
            {concept.concept_id: concept_weights[concept.concept_id] for concept in concepts},
            {
                concept.concept_id: recommended_weights[concept.concept_id]
                for concept in concepts
            },
            {
                exercise.exercise_id: related_metadata[exercise.exercise_id]
                for exercise in related_exercises
            },
        )

    def evaluate_exercise_concepts(
        self,
        *,
        main_exercise: ExerciseRecord,
        concepts: list[ConceptRecord],
    ) -> tuple[dict[str, float], dict[str, float]]:
        concept_weights = {
            concept.concept_id: self._score_concept_weight(
                main_exercise=main_exercise,
                concept=concept,
            )
            for concept in concepts
        }
        recommended_weights = {
            concept.concept_id: self._score_recommended_weight(
                concept=concept,
                concept_weight=concept_weights[concept.concept_id],
                main_exercise=main_exercise,
            )
            for concept in concepts
        }
        return concept_weights, recommended_weights

    def _normalize_weight(self, value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return self.DEFAULT_WEIGHT

        if numeric >= self.STRONG_WEIGHT_THRESHOLD:
            return 1.0
        if numeric >= self.MEDIUM_WEIGHT_THRESHOLD:
            return 0.7
        return 0.3

    def _score_recommended_weight(
        self,
        *,
        concept: ConceptRecord,
        concept_weight: float,
        main_exercise: ExerciseRecord,
    ) -> float:
        return self._score_concept_weight(
            main_exercise=main_exercise,
            concept=concept,
        ) if concept_weight <= 0 else concept_weight

    def _compute_related_weight(
        self,
        *,
        solution_pattern_score: float,
        difficulty_alignment_score: float,
        progression_score: float,
        similarity_score: float,
        relation_bonus: float = 0.0,
    ) -> float:
        raw_weight = (
            0.35 * similarity_score
            + 0.30 * progression_score
            + 0.20 * solution_pattern_score
            + 0.15 * difficulty_alignment_score
        )
        raw_weight += relation_bonus
        return self._normalize_weight(max(0.0, min(1.0, raw_weight)))

    def _score_related_exercise_pair(
        self,
        *,
        main_exercise: ExerciseRecord,
        related_exercise: ExerciseRecord,
        main_concept_slugs: list[str],
        related_concept_slugs: list[str],
    ) -> dict[str, Any]:
        concept_overlap = self._jaccard_similarity(
            {
                concept_slug.strip().lower()
                for concept_slug in main_concept_slugs
                if concept_slug.strip()
            },
            {
                concept_slug.strip().lower()
                for concept_slug in related_concept_slugs
                if concept_slug.strip()
            },
        )
        text_overlap = self._jaccard_similarity(
            self._tokenize_exercise(main_exercise),
            self._tokenize_exercise(related_exercise),
        )
        difficulty_gap = self._difficulty_gap(main_exercise, related_exercise)
        difficulty_alignment_score = self._difficulty_alignment_score(difficulty_gap)
        embedding_similarity = self._cosine_similarity(
            main_exercise.embedding,
            related_exercise.embedding,
        )
        solution_pattern_score = self._clamp_score(
            0.55 * embedding_similarity + 0.45 * concept_overlap
        )
        similarity_score = self._clamp_score(
            0.45 * embedding_similarity
            + 0.35 * concept_overlap
            + 0.10 * text_overlap
        )
        progression_fit = self._progression_fit(difficulty_gap)
        progression_score = self._clamp_score(
            0.40 * concept_overlap
            + 0.30 * progression_fit
            + 0.20 * difficulty_alignment_score
            + 0.10 * embedding_similarity
        )
        return {
            "weight": self._compute_related_weight(
                solution_pattern_score=solution_pattern_score,
                difficulty_alignment_score=difficulty_alignment_score,
                progression_score=progression_score,
                similarity_score=similarity_score,
                relation_bonus=self._related_weight_adjustment(
                    concept_overlap=concept_overlap,
                    difficulty_gap=difficulty_gap,
                    progression_score=progression_score,
                    similarity_score=similarity_score,
                ),
            ),
            "difficulty_gap": difficulty_gap,
            "progression_score": progression_score,
            "similarity_score": similarity_score,
        }

    def _resolved_main_concept_slugs(
        self,
        *,
        concepts: list[ConceptRecord],
        main_concept_slugs: list[str] | None,
    ) -> list[str]:
        if main_concept_slugs is not None:
            return [
                concept_slug.strip()
                for concept_slug in main_concept_slugs
                if concept_slug.strip()
            ]
        return [
            (concept.slug or concept.concept_id).strip()
            for concept in concepts
            if (concept.slug or concept.concept_id).strip()
        ]

    @staticmethod
    def _tokenize_exercise(exercise: ExerciseRecord) -> set[str]:
        parts = [exercise.slug, exercise.title, exercise.description]
        return {
            token
            for part in parts
            for token in re.findall(r"[a-z0-9]+", part.lower())
            if len(token) >= 3
        }

    @staticmethod
    def _jaccard_similarity(left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        union = left | right
        if not union:
            return 0.0
        return len(left & right) / len(union)

    @staticmethod
    def _difficulty_level(exercise: ExerciseRecord) -> float:
        return {
            "easy": 1.0,
            "medium": 2.0,
            "hard": 3.0,
        }.get(exercise.difficulty.strip().lower(), 2.0)

    def _difficulty_gap(
        self,
        main_exercise: ExerciseRecord,
        related_exercise: ExerciseRecord,
    ) -> float:
        return max(
            -3.0,
            min(
                3.0,
                self._difficulty_level(related_exercise)
                - self._difficulty_level(main_exercise),
            ),
        )

    @staticmethod
    def _difficulty_alignment_score(difficulty_gap: float) -> float:
        return max(0.0, 1.0 - min(abs(difficulty_gap), 2.0) / 2.0)

    @staticmethod
    def _progression_fit(difficulty_gap: float) -> float:
        if difficulty_gap == 1.0:
            return 1.0
        if difficulty_gap == 0.0:
            return 0.7
        if difficulty_gap == -1.0:
            return 0.4
        return 0.2

    @staticmethod
    def _clamp_score(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot_product = sum(
            left_value * right_value for left_value, right_value in zip(left, right)
        )
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        cosine = dot_product / (left_norm * right_norm)
        return max(0.0, min(1.0, (cosine + 1.0) / 2.0))

    @staticmethod
    def _related_weight_adjustment(
        *,
        concept_overlap: float,
        difficulty_gap: float,
        progression_score: float,
        similarity_score: float,
    ) -> float:
        if concept_overlap >= 0.6 and difficulty_gap >= 1.0:
            return 0.05
        if concept_overlap >= 0.6 and difficulty_gap <= -1.0:
            return 0.05
        if progression_score >= 0.72 and difficulty_gap > 0.0:
            return 0.05
        if progression_score >= 0.58 and difficulty_gap < 0.0:
            return -0.05
        if similarity_score >= 0.7:
            return 0.0
        return 0.0

    def _score_concept_weight(
        self,
        *,
        main_exercise: ExerciseRecord,
        concept: ConceptRecord,
    ) -> float:
        exercise_tokens = self._exercise_text_tokens(main_exercise)
        concept_tokens = self._concept_tokens(concept)
        centrality_score = self._jaccard_similarity(exercise_tokens, concept_tokens)
        title_overlap = self._jaccard_similarity(
            self._tokens(main_exercise.title),
            concept_tokens,
        )
        declared_concept_overlap = 1.0 if concept.slug in main_exercise.concept_slugs else 0.0
        solution_dependency_score = self._clamp_score(
            0.45 * centrality_score
            + 0.25 * title_overlap
            + 0.30 * declared_concept_overlap
        )
        explicit_usage_score = self._clamp_score(
            0.45 * centrality_score
            + 0.35 * declared_concept_overlap
            + 0.20 * title_overlap
        )
        difficulty_alignment_score = self._clamp_score(
            1.0
            - min(
                abs(self._difficulty_level(main_exercise) - float(concept.difficulty)),
                2.0,
            )
            / 2.0
        )
        return self._compute_concept_weight(
            centrality_score=centrality_score,
            solution_dependency_score=solution_dependency_score,
            explicit_usage_score=explicit_usage_score,
            difficulty_alignment_score=difficulty_alignment_score,
        )

    def _compute_concept_weight(
        self,
        *,
        centrality_score: float,
        solution_dependency_score: float,
        explicit_usage_score: float,
        difficulty_alignment_score: float,
    ) -> float:
        raw_weight = (
            0.35 * centrality_score
            + 0.30 * solution_dependency_score
            + 0.20 * explicit_usage_score
            + 0.15 * difficulty_alignment_score
        )
        return self._normalize_weight(max(0.0, min(1.0, raw_weight)))

    @staticmethod
    def _exercise_text_tokens(exercise: ExerciseRecord) -> set[str]:
        return ExerciseRelationScoringService._tokens(
            " ".join(
                [
                    exercise.slug,
                    exercise.title,
                    exercise.description,
                    exercise.content,
                ]
            )
        )

    @staticmethod
    def _concept_tokens(concept: ConceptRecord) -> set[str]:
        return ExerciseRelationScoringService._tokens(
            f"{concept.slug} {concept.name} {concept.description}"
        )

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) >= 3
        }
