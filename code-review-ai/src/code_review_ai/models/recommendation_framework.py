from typing import Literal

from pydantic import BaseModel


class RecommendationScoringFramework(BaseModel):
    risk_level: Literal["high", "medium", "low"]
    readiness_level: Literal["emerging", "developing", "ready"]
    explanation: str
