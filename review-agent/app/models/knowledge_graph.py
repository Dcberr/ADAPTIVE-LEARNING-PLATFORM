from typing import Literal

from pydantic import BaseModel, Field

from app.models.exercise_record import ExerciseRecord
from app.models.review_record import ReviewRecord
from app.models.submission_record import SubmissionRecord
from app.models.student_record import StudentRecord


AssignedPath = Literal["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]


class ConceptRecord(BaseModel):
    concept_id: str
    name: str
    description: str = ""
    difficulty: int = 1


class ConceptRelation(BaseModel):
    prerequisite_id: str
    concept_id: str


class ExerciseConceptLink(BaseModel):
    exercise_id: str
    concept_id: str
    weight: float = 1.0


class ExercisePathLink(BaseModel):
    exercise_id: str
    path: AssignedPath


class KnowledgeGraphDocument(BaseModel):
    concepts: list[ConceptRecord] = Field(default_factory=list)
    concept_relations: list[ConceptRelation] = Field(default_factory=list)
    exercises: list[ExerciseRecord] = Field(default_factory=list)
    exercise_concept_links: list[ExerciseConceptLink] = Field(default_factory=list)
    exercise_path_links: list[ExercisePathLink] = Field(default_factory=list)
    students: list[StudentRecord] = Field(default_factory=list)
    submissions: list[SubmissionRecord] = Field(default_factory=list)
    reviews: list[ReviewRecord] = Field(default_factory=list)
