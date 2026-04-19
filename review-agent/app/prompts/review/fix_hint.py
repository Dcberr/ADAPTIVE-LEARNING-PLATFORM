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

                Your hint must be grounded in the provided diagnosis. Use the
                failure cause, testcase behavior, and code context to give one
                focused next step.
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

                ANCHOR SNIPPET:
                {issue.get('anchor_snippet', '')}

                PROBLEM SUMMARY:
                {issue.get('issue', '')}

                CAUSE TYPE:
                {issue.get('cause_type', '')}

                WHY THE TEST FAILED:
                {issue.get('why_test_failed', '')}

                MISSING BEHAVIOR:
                {issue.get('missing_behavior', '')}

                FAILING TESTCASE DETAILS:
                {testcase_context}

                EVIDENCE:
                Test case ID {issue.get('evidence')}

                HISTORY STATUS:
                {issue.get('history_status', 'unknown')}

                TASK:
                Generate a JSON object with a clear fix hint that explains what might
                be wrong conceptually and what steps the student should take to fix it.

                Hint strategy by cause type:
                - incorrect_code: explain what the current code is doing wrong for this testcase and what value, branch, or calculation the student should trace first.
                - missing_logic or missing_branch: explain what case is not handled yet and where to add that behavior near the ANCHOR SNIPPET.
                - missing_validation: explain what should be checked before the current logic continues.

                Rules:
                - If CODE SNIPPET is empty, assume the issue is missing logic and explain what to add conceptually near the ANCHOR SNIPPET.
                - Do not invent exact code that is not present in the student's submission.
                - Focus on the smallest conceptual change that would make the testcase pass.
                - Give one actionable next step the student can try immediately.
                - Do not rewrite the whole program.
                - Do not provide the final full solution.
                - Ground the hint in the failing testcase details.

                Output must be valid JSON:
                {{
                  "fix_suggestion": "your suggestion here"
                }}
                """
            ).strip(),
        },
    ]
