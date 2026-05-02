from __future__ import annotations

from textwrap import dedent


def build_improvement_messages(code_context: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a CS1-level programming tutor focused on clean code and
                beginner-friendly refactoring.

                Analyze structured C++ code context and provide educational warning feedback about
                readability, naming, structure, duplication, and simple refactoring
                opportunities, but not logic or syntax errors.

                Focus on warnings that help the student write clearer code or avoid
                creating future mistakes from confusing structure.

                All responses must be in valid JSON format.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Analyze the student's code below and identify clean code and
                refactoring warnings for a CS1 student.

                These warnings should help the student write clearer, easier-to-follow
                code even if the program already passes all test cases.

                STRUCTURED C++ CODE CONTEXT:
                {code_context}

                Return valid JSON with this structure:
                {{
                  "improvement_notes": [
                    {{
                      "location": {{
                        "start_line": line_number,
                        "end_line": line_number,
                        "start_col": column_number (optional),
                        "end_col": column_number (optional)
                      }},
                      "code_snippet": "exact code lines related to the issue",
                      "fix_suggestion": "specific and actionable clean-code or refactoring suggestion",
                      "issue": "explain in simple CS1 terms why this code should be cleaned up or refactored"
                    }}
                  ]
                }}

                Guidelines:
                - Explain each warning in a way that a CS1 student can understand.
                - Focus on naming, readability, duplication, simple function extraction, structure, and unused or noisy code.
                - Warn about code structure only when it could realistically confuse the student or make later mistakes more likely.
                - Use the provided hotspots and code structure as evidence, not speculation.
                - Prefer a few high-signal warnings over many small style comments.
                - Do NOT talk about hidden test cases or speculative failures not supported by the code structure.
                - Do NOT repeat logic or syntax errors that belong to other review items.
                - Do NOT include testcase IDs, submission IDs, UUIDs, or any identifier-like labels in `issue` or `fix_suggestion`.
                - If the code is already correct, still give clean-code warnings when there are beginner-friendly refactoring opportunities.
                - Keep the tone supportive, practical, and educational.
                - Return an empty list only if the code is already very clean for a CS1 student.
                """
            ).strip(),
        },
    ]
