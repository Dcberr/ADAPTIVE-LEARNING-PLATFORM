from typing import TypedDict


class ReviewLink(TypedDict):
    current_issue: str
    current_code_snippet: str
    previous_submission_indexes: list[int]
    previous_code_snippet: str
    what_improved: str
    what_still_needs_work: str
    relation_summary: str


def create_review_link(
    current_issue: str = "",
    current_code_snippet: str = "",
    previous_submission_indexes: list[int] | None = None,
    previous_code_snippet: str = "",
    what_improved: str = "",
    what_still_needs_work: str = "",
    relation_summary: str = "",
) -> ReviewLink:
    return {
        "current_issue": current_issue,
        "current_code_snippet": current_code_snippet,
        "previous_submission_indexes": previous_submission_indexes or [],
        "previous_code_snippet": previous_code_snippet,
        "what_improved": what_improved,
        "what_still_needs_work": what_still_needs_work,
        "relation_summary": relation_summary,
    }
