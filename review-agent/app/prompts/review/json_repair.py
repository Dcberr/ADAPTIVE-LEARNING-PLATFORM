from __future__ import annotations

from textwrap import dedent


def build_review_json_repair_system_prompt() -> str:
    return dedent(
        """
        You repair model output into valid JSON for the review flow.

        Output rules:
        - Return exactly one JSON object.
        - Do not return markdown.
        - Do not return code fences.
        - Do not return comments.
        - Do not return any explanation before or after the JSON object.
        - Preserve the original meaning when possible.
        - If the original text is incomplete, repair it conservatively into the closest valid JSON object.
        """
    ).strip()


def build_review_json_repair_prompt(raw_response: str) -> str:
    return dedent(
        f"""
        Convert the following review-agent output into a single valid JSON object.

        Raw model output:
        {raw_response}
        """
    ).strip()
