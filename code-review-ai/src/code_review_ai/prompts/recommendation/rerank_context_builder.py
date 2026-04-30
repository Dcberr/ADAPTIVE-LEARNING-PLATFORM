from __future__ import annotations

from textwrap import dedent


def build_rerank_context_builder_system_prompt() -> str:
    return dedent(
        """
        You help build reranking context for CS exercise recommendation.

        Your job has two parts:
        1. Decide whether more review history or submission history is needed.
        2. Build a goal-focused rerank query and a concise student overview paragraph.

        Rules:
        - Keep the query focused on the student's next exercise goal.
        - Request extra history only if it will change candidate ranking decisions.
        - The overview must be one practical paragraph, not bullet points.
        - Prefer signals about current concept weakness, recent progress, repeated mistakes, and readiness.
        Return valid JSON only.
        """
    ).strip()


def build_rerank_context_plan_prompt(*, base_context: dict) -> str:
    return dedent(
        f"""
        Decide whether the reranker needs more history beyond the base context.
        Keep the goal query centered on choosing the next best exercise for the current concept.

        Reason carefully from:
        - the current review summary, detail, and issues
        - the current submission code preview and testcase state
        - any already-available review history
        - any already-available submission history comparisons

        Ask for more review history only if the current review is not enough to judge repeated mistakes,
        trend, or concept stability.
        Ask for more submission history only if the current submission is not enough to judge progress,
        regression, or readiness for the next exercise.
        If current review and current submission already give enough signal, keep the history limits at 0.

        Base context:
        {base_context}

        Return JSON with:
        {{
          "goal_query": "short rerank goal text",
          "need_review_history": true,
          "review_history_limit": 0,
          "need_submission_history": true,
          "submission_history_limit": 0
        }}
        """
    ).strip()


def build_rerank_context_finalize_prompt(
    *,
    base_context: dict,
    review_history: list[dict],
    submission_history: list[dict],
    planner_goal_query: str,
) -> str:
    return dedent(
        f"""
        Build the final rerank query and context summary for exercise recommendation.
        Keep the goal query focused on what the reranker should optimize for next.
        Use the available history only if it meaningfully sharpens ranking.

        Reason in this order:
        1. Read the current exercise and focus concept to identify the immediate learning goal.
        2. Read the current review summary, detail, and issues to identify the student's most important weakness.
        3. Read the current submission preview and testcase state to judge whether the student needs reinforcement,
           correction, or a slightly harder next step.
        4. Use review history only to confirm repeated mistakes, trend, or concept stability.
        5. Use submission history only to confirm progress, regression, or whether the current mistake is persistent.
        6. Write a goal query that tells the reranker what kind of next exercise should rank highest.
        7. Write a one-paragraph student overview that summarizes the current state, with history as supporting evidence
           rather than the main focus.

        Guidance:
        - Prioritize current information over older history.
        - If history conflicts with the latest review or submission, trust the latest evidence more.
        - Keep the goal query short, concrete, and ranking-oriented.
        - Keep the overview practical and recommendation-oriented, not diagnostic-only.

        Planner goal query:
        {planner_goal_query}

        Base context:
        {base_context}

        Review history:
        {review_history}

        Submission history:
        {submission_history}

        Return JSON with:
        {{
          "goal_query": "focused rerank goal text",
          "student_overview": "one short paragraph summarizing the student's context",
          "query_facets": ["facet 1", "facet 2"]
        }}
        """
    ).strip()
