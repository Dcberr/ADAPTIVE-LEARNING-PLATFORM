from typing import NotRequired, TypedDict

from app.models.location import Location


class LogicIssue(TypedDict):
    issue: str
    evidence: str
    location: NotRequired[Location]
    code_snippet: str
    history_status: str
    fix_suggestion: str


def create_logic_issue(
    issue: str = "",
    evidence: str = "",
    code_snippet: str = "",
    location: Location = None,
) -> LogicIssue:
    """Helper function to create a LogicIssue."""
    return {
        "issue": issue,
        "evidence": evidence,
        "code_snippet": code_snippet,
        "location": location,
        "history_status": "",
        "fix_suggestion": "",
    }
