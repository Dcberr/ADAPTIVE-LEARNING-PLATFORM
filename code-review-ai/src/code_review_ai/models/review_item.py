from typing import Literal, NotRequired, TypedDict

from code_review_ai.models.location import Location


class ReviewItem(TypedDict):
    type: Literal["Warning", "Error"]
    location: NotRequired[Location]
    code_snippet: str
    fix_suggestion: str
    issue: str
