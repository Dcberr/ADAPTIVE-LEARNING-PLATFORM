import logging
from typing import Any

from openai import OpenAI

from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath, ConceptRecord
from app.prompts.knowledge_graph.exercise_weight import (
    build_exercise_weight_messages,
)
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ExerciseWeightAgent:
    """Evaluates exercise-to-concept and exercise-to-exercise weights for CS1 graphs."""

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
        "target_concept_id": "",
        "shared_concept_ids": [],
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

        if numeric >= 0.85:
            return 1.0
        if numeric >= 0.5:
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

        messages = build_exercise_weight_messages(
            main_exercise=main_exercise,
            concepts=concepts,
            related_exercises=related_exercises,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            concept_weights = {
                str(row.get("concept_id")): self._normalize_weight(row.get("weight"))
                for row in parsed.get("concepts", [])
                if row.get("concept_id")
            }
            concept_paths = {
                str(row.get("concept_id")): self._normalize_paths(
                    row.get("recommended_paths")
                )
                for row in parsed.get("concepts", [])
                if row.get("concept_id")
            }
            related_metadata = {
                str(row.get("exercise_id")): self._normalize_related_metadata(
                    row,
                    allowed_concept_ids={concept.concept_id for concept in concepts},
                )
                for row in parsed.get("related_exercises", [])
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
        *,
        allowed_concept_ids: set[str],
    ) -> dict[str, Any]:
        relation_type = str(row.get("relation_type", "")).upper()
        if relation_type not in self.VALID_RELATION_TYPES:
            relation_type = self.DEFAULT_RELATION_TYPE

        target_concept_id = str(row.get("target_concept_id", ""))
        if target_concept_id not in allowed_concept_ids:
            target_concept_id = ""

        shared_concept_ids = [
            concept_id
            for concept_id in (row.get("shared_concept_ids") or [])
            if isinstance(concept_id, str) and concept_id in allowed_concept_ids
        ]

        deduped_shared_concepts: list[str] = []
        seen: set[str] = set()
        for concept_id in shared_concept_ids:
            if concept_id in seen:
                continue
            deduped_shared_concepts.append(concept_id)
            seen.add(concept_id)

        return {
            "weight": self._normalize_weight(row.get("weight")),
            "relation_type": relation_type,
            "target_concept_id": target_concept_id,
            "shared_concept_ids": deduped_shared_concepts,
            "difficulty_gap": self._normalize_difficulty_gap(row.get("difficulty_gap")),
            "progression_score": self._normalize_score(
                row.get("progression_score"), default=self.DEFAULT_WEIGHT
            ),
            "similarity_score": self._normalize_score(
                row.get("similarity_score"), default=self.DEFAULT_WEIGHT
            ),
        }

    def _default_related_metadata(self) -> dict[str, Any]:
        return dict(self.DEFAULT_RELATION_METADATA)
