from typing import NotRequired, TypedDict

from code_review_ai.models.location import Location


class ImprovementNote(TypedDict):
    location: NotRequired[Location]
    code_snippet: str
    fix_suggestion: str
    issue: str
