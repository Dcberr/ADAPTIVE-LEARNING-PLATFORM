from pydantic import BaseModel, Field

from code_review_ai.api.review_code_schema import ReviewItem, ScoreCard
from code_review_ai.models.exercise_record import ExerciseRecord


class RecommendationReviewRequest(BaseModel):
    review_id: str
    summary: str
    detail: str
    review_items: list[ReviewItem] = Field(default_factory=list)


class RecommendationSubmissionTestCase(BaseModel):
    input: str = ""
    expect: str = ""
    output: str = ""


class RecommendationSubmissionRequest(BaseModel):
    submission_id: str
    code: str
    testcases: list[RecommendationSubmissionTestCase] = Field(default_factory=list)
    created_at: str = ""


class RecommendationRequest(BaseModel):
    student_id: str
    exercise: ExerciseRecord
    review: RecommendationReviewRequest | None = None
    submission: RecommendationSubmissionRequest | None = None
    focus_concept_id: str
    attempted_exercise_ids: list[str] = Field(default_factory=list)


class RecommendationExercise(ExerciseRecord):
    concept_ids: list[str]
    directive: str


class RecommendationRoadmapStep(BaseModel):
    step: int
    exercise: RecommendationExercise


class RecommendationResponse(BaseModel):
    student_id: str
    current_exercise_id: str
    focus_concept_id: str
    roadmap: list[RecommendationRoadmapStep]
