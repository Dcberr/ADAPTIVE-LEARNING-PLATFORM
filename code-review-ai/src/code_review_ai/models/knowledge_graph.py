from typing import Literal

from pydantic import BaseModel


AssignedPath = Literal[
    "REINFORCE",
    "IMPROVE",
    "HARDER",
    "PREREQUISITE_REVIEW",
    "TRANSFER",
]


class ConceptRecord(BaseModel):
    concept_id: str
    slug: str = ""
    name: str
    description: str = ""
    difficulty: int = 1


class ExerciseRelation(BaseModel):
    exercise_id: str
    related_exercise_id: str
    weight: float = 1.0
    relation_type: str = ""
    difficulty_gap: float = 0.0
    progression_score: float = 0.0
    similarity_score: float = 0.0
