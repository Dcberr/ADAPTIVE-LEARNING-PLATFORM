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
        - HARDER
        - PREREQUISITE_REVIEW
        - TRANSFER

        Decision policy:
        - Treat this as a pedagogical diagnosis task, not a generic classification task.
        - Start from the anchor concept and latest review evidence.
        - Use history or graph blocks only if they are explicitly present in the prompt.
        - Give more weight to validated history than to weak intuition from one attempt.
        - When signals conflict, prefer the safer path unless strong evidence shows readiness.
        - Consider every validated block that appears: review trend, submission trend, student history, and exercise graph.

        Reasoning protocol:
        1. Identify the dominant risk on the current concept.
        2. Check whether recent history confirms or weakens that risk.
        3. Check whether student history suggests repeated exposure or unresolved instability.
        4. Use graph evidence to sanity-check concept fit and local recommendation strength.
        5. Decide whether the student needs prerequisite repair, easier reinforcement, same-level improvement, harder same-concept practice, or transfer-style variation.
        6. Pick a focus concept from the valid list only.
        7. Explain why the chosen path beats the strongest alternative.

        Path definitions:
        - PREREQUISITE_REVIEW: choose when the student appears blocked by missing foundations and should step down to prerequisite review.
        - REINFORCE: choose when the student should stay near the same concept but needs an easier or safer follow-up.
        - IMPROVE: choose when the student should stay on the same concept at a similar level for consolidation.
        - HARDER: choose when the student shows strong enough readiness for a more challenging same-concept exercise.
        - TRANSFER: choose when the student should stay on the same concept but practice it in a different problem form instead of just a harder variant.

        Output rules:
        - Base the answer only on evidence actually shown in the prompt.
        - Do not mention missing history or graph blocks as if they were known.
        - Keep the reason concise but evidence-based, and include the main competing path you rejected.

        Return valid JSON only.
        """
    ).strip()


def build_path_decider_prompt(
    *,
    anchor_concept: str,
    suggested_focus_concept: str,
    critical_errors: int,
    latest_review_summary: str,
    review_trend_summary: dict[str, Any] | None,
    submission_trend_summary: dict[str, Any] | None,
    student_history_summary: dict[str, Any] | None,
    exercise_graph: dict[str, Any] | None,
    valid_focus_concepts: list[str],
) -> str:
    evidence_blocks = [
        f"Anchor concept: {anchor_concept}",
        f"Suggested focus concept: {suggested_focus_concept}",
        f"Critical errors: {critical_errors}",
        "",
        "Latest review summary:",
        str(latest_review_summary),
    ]
    if review_trend_summary is not None:
        evidence_blocks.extend(
            [
                "",
                "Validated review trend:",
                str(review_trend_summary),
            ]
        )
    if submission_trend_summary is not None:
        evidence_blocks.extend(
            [
                "",
                "Validated submission trend:",
                str(submission_trend_summary),
            ]
        )
    if student_history_summary is not None:
        evidence_blocks.extend(
            [
                "",
                "Validated student history:",
                str(student_history_summary),
            ]
        )
    if exercise_graph is not None:
        evidence_blocks.extend(
            [
                "",
                "Exercise graph summary:",
                str(exercise_graph),
            ]
        )
    evidence_blocks.extend(
        [
            "",
            "Valid focus concepts:",
            str(valid_focus_concepts),
        ]
    )
    return dedent(
        f"""
        Choose the most appropriate next recommendation path.

        Evidence:
        {chr(10).join(evidence_blocks)}

        Decision checklist:
        1. What is the strongest current sign of instability or readiness?
        2. Which validated history block matters most, if any?
        3. Do the trend signals confirm the latest review or pull against it?
        4. Does student history suggest repeated exposure, recent assignment overlap, or persistent instability?
        5. Does the exercise graph support staying on the same concept strongly enough?
        6. Is the real need prerequisite repair, reinforcement, consolidation, harder progression, or transfer?
        7. Which focus concept is most defensible from the valid list?
        8. What is the main reason not to choose the strongest competing path?

        Return JSON with:
        {{
          "assigned_path": "REINFORCE|IMPROVE|HARDER|PREREQUISITE_REVIEW|TRANSFER",
          "focus_concept_id": "string",
          "confidence": 0.0,
          "risk_level": "high|medium|low",
          "readiness_level": "emerging|developing|ready",
          "reason": "string"
        }}
        """
    ).strip()
