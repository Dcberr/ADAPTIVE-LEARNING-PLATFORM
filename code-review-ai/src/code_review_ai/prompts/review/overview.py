from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.review_state import ReviewState


def build_overview_messages(state: ReviewState) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "You are a helpful CS1 teacher."},
        {"role": "user", "content": build_overview_prompt(state)},
    ]


def build_overview_prompt(state: ReviewState) -> str:
    return dedent(
        f"""
        You are a CS1 teacher reviewing a student's code submission.

        Summarize the review concisely and in beginner-friendly language. Base your
        overview only on the current submission and its current review findings.

        Focus on helping the student understand:
        1. Functional errors (logic issues)
        2. Style/quality warnings (improvement notes)
        3. What the current submission does better
        4. What habits or mistakes they should avoid next

        Current student code:
        {state['code']}

        Logic issues (Errors):
        {list(state.get('logic_issues', {}).values())}

        Improvement notes (Warnings):
        {state.get('improvement_notes', [])}

        Instructions:
        - Generate only 3 to 5 sentences in one paragraph.
        - Keep the summary moderately detailed but still easy for a CS1 student to understand.
        - Focus only on what the student improved and what the student needs to avoid next.
        - You may briefly mention the main remaining problem, but do not turn the summary into a step-by-step checklist.
        - Do not mention submission history, progress tracking, persistence, regression, or earlier attempts.
        - Do NOT list test cases, test case IDs, testcase names, or any identifier-like labels.
        - If you mention an example failure, describe it using the testcase text or behavior, not any ID.
        - Highlight the most important errors first, then warnings.
        - Keep it concise and actionable.
        - Output ONLY the overview text.
        """
    ).strip()
