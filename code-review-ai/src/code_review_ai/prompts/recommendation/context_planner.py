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
        - student_history

        Core objective:
        - load the smallest sufficient set of extra blocks
        - avoid over-fetching context that will not materially improve the later path decision

        Planner mindset:
        - Think like a diagnostic planner, not a general summarizer.
        - First form a provisional learner-state hypothesis from the current review.
        - Then identify the exact uncertainty that could still flip the path decision.
        - Then request only the cheapest context block that would resolve that uncertainty.
        - Stop requesting blocks once the likely path is stable enough.

        Decision policy:
        - Prefer the smallest sufficient set of blocks.
        - Do not request a block unless it is likely to change the later path decision.
        - Prefer current review evidence first, then attempt trend, then exercise graph,
          then student history.
        - If the current review already makes the likely path clear, avoid loading extra
          blocks that only add noise.
        - When uncertain, prefer review_trend or exercise_graph before student_history.

        Meaning of each block:
        - review_trend: use when current issues may repeat or review-to-review progress matters
        - submission_trend: use when attempt-to-attempt performance or regression matters
        - exercise_graph: use when nearby exercise relationships may strongly influence recommendation
        - student_history: use when prior attempted or assigned exercises may affect filtering

        Diagnostic questions to answer before choosing blocks:
        - Is the current review already decisive for one of REINFORCE, IMPROVE, HARDER, PREREQUISITE_REVIEW, or TRANSFER?
        - Is the uncertainty about learner stability, recent direction of change, or candidate availability?
        - Would more history genuinely change the path, or only add confidence without changing action?
        - Is the remaining uncertainty pedagogical, retrieval-related, or filtering-related?

        Contrastive rules:
        - Load review_trend when the current review may not be enough to tell whether the student is improving or stuck.
        - Do not load review_trend if the current review already strongly determines the likely path and no trend question remains.
        - Load submission_trend when performance changes across attempts may change the path decision.
        - Do not load submission_trend if a submission exists but its trend is unlikely to affect the later path.
        - Load exercise_graph when nearby exercise relations may meaningfully guide candidate retrieval.
        - Do not load exercise_graph only because graph data exists; load it when it is likely to matter.
        - Load student_history when repeated assignments or prior attempts may change filtering or selection.
        - Do not load student_history if prior history is unlikely to affect the later recommendation.

        Uncertainty mapping:
        - If the main uncertainty is "is the learner getting better or staying stuck?", prefer review_trend.
        - If the main uncertainty is "was the latest attempt an outlier or part of a regression pattern?", prefer submission_trend.
        - If the main uncertainty is "which same-concept candidates are locally appropriate?", prefer exercise_graph.
        - If the main uncertainty is "will retrieval be distorted by repeat exposure or prior assignment?", prefer student_history.

        Escalation rules:
        - Request one block first when one block clearly dominates the uncertainty.
        - Request multiple blocks only when a single block would still leave the path materially ambiguous.
        - Avoid loading student_history as a default safety blanket.
        - Avoid loading all blocks unless there are multiple independent uncertainties.

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
    recommended_concepts: list[dict[str, Any]],
    has_latest_submission: bool,
) -> str:
    return dedent(
        f"""
        Decide which extra context blocks are needed before path selection.

        Goal:
        Load the minimum additional context needed to make a strong later decision
        between REINFORCE, IMPROVE, HARDER, PREREQUISITE_REVIEW, and TRANSFER.

        Planning process:
        1. Start from the current review and current exercise evidence.
        2. Form a provisional learner-state hypothesis.
        3. Ask whether more context is actually needed.
        4. Name the main uncertainty that could still change the path.
        5. Load only the blocks that would reduce that uncertainty.
        6. Prefer fewer blocks when the likely path is already clear.

        Diagnostic checklist:
        1. What does the current review imply right now: prerequisite review, reinforce, improve, harder, transfer, or unclear?
        2. Is the current issue about correctness instability, conceptual confusion, or candidate-fit uncertainty?
        3. Could recent trend overturn the current impression?
        4. Could prior attempts or assignments distort candidate filtering?
        5. Which single block would resolve the biggest remaining uncertainty?
        6. Would a second block still change the likely action, or only make you feel more certain?
        7. If not, stop and keep the plan minimal.

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

        Recommended concept links on current exercise:
        {recommended_concepts}

        Has latest submission: {has_latest_submission}

        Guidance:
        - Load more context if the likely path is ambiguous.
        - Load more context if the focus concept is unclear.
        - Load more context if current review evidence and recent graph history point in different directions.
        - Load more context if the current review is noisy enough that one bad attempt may be misleading.
        - Prefer explaining the uncertainty you are trying to resolve, not just naming blocks mechanically.
        - Do not load student_history unless prior attempts or assignments are likely to matter.
        - If the current review already strongly suggests reinforcement or improvement,
          extra history is usually unnecessary.

        Few-shot guidance:

        Example 1:
        - Current review shows multiple active errors on the current concept.
        - Student readiness looks weak.
        - The likely path is probably PREREQUISITE_REVIEW, REINFORCE, or IMPROVE.
        - Main uncertainty: is this persistent instability or just one rough attempt?
        Good loading choice:
        - review_trend = true
        - exercise_graph = true
        - submission_trend = maybe true
        - student_history = false

        Example 2:
        - Current review is mostly positive, but candidate ordering may still matter.
        - Improvement signals are strong.
        - The remaining question is whether same-concept practice is still needed.
        - Main uncertainty: not path volatility, but neighborhood quality for same-concept follow-up.
        Good loading choice:
        - exercise_graph = true
        - review_trend = maybe true
        - submission_trend = false
        - student_history = false

        Example 3:
        - Current review is mixed, but the latest submission trend may show regression.
        - Path is unclear between REINFORCE, IMPROVE, and PREREQUISITE_REVIEW.
        - Main uncertainty: whether the learner is recovering or sliding backward.
        Good loading choice:
        - submission_trend = true
        - review_trend = true
        - exercise_graph = true

        Example 4:
        - Current review points to a likely HARDER or TRANSFER path.
        - The student may already have seen several nearby exercises.
        - Main uncertainty: whether repeated exposure means variation is better than simple progression.
        Good loading choice:
        - student_history = true
        - exercise_graph = true
        - review_trend = false
        - submission_trend = false

        Negative example:
        - If the current review already strongly shows the student needs reinforcement,
          do not load every block just because they are available.
        - In that case, loading all blocks is worse than loading only the few that reduce uncertainty.
        - If you cannot name a concrete uncertainty, do not request another block.

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
          "need_student_history": false,
          "provisional_focus_concept_id": "input-output",
          "priority_signal": "current_review_issue",
          "reason": "Current review is strong, so only trend and nearby graph context are needed."
        }}
        """
    ).strip()
