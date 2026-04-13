import logging
from typing import Any

from openai import OpenAI

from app.models.knowledge_graph import ConceptRecord
from app.utils.parse_json_response import safe_parse_json_response

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

        messages = [
            {
                "role": "system",
                "content": (
                    "You are labeling prerequisite strength for CS1 programming concepts. "
                    "For each prerequisite candidate, choose exactly one strength from 1.0, 0.6, or 0.3. "
                    "1.0 means hard prerequisite, 0.6 means strong supporting prerequisite, "
                    "0.3 means soft prerequisite. Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": f"""
Target concept:
{{
  "concept_id": "{main_concept.concept_id}",
  "name": "{main_concept.name}",
  "description": "{main_concept.description}",
  "difficulty": {main_concept.difficulty}
}}

Prerequisite candidates:
{[
    {
        "concept_id": concept.concept_id,
        "name": concept.name,
        "description": concept.description,
        "difficulty": concept.difficulty,
    }
    for concept in prerequisites
]}

Return JSON in exactly this shape:
{{
  "prerequisites": [
    {{
      "concept_id": "string",
      "strength": 1.0,
      "reason": "short explanation"
    }}
  ]
}}

Rules:
- Only use concept_ids from the provided prerequisite candidates.
- Use 1.0 when the target concept usually depends directly on the prerequisite.
- Use 0.6 when the prerequisite is strongly helpful but not strictly required.
- Use 0.3 when the prerequisite is useful background only.
- Return one item for every provided prerequisite candidate.
                """,
            },
        ]

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
