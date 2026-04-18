from __future__ import annotations

from textwrap import dedent

from app.models.review_state import LogicIssue


def build_fix_hint_messages(
    issue: LogicIssue,
    assignment: str,
    current_code: str,
    testcase_context: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a helpful CS1 tutoring assistant.

                Help students understand and fix their code issues by focusing on
                conceptual understanding.

                Do not reveal the full code solution. Guide the student with
                reasoning and hints.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                ASSIGNMENT DESCRIPTION:
                {assignment}

                CURRENT STUDENT CODE:
                {current_code}

                CODE SNIPPET:
                {issue.get('code_snippet', '')}

                PROBLEM SUMMARY:
                {issue.get('issue', '')}

                FAILING TESTCASE DETAILS:
                {testcase_context}

                EVIDENCE:
                Test case ID {issue.get('evidence')}

                HISTORY STATUS:
                {issue.get('history_status', 'unknown')}

                TASK:
                Generate a JSON object with a clear fix hint that explains what might
                be wrong conceptually and what steps the student should take to fix it.

                Output must be valid JSON:
                {{
                  "fix_suggestion": "your suggestion here"
                }}
                """
            ).strip(),
        },
    ]
