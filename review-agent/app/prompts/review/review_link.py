from __future__ import annotations

from textwrap import dedent


def build_review_link_messages(
    current_code: str,
    batch_candidates: list[dict],
) -> list[dict[str, str]]:
    issues_text = "\n\n".join(
        [
            f"""Issue ref: {index}
Current issue summary: {candidate['current_issue']}
Current code snippet identified by the logic agent:
{candidate['current_code_snippet']}

Matching previous submissions for the same testcase:
{_format_history_matches(candidate['history_matches'])}
"""
            for index, candidate in enumerate(batch_candidates)
        ]
    )
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a CS1 progress-analysis agent.

                Compare each current issue with previous submissions that failed the
                same testcase. Use the current issue description and code snippet as
                anchors, then inspect the previous code to identify what improved and
                what still needs work for each issue.

                Return valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Current student code:
                {current_code}

                Issues to compare:
                {issues_text}

                Task:
                Compare each current issue with the previous submissions that failed
                the same testcase. Focus on how the student's code changed around the
                relevant logic.

                Return JSON in exactly this shape:
                {{
                  "review_links": [
                    {{
                      "issue_ref": 0,
                      "previous_code_snippet": "snippet from a previous submission that best matches the current issue",
                      "what_improved": "brief statement of what improved compared with the past attempt(s)",
                      "what_still_needs_work": "brief statement of what still needs to be fixed",
                      "relation_summary": "one concise sentence explaining the link between past and current attempts"
                    }}
                  ]
                }}

                Guidelines:
                - Ground the comparison in the current issue and current code snippet.
                - If improvement is minimal, say so clearly.
                - Keep the language student-friendly.
                - Return JSON only.
                """
            ).strip(),
        },
    ]


def _format_history_matches(history_matches: list[dict[str, str | int]]) -> str:
    return "\n\n".join(
        [
            (
                f"Previous submission index: {match['submission_index']}\n"
                f"Code:\n{match['code']}"
            )
            for match in history_matches
        ]
    )
