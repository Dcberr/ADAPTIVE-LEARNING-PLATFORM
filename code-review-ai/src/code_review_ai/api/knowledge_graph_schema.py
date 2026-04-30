from pydantic import BaseModel, Field

from code_review_ai.api.review_code_schema import ReviewItem, ScoreCard
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord, SubmissionTestCaseOutput


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
    concept_slugs: list[str] = Field(default_factory=list)


class BatchUpsertExerciseItem(UpsertExerciseRequest):
    exercise_id: str


class BatchUpsertExercisesRequest(BaseModel):
    exercises: list[BatchUpsertExerciseItem] = Field(default_factory=list)


class BatchSyncExercisesToVectorRequest(BaseModel):
    exercise_ids: list[str] = Field(default_factory=list)


class PatchExerciseRelationsRequest(BaseModel):
    concept_slugs: list[str] | None = None
    related_exercise_slugs: list[str] | None = None


class BatchPatchExerciseRelationsItem(PatchExerciseRelationsRequest):
    exercise_id: str


class BatchPatchExerciseRelationsRequest(BaseModel):
    exercises: list[BatchPatchExerciseRelationsItem] = Field(default_factory=list)


class UpsertStudentRequest(BaseModel):
    pass


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


class KnowledgeGraphConceptResponse(BaseModel):
    concept: ConceptRecord


class KnowledgeGraphExerciseResponse(BaseModel):
    exercise: ExerciseRecord


class KnowledgeGraphExercisesBatchResponse(BaseModel):
    exercises: list[ExerciseRecord] = Field(default_factory=list)


class KnowledgeGraphStudentResponse(BaseModel):
    student_id: str


class KnowledgeGraphReviewResponse(BaseModel):
    review: ReviewRecord


class KnowledgeGraphSubmissionResponse(BaseModel):
    submission: SubmissionRecord
