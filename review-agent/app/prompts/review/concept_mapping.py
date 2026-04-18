from __future__ import annotations

from textwrap import dedent
from typing import List

from app.models.review_state import LogicIssue


def build_concept_mapping_messages(
    issues_batch: List[LogicIssue],
    expected_concepts: List[str],
    assignment_requirements: str,
) -> list[dict[str, str]]:
    formatted_issues = [format_issue(issue) for issue in issues_batch]
    formatted_issues_str = "\n".join(formatted_issues)
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are a concept-mapping agent for CS1 (intro to programming).

                Map each logic issue to CS1 concepts accurately.
                Always respond in valid JSON format.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Assignment requirements:
                {assignment_requirements}

                Expected concepts:
                {expected_concepts}

                Logic issues in this batch:
                {formatted_issues_str}

                Task:
                1. If the issue relates to an expected concept, append it to "relevant_concept".
                2. If the issue relates to other valid CS1 concepts, append it to "other_concept".
                3. Include issue reference "issue_ref" as the index in this batch.
                4. Provide a short explanation citing the evidence (test case ID and/or code snippet).

                Output JSON format:
                {{
                  "concept_issues": [
                    {{
                      "issue_ref": <index>,
                      "relevant_concept": ["concept1", ...],
                      "other_concept": ["conceptX", ...],
                      "explanation": "brief explanation"
                    }}
                  ]
                }}

                Notes:
                - Do NOT invent new failing cases.
                - Keep JSON valid.
                """
            ).strip(),
        },
    ]


def format_issue(issue: LogicIssue) -> str:
    location_str = ""
    if "location" in issue and issue["location"]:
        loc = issue["location"]
        location_str = f" (line {loc.get('line')}, col {loc.get('col')})"

    return (
        f"Issue {issue['evidence']} | "
        f"Summary: {issue['issue']} | "
        f"Evidence (test case ID): {issue['evidence']} | "
        f"Code snippet: {issue['code_snippet']}{location_str}"
    )
