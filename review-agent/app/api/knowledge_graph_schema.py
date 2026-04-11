from pydantic import BaseModel, Field

from app.api.review_code_schema import ReviewItem, ScoreCard
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath, ConceptRecord, KnowledgeGraphDocument
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring
from app.models.student_record import StudentRecord


class UpsertConceptRequest(BaseModel):
    concept_id: str
    name: str
    description: str = ""
    difficulty: int = 1
    prerequisite_ids: list[str] = Field(default_factory=list)


class UpsertExerciseRequest(BaseModel):
    exercise_id: str
    title: str
    description: str
    content: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    recommended_paths: list[AssignedPath] = Field(default_factory=list)


class UpsertStudentRequest(BaseModel):
    student_id: str
    current_concept: str = ""
    mastered_concepts: list[str] = Field(default_factory=list)
    attempted_exercise_ids: list[str] = Field(default_factory=list)
    student_profile: StudentProfileScoring
    notes: str = ""


class UpsertReviewRequest(BaseModel):
    student_id: str
    exercise_id: str
    submission_id: str
    summary: str
    detail: str
    review_items: list[ReviewItem] = Field(default_factory=list)
    scorecard: ScoreCard
    current_concept: str = ""
    review_id: str | None = None


class RecalculateStudentProfileRequest(BaseModel):
    exercise_id: str
    current_concept: str = ""
    scorecard: ScoreCard


class KnowledgeGraphConceptResponse(BaseModel):
    concept: ConceptRecord


class KnowledgeGraphExerciseResponse(BaseModel):
    exercise: ExerciseRecord


class KnowledgeGraphStudentResponse(BaseModel):
    student: StudentRecord


class KnowledgeGraphReviewResponse(BaseModel):
    review: ReviewRecord


class KnowledgeGraphStudentProfileResponse(BaseModel):
    student_id: str
    exercise_id: str
    current_concept: str
    student_profile: StudentProfileScoring


class KnowledgeGraphSnapshotResponse(BaseModel):
    graph: KnowledgeGraphDocument
