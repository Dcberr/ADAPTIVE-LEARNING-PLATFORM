from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.review_state import ReviewState


def build_overview_messages(state: ReviewState) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are a CS1 teacher writing a short review summary. "
                "Return only a brief student-facing overview paragraph. "
                "Do not repeat the prompt, instructions, labels, or raw analysis."
            ),
        },
        {"role": "user", "content": build_overview_prompt(state)},
    ]


def build_overview_prompt(state: ReviewState) -> str:
    logic_issues = list(state.get("logic_issues", {}).values())[:2]
    improvement_notes = list(state.get("improvement_notes", []))[:2]

    return dedent(
        f"""
        Write a short overview review for the student's current submission.

        Use only the current review findings. Do not mention earlier attempts or review history.

        Current review findings:
        - Logic issues: {logic_issues}
        - Improvement notes: {improvement_notes}

        Instructions:
        - Generate exactly one short paragraph with 2 to 3 sentences.
        - Keep it high-level and beginner-friendly.
        - Start with the main problem in the submission, then briefly mention one important improvement point if relevant.
        - Focus on the overall review, not line-by-line explanation.
        - Do not include raw code, JSON-like objects, labels, headings, or bullet points.
        - Do not repeat these instructions or mention the system prompt.
        - Do not mention submission history, progress tracking, persistence, regression, or earlier attempts.
        - Do NOT list test cases, test case IDs, testcase names, or any identifier-like labels.
        - If you mention an example failure, describe the behavior briefly without using any ID.
        - Output ONLY the overview text.
        """
    ).strip()
