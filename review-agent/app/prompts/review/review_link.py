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

Comparison mode: {candidate['comparison_mode']}

Matching history entries for this testcase (sorted newest first):
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

                Compare each current issue with the sorted testcase history for that
                same testcase. Use the current issue description and code snippet as
                anchors, then inspect the history entries to identify what improved,
                what regressed, and what still needs work.

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
                Compare each current issue with the testcase history shown above. Focus on:
                - what changed around the relevant logic
                - whether the newest matching history entry shows a persistent failure, a regression from pass to fail, or a current-only issue
                - whether there is meaningful improvement, minimal change, or regression
                - what the student should still focus on next

                Return JSON in exactly this shape:
                {{
                  "review_links": [
                    {{
                      "issue_ref": 0,
                      "comparison_mode": "persistent",
                      "previous_code_snippet": "snippet from a previous submission that best matches the current issue",
                      "what_improved": "brief statement of what improved compared with the past attempt(s)",
                      "what_still_needs_work": "brief statement of what still needs to be fixed",
                      "relation_summary": "one concise sentence explaining the link between past and current attempts"
                    }}
                  ]
                }}

                Guidelines:
                - Ground the comparison in the current issue and current code snippet.
                - It is okay to say that improvement is minimal or unclear.
                - Use the newest matching history entry as the main comparison anchor, but use older matching entries to judge trend if helpful.
                - If the newest matching history entry passed the testcase and the current one fails, treat it as a regression.
                - If the newest matching history entry failed the testcase and the current one still fails, treat it as a persistent issue.
                - If there is no meaningful earlier match, say the issue appears only in the current attempt.
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
                f"History submission index: {match['submission_index']}\n"
                f"Testcase status: {match['testcase_status']}\n"
                f"Code:\n{match['code']}"
            )
            for match in history_matches
        ]
    )
