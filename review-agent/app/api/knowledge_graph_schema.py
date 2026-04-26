from pydantic import BaseModel, Field

from app.api.review_code_schema import ReviewItem, ScoreCard
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import ConceptRecord, KnowledgeGraphDocument
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring
from app.models.submission_record import SubmissionRecord, SubmissionTestCaseOutput


class UpsertConceptRequest(BaseModel):
    name: str
    description: str = ""
    difficulty: int = 1


class PatchConceptRelationsRequest(BaseModel):
    prerequisite_slugs: list[str] | None = None


class UpsertExerciseRequest(BaseModel):
    slug: str = ""
    title: str
    description: str
    content: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)


class PatchExerciseRelationsRequest(BaseModel):
    concept_slugs: list[str] | None = None
    related_exercise_ids: list[str] | None = None
    related_exercise_slugs: list[str] | None = None


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
