from __future__ import annotations

from textwrap import dedent

from app.models.review_state import ReviewState


def build_overview_messages(state: ReviewState) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "You are a helpful CS1 teacher."},
        {"role": "user", "content": build_overview_prompt(state)},
    ]


def build_overview_prompt(state: ReviewState) -> str:
    history_text = _format_history(state)
    progress_summary = _format_progress_summary(state)
    return dedent(
        f"""
        You are a CS1 teacher reviewing a student's code submission.

        Summarize the review concisely and in beginner-friendly language. Base your
        overview on both the current submission and the recent sorted submission history when available.

        Focus on helping the student understand:
        1. Functional errors (logic issues)
        2. Style/quality warnings (improvement notes)
        3. What improved from earlier submissions, if there is meaningful progress
        4. How to improve their code step by step

        Current student code:
        {state['code']}

        Submission history:
        {history_text}

        History-based progress summary:
        {progress_summary}

        Logic issues (Errors):
        {list(state.get('logic_issues', {}).values())}

        Review links to earlier attempts for the same testcase:
        {state.get('review_links', [])}

        Improvement notes (Warnings):
        {state.get('improvement_notes', [])}

        Instructions:
        - Generate a clear overview paragraph that a CS1 student can easily understand.
        - Highlight the most important errors first, then warnings.
        - If history is available, briefly mention meaningful improvement since recent attempts.
        - Mention whether the student fixed earlier failures, still has persistent failures, or introduced newly failing cases when that is supported by the data.
        - Keep it concise and actionable.
        - Output ONLY the overview text.
        """
    ).strip()


def _format_history(state: ReviewState) -> str:
    history = state.get("history", [])
    if not history:
        return "No previous submission."

    return "\n\n".join(
        [
            (
                f"Previous submission {index} (newest first order):\n"
                f"Failed testcase IDs: {submission.get('failed_test_case_ids', [])}\n"
                f"Passed testcase IDs: {submission.get('passed_test_case_ids', [])}\n"
                f"Code:\n{submission.get('code', '')}"
            )
            for index, submission in enumerate(history, start=1)
        ]
    )


def _format_progress_summary(state: ReviewState) -> str:
    previous_failed = state.get("previous_failed_test_case_ids", [])
    persistent_failed = state.get("persistent_failed_test_case_ids", [])
    fixed_testcases = state.get("fixed_test_case_ids", [])
    regressed_testcases = state.get("regressed_test_case_ids", [])
    return (
        f"Latest previous submission failed testcase IDs: {previous_failed}\n"
        f"Persistent failed testcase IDs: {persistent_failed}\n"
        f"Fixed testcase IDs since the latest previous submission: {fixed_testcases}\n"
        f"Newly failing testcase IDs since the latest previous submission: {regressed_testcases}"
    )
