from pydantic import BaseModel, Field


class StudentProfileScoring(BaseModel):
    concept_mastery: float = Field(..., ge=0.0, le=1.0)
    implementation_consistency: float = Field(..., ge=0.0, le=1.0)
    debugging_independence: float = Field(..., ge=0.0, le=1.0)
    efficiency_awareness: float = Field(..., ge=0.0, le=1.0)
    concept_transfer: float = Field(..., ge=0.0, le=1.0)
    learning_velocity: float = Field(..., ge=0.0, le=1.0)
    notes: str = ""
