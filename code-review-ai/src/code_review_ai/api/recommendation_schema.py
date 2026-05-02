from typing import Literal

from pydantic import BaseModel, Field

from code_review_ai.api.review_code_schema import ReviewItem
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
    focus_concept_ids: list[str] = Field(default_factory=list)
    attempted_exercise_ids: list[str] = Field(default_factory=list)


class RecommendationExercise(ExerciseRecord):
    concept_ids: list[str]


class RecommendationRoadmapExercise(BaseModel):
    priority: int
    reason: str
    exercise: RecommendationExercise


class RecommendationRoadmapStep(BaseModel):
    step: int
    summary: str
    target_concepts: list[str] = Field(default_factory=list)
    exercises: list[RecommendationRoadmapExercise] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    student_id: str
    current_exercise_id: str
    focus_concept_ids: list[str]
    summary: str
    roadmap: list[RecommendationRoadmapStep]
