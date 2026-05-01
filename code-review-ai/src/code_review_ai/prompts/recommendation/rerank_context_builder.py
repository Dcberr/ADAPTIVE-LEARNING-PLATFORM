from __future__ import annotations

from textwrap import dedent


def build_rerank_context_builder_system_prompt() -> str:
    return dedent(
        """
        You help build reranking context for CS exercise recommendation.

        Your job has two parts:
        1. Build a goal-focused rerank query from the provided exercise, review, and submission context.
        2. Build a concise student overview paragraph from the same provided context.

        Rules:
        - Keep the query focused on the student's next exercise goal.
        - The overview must be one practical paragraph, not bullet points.
        - Prefer signals about current concept weakness, recent progress, repeated mistakes, and readiness.
        Return valid JSON only.
        """
    ).strip()


def build_rerank_context_plan_prompt(*, base_context: dict) -> str:
    return dedent(
        f"""
        Build a planning query for the reranker.
        Keep the goal query centered on choosing the next best exercise for the current concept.

        Reason carefully from:
        - the current review summary, detail, and issues
        - the current submission code preview and testcase state

        Base context:
        {base_context}

        Return JSON with:
        {{
          "goal_query": "short rerank goal text"
        }}
        """
    ).strip()


def build_rerank_context_finalize_prompt(
    *,
    base_context: dict,
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
        4. Write a goal query that tells the reranker what kind of next exercise should rank highest.
        5. Write a one-paragraph student overview that summarizes the current state.

        Guidance:
        - Keep the goal query short, concrete, and ranking-oriented.
        - Keep the overview practical and recommendation-oriented, not diagnostic-only.

        Planner goal query:
        {planner_goal_query}

        Base context:
        {base_context}

        Return JSON with:
        {{
          "goal_query": "focused rerank goal text",
          "student_overview": "one short paragraph summarizing the student's context",
          "query_facets": ["facet 1", "facet 2"]
        }}
        """
    ).strip()
