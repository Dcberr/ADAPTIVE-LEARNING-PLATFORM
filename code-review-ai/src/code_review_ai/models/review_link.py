from typing import NotRequired, TypedDict


class ReviewLink(TypedDict):
    issue_evidence: NotRequired[str]
    previous_submission_id: str
    previous_code_snippets: list[str]
    comparison_mode: str
    what_improved: str
    what_still_needs_work: str
    relation_summary: str


def create_review_link(
    issue_evidence: str = "",
    previous_submission_id: str = "",
    previous_code_snippets: list[str] | None = None,
    comparison_mode: str = "",
    what_improved: str = "",
    what_still_needs_work: str = "",
    relation_summary: str = "",
) -> ReviewLink:
    return {
        "issue_evidence": issue_evidence,
        "previous_submission_id": previous_submission_id,
        "previous_code_snippets": previous_code_snippets or [],
        "comparison_mode": comparison_mode,
        "what_improved": what_improved,
        "what_still_needs_work": what_still_needs_work,
        "relation_summary": relation_summary,
    }
