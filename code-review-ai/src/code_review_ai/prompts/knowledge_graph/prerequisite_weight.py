from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.knowledge_graph import ConceptRecord


def build_prerequisite_weight_messages(
    main_concept: ConceptRecord,
    prerequisites: list[ConceptRecord],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are labeling prerequisite strength for CS1 programming concepts.

                For each prerequisite candidate, choose exactly one strength from:
                - 1.0 = hard prerequisite
                - 0.6 = strong supporting prerequisite
                - 0.3 = soft prerequisite

                Return valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
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
                """
            ).strip(),
        },
    ]
