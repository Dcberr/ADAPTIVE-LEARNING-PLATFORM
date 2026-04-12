from pydantic import BaseModel, Field

from app.api.review_code_schema import ReviewItem, ScoreCard
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath, ConceptRecord, KnowledgeGraphDocument
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring
from app.models.submission_record import SubmissionRecord, SubmissionTestCaseOutput


class UpsertConceptRequest(BaseModel):
    name: str
    description: str = ""
    difficulty: int = 1
    prerequisites: list[ConceptRecord] = Field(default_factory=list)


class UpsertExerciseRequest(BaseModel):
    title: str
    description: str
    content: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    recommended_paths: list[AssignedPath] = Field(default_factory=list)


class UpsertStudentProfileRequest(BaseModel):
    student_profile: StudentProfileScoring


class UpsertSubmissionRequest(BaseModel):
    student_id: str
    exercise_id: str
    code: str
    testcase_outputs: list[SubmissionTestCaseOutput] = Field(default_factory=list)


class UpsertReviewRequest(BaseModel):
    submission_id: str
    summary: str
    detail: str
    review_items: list[ReviewItem] = Field(default_factory=list)
    scorecard: ScoreCard
    current_concept: str = ""


class RecalculateStudentProfileRequest(BaseModel):
    exercise_id: str
    current_concept: str = ""
    scorecard: ScoreCard


class KnowledgeGraphConceptResponse(BaseModel):
    concept: ConceptRecord


class KnowledgeGraphExerciseResponse(BaseModel):
    exercise: ExerciseRecord


class KnowledgeGraphStudentResponse(BaseModel):
    student_id: str
    student_profile: StudentProfileScoring


class KnowledgeGraphReviewResponse(BaseModel):
    review: ReviewRecord


class KnowledgeGraphSubmissionResponse(BaseModel):
    submission: SubmissionRecord


class KnowledgeGraphStudentProfileResponse(BaseModel):
    student_id: str
    exercise_id: str
    current_concept: str
    student_profile: StudentProfileScoring


class KnowledgeGraphSnapshotResponse(BaseModel):
    graph: KnowledgeGraphDocument
