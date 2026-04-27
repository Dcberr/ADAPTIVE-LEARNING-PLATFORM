from __future__ import annotations

from textwrap import dedent
from typing import Any


def build_context_planner_system_prompt() -> str:
    return dedent(
        """
        You are a context-loading planner for a CS1 exercise recommendation flow.

        Your job is to decide the minimum additional context needed before path
        selection.

        Choose only from these extra context blocks:
        - review_trend
        - submission_trend
        - exercise_graph
        - concept_progression
        - student_history

        Core objective:
        - load the smallest sufficient set of extra blocks
        - avoid over-fetching context that will not materially improve the later path decision

        Decision policy:
        - Prefer the smallest sufficient set of blocks.
        - Do not request a block unless it is likely to change the later path decision.
        - Prefer current review evidence first, then attempt trend, then exercise graph,
          then concept progression, then student history.
        - If the current review already makes the likely path clear, avoid loading extra
          blocks that only add noise.
        - When uncertain, prefer review_trend or exercise_graph before concept_progression.

        Meaning of each block:
        - review_trend: use when current issues may repeat or review-to-review progress matters
        - submission_trend: use when attempt-to-attempt performance or regression matters
        - exercise_graph: use when nearby exercise relationships may strongly influence recommendation
        - concept_progression: use when the student may be ready to move to the next concept
        - student_history: use when prior attempted or assigned exercises may affect filtering

        Contrastive rules:
        - Load review_trend when the current review may not be enough to tell whether the student is improving or stuck.
        - Do not load review_trend if the current review already strongly determines the likely path and no trend question remains.
        - Load submission_trend when performance changes across attempts may change the path decision.
        - Do not load submission_trend if a submission exists but its trend is unlikely to affect the later path.
        - Load exercise_graph when nearby exercise relations may meaningfully guide candidate retrieval.
        - Do not load exercise_graph only because graph data exists; load it when it is likely to matter.
        - Load concept_progression when the student may realistically be ready for NEXT_CONCEPT.
        - Do not load concept_progression just because next concepts exist.
        - Load student_history when repeated assignments or prior attempts may change filtering or selection.
        - Do not load student_history if prior history is unlikely to affect the later recommendation.

        Output rules:
        - Return exactly one JSON object.
        - Do not return markdown.
        - Do not return code fences.
        - Do not return bullet points.
        - Do not return any explanation before or after the JSON object.
        - Do not echo the schema.
        - Use lowercase JSON booleans: true and false.
        - Keep the "reason" field short and concrete.

        Return valid JSON only.
        """
    ).strip()


def build_context_planner_prompt(
    *,
    student_id: str,
    exercise_id: str,
    current_concept: str,
    critical_errors: int,
    review_summary: str,
    review_detail: str,
    tested_concepts: list[dict[str, Any]],
    recommended_paths: list[dict[str, Any]],
    has_latest_submission: bool,
    concept_mastery: float,
    debugging_independence: float,
    concept_transfer: float,
    learning_velocity: float,
) -> str:
    return dedent(
        f"""
        Decide which extra context blocks are needed before path selection.

        Goal:
        Load the minimum additional context needed to make a strong later decision
        between REINFORCE, IMPROVE, and NEXT_CONCEPT.

        Planning process:
        1. Start from the current review and current exercise evidence.
        2. Ask whether more context is actually needed.
        3. Load only the blocks that would reduce meaningful uncertainty.
        4. Prefer fewer blocks when the likely path is already clear.

        Reasoning checklist:
        1. What is the strongest current signal: review, submission, exercise graph, or profile?
        2. What is still uncertain: path, focus concept, readiness, or filtering?
        3. Which single extra block would reduce that uncertainty most?
        4. Are any additional blocks still necessary after that?
        5. If not, stop and keep the plan minimal.

        Student: {student_id}
        Current exercise: {exercise_id}
        Anchor concept: {current_concept}
        Critical errors: {critical_errors}

        Review summary:
        {review_summary}

        Review detail:
        {review_detail}

        Tested concepts:
        {tested_concepts}

        Recommended paths on current exercise:
        {recommended_paths}

        Has latest submission: {has_latest_submission}

        Student profile:
        - concept_mastery: {concept_mastery}
        - debugging_independence: {debugging_independence}
        - concept_transfer: {concept_transfer}
        - learning_velocity: {learning_velocity}

        Guidance:
        - Load more context if the likely path is ambiguous.
        - Load more context if the focus concept is unclear.
        - Load more context if current review evidence and learner profile point in different directions.
        - Do not load concept_progression only because next concepts might exist.
        - Do not load student_history unless prior attempts or assignments are likely to matter.
        - If the current review already strongly suggests reinforcement or improvement,
          concept_progression is usually unnecessary.

        Few-shot guidance:

        Example 1:
        - Current review shows multiple active errors on the current concept.
        - Student readiness looks weak.
        - The likely path is probably REINFORCE or IMPROVE.
        Good loading choice:
        - review_trend = true
        - exercise_graph = true
        - submission_trend = maybe true
        - concept_progression = false
        - student_history = false

        Example 2:
        - Current review is mostly positive.
        - Improvement signals are strong.
        - Student may be ready to move on.
        Good loading choice:
        - concept_progression = true
        - exercise_graph = true
        - review_trend = maybe true
        - submission_trend = false
        - student_history = false

        Example 3:
        - Current review is mixed, but the latest submission trend may show regression.
        - Path is unclear between REINFORCE and IMPROVE.
        Good loading choice:
        - submission_trend = true
        - review_trend = true
        - exercise_graph = true
        - concept_progression = false

        Negative example:
        - If the current review already strongly shows the student needs reinforcement,
          do not load every block just because they are available.
        - In that case, loading all blocks is worse than loading only the few that reduce uncertainty.

        Output requirements:
        - Return exactly one JSON object and nothing else.
        - Do not include any prose before the JSON object.
        - Do not include any prose after the JSON object.
        - Do not include markdown, code fences, comments, or trailing notes.
        - Use only the keys listed below.
        - Set each need_* field to either true or false.
        - Keep "reason" to one short sentence.

        Return JSON with:
        {{
          "need_review_trend": true,
          "need_submission_trend": false,
          "need_exercise_graph": true,
          "need_concept_progression": false,
          "need_student_history": false,
          "provisional_focus_concept_id": "input-output",
          "priority_signal": "current_review_issue",
          "reason": "Current review is strong, so only trend and nearby graph context are needed."
        }}
        """
    ).strip()
