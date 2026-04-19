from __future__ import annotations

from textwrap import dedent

from app.models.review_state import SandBoxResult


def build_logic_messages(
    code_context: str,
    failed_tests: list[SandBoxResult],
) -> list[dict[str, str]]:
    tests_str = "\n".join(
        [
            f"ID: {tc['id']} | Input: {tc['input']} | Expected: {tc['expected']} | Actual: {tc['actual']}"
            for tc in failed_tests
        ]
    )
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a CS1-level programming tutor.

                Analyze C++ student code context and failing test cases, and identify
                the root cause of each failure.

                If the needed behavior is missing, do not invent code that is not
                present in the submission.

                You must respond in valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Relevant code context:
                {code_context}

                Failing test cases:
                {tests_str}

                Instructions:
                1. For each failing test case, produce a JSON object containing:
                   - "issue": a short explanation of why the test failed
                   - "evidence": the 'id' of the failing test case
                   - "cause_type": one of "incorrect_code", "missing_logic", "missing_branch", or "missing_validation"
                   - "why_test_failed": one short causal explanation tied to the testcase
                   - "code_snippet": the exact buggy code copied verbatim from the student code if it exists, otherwise null
                   - "anchor_snippet": the nearest relevant code copied verbatim from the student code if no exact buggy code exists, otherwise null
                   - "location": line/column start and end of the code snippet if known (otherwise null)
                   - "missing_behavior": the missing behavior to add if the failure is caused by missing logic, otherwise null
                2. Respond only in JSON format, matching this schema:

                {{
                  "logic_issues": [
                    {{
                      "issue": "short explanation",
                      "evidence": "test case id",
                      "cause_type": "incorrect_code",
                      "why_test_failed": "short causal explanation",
                      "code_snippet": "verbatim buggy code snippet or null",
                      "anchor_snippet": "nearest related code snippet or null",
                      "location": {{
                        "start_line": line_number,
                        "end_line": line_number,
                        "start_col": column_number (optional),
                        "end_col": column_number (optional)
                      }},
                      "missing_behavior": "short description or null"
                    }}
                  ]
                }}

                Rules:
                - Only copy code that actually appears in the student submission.
                - If the test fails because a branch, validation step, or case is missing, set "code_snippet" to null.
                - Use "anchor_snippet" to point to the nearest relevant code when behavior is missing.
                - Merge duplicate test failures that clearly share the same root cause only if the current batch still makes the evidence clear.
                Make your explanations concise and beginner-friendly.
                """
            ).strip(),
        },
    ]
