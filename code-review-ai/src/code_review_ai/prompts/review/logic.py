from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.review_state import SandBoxResult


def build_logic_messages(
    code_context: str,
    failed_tests: list[SandBoxResult],
) -> list[dict[str, str]]:
    tests_str = "\n".join(
        [
            (
                f"Testcase {index + 1} | "
                f"Input: {tc['input']} | Expected: {tc['expected']} | Actual: {tc['actual']}"
            )
            for index, tc in enumerate(failed_tests)
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
                1. For each failing test case, produce one JSON object in the same order as the testcases shown above.
                2. Each JSON object must contain:
                   - "issue": a short explanation of why the test failed
                   - "cause_type": one of "incorrect_code", "missing_logic", "missing_branch", or "missing_validation"
                   - "why_test_failed": one short causal explanation tied to the testcase
                   - "code_snippet": the exact buggy code copied verbatim from the student code if it exists, otherwise null
                   - "anchor_snippet": the nearest relevant code copied verbatim from the student code if no exact buggy code exists, otherwise null
                   - "location": line/column start and end of the code snippet if known (otherwise null)
                   - "missing_behavior": the missing behavior to add if the failure is caused by missing logic, otherwise null
                3. Do not include testcase ids, indexes, or any other identifier fields in the response.
                4. Respond only in JSON format, matching this schema:

                {{
                  "logic_issues": [
                    {{
                      "issue": "short explanation",
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
                - Return one item per testcase in the same order they were listed above.
                - Do NOT mention testcase IDs, submission IDs, UUIDs, or any identifier-like labels in `issue`, `why_test_failed`, or `missing_behavior`.
                - If you refer to a testcase, use its shown input/output text or behavior description instead of any ID.
                Make your explanations concise and beginner-friendly.
                """
            ).strip(),
        },
    ]
