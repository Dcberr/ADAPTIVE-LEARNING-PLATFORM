from typing import NotRequired, TypedDict

from app.models.location import Location


class LogicIssue(TypedDict):
    issue: str
    evidence: str
    location: NotRequired[Location]
    code_snippet: str
    history_status: str
    relevant_concept: list[str]
    other_concept: list[str]
    fix_suggestion: str


def create_logic_issue(
    issue: str = "",
    evidence: str = "",
    code_snippet: str = "",
    location: Location = None,
) -> LogicIssue:
    """
    Helper function to create a LogicIssue with default empty lists for concepts.
    """
    return {
        "issue": issue,
        "evidence": evidence,
        "code_snippet": code_snippet,
        "location": location,
        "history_status": "",
        "relevant_concept": [],
        "other_concept": [],
        "fix_suggestion": "",
    }
