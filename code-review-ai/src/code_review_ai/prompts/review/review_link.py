from __future__ import annotations

from textwrap import dedent


def build_review_link_messages(
    current_code: str,
    batch_candidates: list[dict],
) -> list[dict[str, str]]:
    issues_text = "\n\n".join(
        [
            f"""Issue {index + 1}
Current issue summary: {candidate['issue'].get('issue', '')}
Current code snippet identified by the logic agent:
{candidate['current_code_snippet']}

Comparison mode: {candidate['comparison_mode']}

First earlier failed submission for this testcase:
{_format_previous_submission(candidate['previous_submission'])}

Changed code summary between that submission and the current code:
{_format_changed_summary(candidate.get('changed_summary', []))}
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

                Compare each current issue with the first earlier submission where
                the same testcase also failed. Use the current issue description and
                code snippet as anchors, then inspect that earlier failed submission
                to identify what improved and what still needs work.

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
                Compare each current issue with the earlier failed submission shown above. Focus on:
                - what changed around the relevant logic
                - whether the issue is still persistent or is only linked to an older failed attempt
                - whether there is meaningful improvement or minimal change
                - what the student should still focus on next

                Return JSON in exactly this shape:
                {{
                  "review_links": [
                    {{
                      "previous_code_snippets": ["snippet from the earlier failed submission that relates to the current issue"],
                      "comparison_mode": "persistent",
                      "what_improved": "brief statement of what improved compared with the past attempt(s)",
                      "what_still_needs_work": "brief statement of what still needs to be fixed",
                      "relation_summary": "one concise sentence explaining the link between past and current attempts"
                    }}
                  ]
                }}

                Guidelines:
                - Ground the comparison in the current issue, current code snippet, and the earlier failed submission.
                - It is okay to say that improvement is minimal or unclear.
                - Use only the first earlier submission where the testcase failed.
                - Return one review link object per issue in the same order the issues were listed above.
                - Do not include ids, issue refs, testcase ids, or submission ids in the response.
                - If you mention the testcase, describe it using its shown behavior or code context, not any ID.
                - `previous_code_snippets` should contain only short snippets from that earlier failed submission that relate to the current issue.
                - If the latest previous submission also failed this testcase, `comparison_mode` should usually be `persistent`.
                - If the match comes from an older earlier failed submission but not the latest previous submission, `comparison_mode` can be `historical_match`.
                - Keep the language student-friendly.
                - Return JSON only.
                """
            ).strip(),
        },
    ]


def _format_previous_submission(previous_submission: dict[str, str]) -> str:
    return (
        f"Code:\n{previous_submission.get('code', '')}"
    )


def _format_changed_summary(changed_summary: list[str]) -> str:
    if not changed_summary:
        return "No concise code diff summary available."
    return "\n".join(changed_summary)
