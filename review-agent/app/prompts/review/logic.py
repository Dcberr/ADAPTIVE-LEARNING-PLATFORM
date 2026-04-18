from __future__ import annotations

from textwrap import dedent
from typing import Any

from app.models.review_state import SandBoxResult


def build_logic_messages(
    code: str,
    failed_tests: list[SandBoxResult],
    history: list[dict[str, Any]],
) -> list[dict[str, str]]:
    tests_str = "\n".join(
        [
            f"ID: {tc['id']} | Input: {tc['input']} | Expected: {tc['expected']} | Actual: {tc['actual']}"
            for tc in failed_tests
        ]
    )
    history_str = _format_history(history)
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a CS1-level programming tutor.

                Analyze student code and failing test cases, optionally using prior
                submission history as context, and identify the specific code snippets
                causing each failure.

                You must respond in valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Student code:
                {code}

                Submission history:
                {history_str}

                Failing test cases:
                {tests_str}

                Instructions:
                1. For each failing test case, produce a JSON object containing:
                   - "issue": a short explanation of why the test failed
                   - "evidence": the 'id' of the failing test case
                   - "code_snippet": the part of the student's code that likely caused this failure
                   - "location": line/column start and end of the code snippet if known (otherwise null)
                2. Respond only in JSON format, matching this schema:

                {{
                  "logic_issues": [
                    {{
                      "issue": "short explanation",
                      "evidence": "test case id",
                      "code_snippet": "relevant code snippet",
                      "location": {{
                        "start_line": line_number,
                        "end_line": line_number,
                        "start_col": column_number (optional),
                        "end_col": column_number (optional)
                      }}
                    }}
                  ]
                }}

                Make your explanations concise and beginner-friendly.
                """
            ).strip(),
        },
    ]


def _format_history(history: list[dict[str, Any]]) -> str:
    if not history:
        return "None"

    return "\n".join(
        [
            (
                f"Submission {index}: "
                f"failed_test_case_ids={submission.get('failed_test_case_ids', [])}\n"
                f"Code:\n{submission.get('code', '')}"
            )
            for index, submission in enumerate(history, start=1)
        ]
    )
