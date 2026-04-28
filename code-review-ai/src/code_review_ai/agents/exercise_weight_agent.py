import logging
from typing import Any

from openai import OpenAI

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import AssignedPath, ConceptRecord
from code_review_ai.prompts.knowledge_graph.exercise_concept_weight import (
    build_exercise_concept_weight_messages,
)
from code_review_ai.prompts.knowledge_graph.exercise_relation_weight import (
    build_exercise_relation_weight_messages,
)
from code_review_ai.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ExerciseWeightAgent:
    """Evaluates exercise-to-concept and exercise-to-exercise weights for CS1 graphs."""

    STRONG_WEIGHT_THRESHOLD = 0.85
    MEDIUM_WEIGHT_THRESHOLD = 0.5
    VALID_WEIGHTS = {1.0, 0.7, 0.3}
    DEFAULT_WEIGHT = 0.7
    VALID_PATHS: set[AssignedPath] = {"REINFORCE", "IMPROVE", "NEXT_CONCEPT"}
    DEFAULT_PATH: AssignedPath = "REINFORCE"
    VALID_RELATION_TYPES = {
        "SIMILAR_PRACTICE",
        "NEXT_STEP",
        "PREREQUISITE_REVIEW",
        "SAME_CONCEPT_HARDER",
        "SAME_CONCEPT_EASIER",
    }
    DEFAULT_RELATION_TYPE = "SIMILAR_PRACTICE"
    DEFAULT_RELATION_METADATA = {
        "weight": DEFAULT_WEIGHT,
        "relation_type": DEFAULT_RELATION_TYPE,
        "difficulty_gap": 0.0,
        "progression_score": DEFAULT_WEIGHT,
        "similarity_score": DEFAULT_WEIGHT,
    }

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.0,
        max_tokens: int = 1200,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

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

    def evaluate(
        self,
        *,
        main_exercise: ExerciseRecord,
        concepts: list[ConceptRecord],
        related_exercises: list[ExerciseRecord],
    ) -> tuple[
        dict[str, float],
        dict[str, list[dict[str, Any]]],
        dict[str, dict[str, Any]],
    ]:
        if not concepts and not related_exercises:
            return {}, {}, {}

        try:
            concept_weights: dict[str, float] = {}
            concept_paths: dict[str, list[dict[str, Any]]] = {}
            if concepts:
                concept_messages = build_exercise_concept_weight_messages(
                    main_exercise=main_exercise,
                    concepts=concepts,
                )
                concept_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=concept_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                concept_parsed = safe_parse_json_response(
                    concept_response.choices[0].message.content
                )
                concept_weights = {
                    str(row.get("concept_id")): self._normalize_concept_metadata(row)[
                        "weight"
                    ]
                    for row in concept_parsed.get("concepts", [])
                    if row.get("concept_id")
                }
                concept_paths = {
                    str(row.get("concept_id")): self._normalize_concept_metadata(row)[
                        "recommended_paths"
                    ]
                    for row in concept_parsed.get("concepts", [])
                    if row.get("concept_id")
                }

            related_metadata: dict[str, dict[str, Any]] = {}
            if related_exercises:
                related_messages = build_exercise_relation_weight_messages(
                    main_exercise=main_exercise,
                    concepts=concepts,
                    related_exercises=related_exercises,
                )
                related_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=related_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                related_parsed = safe_parse_json_response(
                    related_response.choices[0].message.content
                )
                related_metadata = {
                    str(row.get("exercise_id")): self._normalize_related_metadata(row)
                    for row in related_parsed.get("related_exercises", [])
                    if row.get("exercise_id")
                }
        except Exception:
            logger.exception(
                "ExerciseWeightAgent failed; falling back to default exercise weights"
            )
            concept_weights = {}
            concept_paths = {}
            related_metadata = {}

        return (
            {
                concept.concept_id: concept_weights.get(
                    concept.concept_id, self.DEFAULT_WEIGHT
                )
                for concept in concepts
            },
            {
                concept.concept_id: concept_paths.get(
                    concept.concept_id,
                    self._default_paths_for_weight(
                        concept_weights.get(concept.concept_id, self.DEFAULT_WEIGHT)
                    ),
                )
                for concept in concepts
            },
            {
                exercise.exercise_id: related_metadata.get(
                    exercise.exercise_id,
                    self._default_related_metadata(),
                )
                for exercise in related_exercises
            },
        )

    def _normalize_paths(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        normalized: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        for item in value:
            if not isinstance(item, dict):
                continue
            raw_path = str(item.get("path", "")).upper()
            if raw_path not in self.VALID_PATHS or raw_path in seen_paths:
                continue
            normalized.append(
                {
                    "path": raw_path,
                    "weight": self._normalize_weight(item.get("weight")),
                }
            )
            seen_paths.add(raw_path)
        return normalized

    def _normalize_concept_metadata(self, row: dict[str, Any]) -> dict[str, Any]:
        centrality_score = self._normalize_score(
            row.get("centrality_score"), default=self.DEFAULT_WEIGHT
        )
        solution_dependency_score = self._normalize_score(
            row.get("solution_dependency_score"), default=self.DEFAULT_WEIGHT
        )
        explicit_usage_score = self._normalize_score(
            row.get("explicit_usage_score"), default=self.DEFAULT_WEIGHT
        )
        difficulty_alignment_score = self._normalize_score(
            row.get("difficulty_alignment_score"), default=self.DEFAULT_WEIGHT
        )
        recommended_paths = self._normalize_paths(row.get("recommended_paths"))

        return {
            "weight": self._compute_concept_weight(
                centrality_score=centrality_score,
                solution_dependency_score=solution_dependency_score,
                explicit_usage_score=explicit_usage_score,
                difficulty_alignment_score=difficulty_alignment_score,
            ),
            "recommended_paths": recommended_paths,
        }

    def _default_paths_for_weight(self, weight: float) -> list[dict[str, Any]]:
        if weight >= 1.0:
            return [
                {"path": "REINFORCE", "weight": 1.0},
                {"path": "IMPROVE", "weight": 0.7},
            ]
        if weight >= 0.7:
            return [{"path": "IMPROVE", "weight": 0.7}]
        return [{"path": self.DEFAULT_PATH, "weight": self.DEFAULT_WEIGHT}]

    def _normalize_score(self, value: Any, default: float = 0.7) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return default
        return max(0.0, min(1.0, numeric))

    def _normalize_difficulty_gap(self, value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(-3.0, min(3.0, numeric))

    def _normalize_related_metadata(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        relation_type = str(row.get("relation_type", "")).upper()
        if relation_type not in self.VALID_RELATION_TYPES:
            relation_type = self.DEFAULT_RELATION_TYPE

        solution_pattern_score = self._normalize_score(
            row.get("solution_pattern_score"), default=self.DEFAULT_WEIGHT
        )
        difficulty_alignment_score = self._normalize_score(
            row.get("difficulty_alignment_score"), default=self.DEFAULT_WEIGHT
        )
        progression_score = self._normalize_score(
            row.get("progression_score"), default=self.DEFAULT_WEIGHT
        )
        similarity_score = self._normalize_score(
            row.get("similarity_score"), default=self.DEFAULT_WEIGHT
        )

        return {
            "weight": self._compute_related_weight(
                solution_pattern_score=solution_pattern_score,
                difficulty_alignment_score=difficulty_alignment_score,
                progression_score=progression_score,
                similarity_score=similarity_score,
                relation_type=relation_type,
            ),
            "relation_type": relation_type,
            "difficulty_gap": self._normalize_difficulty_gap(row.get("difficulty_gap")),
            "progression_score": progression_score,
            "similarity_score": similarity_score,
        }

    def _default_related_metadata(self) -> dict[str, Any]:
        return dict(self.DEFAULT_RELATION_METADATA)

    def _compute_related_weight(
        self,
        *,
        solution_pattern_score: float,
        difficulty_alignment_score: float,
        progression_score: float,
        similarity_score: float,
        relation_type: str,
    ) -> float:
        raw_weight = (
            0.35 * similarity_score
            + 0.30 * progression_score
            + 0.20 * solution_pattern_score
            + 0.15 * difficulty_alignment_score
        )

        if relation_type in {"NEXT_STEP", "SAME_CONCEPT_HARDER", "SAME_CONCEPT_EASIER"}:
            raw_weight += 0.05
        elif relation_type == "PREREQUISITE_REVIEW":
            raw_weight -= 0.05

        raw_weight = max(0.0, min(1.0, raw_weight))
        return self._normalize_weight(raw_weight)

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
        raw_weight = max(0.0, min(1.0, raw_weight))
        return self._normalize_weight(raw_weight)
