import logging
from typing import Any

from openai import OpenAI

from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.prompts.knowledge_graph.prerequisite_weight import (
    build_prerequisite_weight_messages,
)
from code_review_ai.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class PrerequisiteWeightAgent:
    """Evaluates prerequisite strength between a main concept and prerequisite concepts."""

    VALID_STRENGTHS = {1.0, 0.6, 0.3}
    DEFAULT_STRENGTH = 0.6

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.1,
        max_tokens: int = 1200,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _normalize_strength(self, value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return self.DEFAULT_STRENGTH

        if numeric >= 0.8:
            return 1.0
        if numeric >= 0.45:
            return 0.6
        return 0.3

    def evaluate(
        self,
        *,
        main_concept: ConceptRecord,
        prerequisites: list[ConceptRecord],
    ) -> dict[str, float]:
        if not prerequisites:
            return {}

        messages = build_prerequisite_weight_messages(main_concept, prerequisites)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            rows = parsed.get("prerequisites", [])
            strengths = {
                str(row.get("concept_id")): self._normalize_strength(row.get("strength"))
                for row in rows
                if row.get("concept_id")
            }
        except Exception:
            logger.exception("PrerequisiteWeightAgent failed; falling back to default strengths")
            strengths = {}

        return {
            concept.concept_id: strengths.get(concept.concept_id, self.DEFAULT_STRENGTH)
            for concept in prerequisites
        }
