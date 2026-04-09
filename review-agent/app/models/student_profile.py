from pydantic import BaseModel, Field


class StudentProfileScoring(BaseModel):
    concept_mastery: int = Field(..., ge=1, le=5)
    implementation_consistency: int = Field(..., ge=1, le=5)
    debugging_independence: int = Field(..., ge=1, le=5)
    efficiency_awareness: int = Field(..., ge=1, le=5)
    concept_transfer: int = Field(..., ge=1, le=5)
    learning_velocity: int = Field(..., ge=1, le=5)
    notes: str = ""
