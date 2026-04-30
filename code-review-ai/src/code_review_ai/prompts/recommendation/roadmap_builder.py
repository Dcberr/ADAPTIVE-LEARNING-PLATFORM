from __future__ import annotations

from textwrap import dedent
from typing import Any


def build_roadmap_builder_system_prompt() -> str:
    return dedent(
        """
        You are a CS1 roadmap selector.

        Choose the most important exercises from the provided candidate list.
        Return valid JSON only.
        """
    ).strip()


def build_roadmap_builder_prompt(
    *,
    assigned_path: str,
    focus_concept_id: str,
    path_reason: str,
    candidates: list[dict[str, Any]],
) -> str:
    return dedent(
        f"""
        Select up to 3 exercises for the roadmap in order.

        Assigned path: {assigned_path}
        Focus concept: {focus_concept_id}

        Path reason:
        {path_reason}

        Candidates:
        {candidates}

        Return JSON with:
        {{
          "exercise_ids": ["id1", "id2"],
          "directives": ["step 1 directive", "step 2 directive"]
        }}
        """
    ).strip()
