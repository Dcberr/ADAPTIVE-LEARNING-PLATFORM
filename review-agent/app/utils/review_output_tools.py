from __future__ import annotations

from typing import Any

from app.prompts.review.json_repair import (
    build_review_json_repair_prompt,
    build_review_json_repair_system_prompt,
)
from app.utils.parse_json_response import safe_parse_json_response


def parse_review_json_with_repair(
    *,
    client: Any,
    model_name: str,
    raw_response: str,
    expected_shape: dict[str, type],
    repair_max_tokens: int = 600,
) -> dict[str, Any]:
    parsed = safe_parse_json_response(raw_response)
    if _matches_expected_shape(parsed, expected_shape):
        return parsed

    repaired_response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": build_review_json_repair_system_prompt(),
            },
            {
                "role": "user",
                "content": build_review_json_repair_prompt(raw_response),
            },
        ],
        temperature=0.0,
        max_tokens=repair_max_tokens,
    )
    repaired_text = repaired_response.choices[0].message.content
    repaired = safe_parse_json_response(repaired_text)
    return repaired if _matches_expected_shape(repaired, expected_shape) else parsed


def _matches_expected_shape(
    parsed: dict[str, Any],
    expected_shape: dict[str, type],
) -> bool:
    for key, expected_type in expected_shape.items():
        value = parsed.get(key)
        if not isinstance(value, expected_type):
            return False
    return True
