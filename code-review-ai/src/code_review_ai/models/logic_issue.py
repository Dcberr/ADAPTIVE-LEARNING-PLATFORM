from typing import NotRequired, TypedDict

from code_review_ai.models.location import Location


class LogicIssue(TypedDict):
    issue: str
    evidence: str
    location: NotRequired[Location]
    code_snippet: str
    anchor_snippet: NotRequired[str]
    cause_type: NotRequired[str]
    why_test_failed: NotRequired[str]
    missing_behavior: NotRequired[str]
    history_status: str
    fix_suggestion: str


def create_logic_issue(
    issue: str = "",
    evidence: str = "",
    code_snippet: str = "",
    anchor_snippet: str = "",
    cause_type: str = "",
    why_test_failed: str = "",
    missing_behavior: str = "",
    location: Location = None,
) -> LogicIssue:
    """Helper function to create a LogicIssue."""
    return {
        "issue": issue,
        "evidence": evidence,
        "code_snippet": code_snippet,
        "anchor_snippet": anchor_snippet,
        "cause_type": cause_type,
        "why_test_failed": why_test_failed,
        "missing_behavior": missing_behavior,
        "location": location,
        "history_status": "",
        "fix_suggestion": "",
    }
