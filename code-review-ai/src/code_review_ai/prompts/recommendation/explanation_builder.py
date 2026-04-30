from __future__ import annotations

from textwrap import dedent


def build_explanation_builder_system_prompt() -> str:
    return dedent(
        """
        You are a CS1 recommendation explainer.

        Use only the provided refs.
        Write `reasoning_content` and `roadmap_summary_content` with placeholders like {ref_id}.
        Return valid JSON only.
        """
    ).strip()


def build_explanation_builder_prompt(
    *,
    assigned_path: str,
    focus_concept_id: str,
    path_reason: str,
    selected_exercises: list[dict[str, str]],
    refs: list[dict[str, str]],
) -> str:
    return dedent(
        f"""
        Explain the roadmap using only the provided refs.

        Assigned path: {assigned_path}
        Focus concept: {focus_concept_id}

        Path reason:
        {path_reason}

        Selected exercises:
        {selected_exercises}

        Available refs:
        {refs}

        Return JSON with:
        {{
          "reasoning_content": "text with {{ref_id}}",
          "reasoning_ref_ids": ["ref_1"],
          "roadmap_summary_content": "text with {{ref_id}}",
          "roadmap_summary_ref_ids": ["ref_2"]
        }}
        """
    ).strip()
