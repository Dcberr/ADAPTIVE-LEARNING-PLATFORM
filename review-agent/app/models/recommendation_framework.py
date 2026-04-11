from pydantic import BaseModel, Field


class RecommendationScoringFramework(BaseModel):
    foundation_risk: float = Field(..., ge=0, le=100)
    efficiency_gap: float = Field(..., ge=0, le=100)
    progression_readiness: float = Field(..., ge=0, le=100)
    support_need: float = Field(..., ge=0, le=100)
    explanation: str
