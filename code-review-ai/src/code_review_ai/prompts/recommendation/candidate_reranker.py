from __future__ import annotations

from textwrap import dedent
from typing import Any


def build_candidate_reranker_system_prompt() -> str:
    return dedent(
        """
        You are a candidate reranker for CS1 exercise recommendation.

        Your job is to reorder already-valid candidate exercises after graph retrieval.
        Do not invent new exercise ids. Only rank ids that already exist in the input list.

        Return valid JSON only.
        """
    ).strip()


def build_candidate_reranker_prompt(
    *,
    assigned_path: str,
    anchor_concept: str,
    focus_concept_id: str,
    path_reason: str,
    critical_errors: int,
    latest_review_summary: str,
    candidates: list[dict[str, Any]],
) -> str:
    return dedent(
        f"""
        Re-rank the candidate exercises for this recommendation request.

        Assigned path: {assigned_path}
        Anchor concept: {anchor_concept}
        Focus concept: {focus_concept_id}
        Critical errors: {critical_errors}

        Path reason:
        {path_reason}

        Latest review summary:
        {latest_review_summary}

        Candidates:
        {candidates}

        Ranking guidance:
        - Prefer candidates that best fit the assigned path.
        - Prefer stronger graph alignment: recommended_weight, tests_weight, related_weight.
        - Use progression_score more strongly for harder or next-step style candidates.
        - Use similarity_score more strongly for reinforce or improve style candidates.
        - Keep the ranking pedagogically coherent; do not over-rank obvious outliers.

        Return JSON with:
        {{
          "exercise_ids": ["id1", "id2", "id3"],
          "reason": "short explanation"
        }}
        """
    ).strip()
