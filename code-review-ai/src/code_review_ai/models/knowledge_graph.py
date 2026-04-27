from typing import Literal

from pydantic import BaseModel, Field

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord
from code_review_ai.models.student_record import StudentRecord


AssignedPath = Literal["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]


class ConceptRecord(BaseModel):
    concept_id: str
    slug: str = ""
    name: str
    description: str = ""
    difficulty: int = 1


class ConceptRelation(BaseModel):
    prerequisite_id: str
    concept_id: str
    strength: float = 1.0


class ExerciseConceptLink(BaseModel):
    exercise_id: str
    concept_id: str
    weight: float = 1.0


class ExercisePathLink(BaseModel):
    exercise_id: str
    concept_id: str
    path: AssignedPath
    weight: float = 1.0


class ExerciseRelation(BaseModel):
    exercise_id: str
    related_exercise_id: str
    weight: float = 1.0
    relation_type: str = ""
    target_concept_id: str = ""
    shared_concept_ids: list[str] = Field(default_factory=list)
    difficulty_gap: float = 0.0
    progression_score: float = 0.0
    similarity_score: float = 0.0


class SubmissionRelation(BaseModel):
    previous_submission_id: str
    next_submission_id: str
    student_id: str = ""
    linked_at: str = ""
    same_exercise: bool = True
    improvement_ratio: float = 0.0
    regression_ratio: float = 0.0


class ReviewRelation(BaseModel):
    previous_review_id: str
    next_review_id: str
    student_id: str = ""
    linked_at: str = ""
    same_concept: bool = False
    improvement_signal: float = 0.0
    severity_change: float = 0.0


class KnowledgeGraphDocument(BaseModel):
    concepts: list[ConceptRecord] = Field(default_factory=list)
    concept_relations: list[ConceptRelation] = Field(default_factory=list)
    exercises: list[ExerciseRecord] = Field(default_factory=list)
    exercise_concept_links: list[ExerciseConceptLink] = Field(default_factory=list)
    exercise_path_links: list[ExercisePathLink] = Field(default_factory=list)
    exercise_relations: list[ExerciseRelation] = Field(default_factory=list)
    students: list[StudentRecord] = Field(default_factory=list)
    submissions: list[SubmissionRecord] = Field(default_factory=list)
    submission_relations: list[SubmissionRelation] = Field(default_factory=list)
    reviews: list[ReviewRecord] = Field(default_factory=list)
    review_relations: list[ReviewRelation] = Field(default_factory=list)
