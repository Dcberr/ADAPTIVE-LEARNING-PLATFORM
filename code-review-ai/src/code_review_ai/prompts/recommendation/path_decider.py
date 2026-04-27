from __future__ import annotations

from textwrap import dedent
from typing import Any


def build_path_decider_system_prompt() -> str:
    return dedent(
        """
        You are a CS1 recommendation path decider.

        Choose one assigned_path from:
        - REINFORCE
        - IMPROVE
        - NEXT_CONCEPT

        Return valid JSON only.
        """
    ).strip()


def build_path_decider_prompt(
    *,
    anchor_concept: str,
    suggested_focus_concept: str,
    critical_errors: int,
    latest_review_summary: str,
    latest_review_improvement_signal: float,
    latest_review_severity_change: float,
    latest_submission_improvement_ratio: float,
    latest_submission_regression_ratio: float,
    exercise_graph: dict[str, Any],
    concept_progression: list[dict[str, Any]],
    student_profile: dict[str, Any],
    valid_focus_concepts: list[str],
) -> str:
    return dedent(
        f"""
        Choose the most appropriate next recommendation path.

        Anchor concept: {anchor_concept}
        Suggested focus concept: {suggested_focus_concept}
        Critical errors: {critical_errors}

        Latest review summary:
        {latest_review_summary}

        Review trend:
        - improvement_signal: {latest_review_improvement_signal}
        - severity_change: {latest_review_severity_change}

        Submission trend:
        - improvement_ratio: {latest_submission_improvement_ratio}
        - regression_ratio: {latest_submission_regression_ratio}

        Exercise graph summary:
        {exercise_graph}

        Next concept candidates:
        {concept_progression}

        Student profile:
        {student_profile}

        Valid focus concepts:
        {valid_focus_concepts}

        Return JSON with:
        {{
          "assigned_path": "REINFORCE|IMPROVE|NEXT_CONCEPT",
          "focus_concept_id": "string",
          "confidence": 0.0,
          "risk_level": "high|medium|low",
          "readiness_level": "emerging|developing|ready",
          "reason": "string"
        }}
        """
    ).strip()
