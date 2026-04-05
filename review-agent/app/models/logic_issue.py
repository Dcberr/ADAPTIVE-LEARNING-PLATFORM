from typing import NotRequired, TypedDict

from app.models.location import Location


class LogicIssue(TypedDict):
    issue: str
    evidence: int
    location: NotRequired[Location]
    code_snippet: str
    relevant_concept: list[str]
    other_concept: list[str]
    fix_suggestion: str


def create_logic_issue(
    issue: str = "",
    evidence: int = -1,
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
        "relevant_concept": [],
        "other_concept": [],
        "fix_suggestion": "",
    }
