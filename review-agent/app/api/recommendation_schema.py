from typing import Literal

from pydantic import BaseModel

from app.models.exercise_record import ExerciseRecord
from app.models.recommendation_framework import RecommendationScoringFramework


class RecommendationRequest(BaseModel):
    student_id: str
    exercise_id: str


class RecommendationExercise(ExerciseRecord):
    concept_ids: list[str]
    directive: str


class ExplanationRef(BaseModel):
    ref_id: str
    content: str
    ref_category: Literal["code", "review", "exercise"]


class ExplanationBlock(BaseModel):
    content: str
    refs: list[ExplanationRef]


class RecommendationRoadmapStep(BaseModel):
    step: int
    exercise: RecommendationExercise


class RecommendationGraphSummary(BaseModel):
    current_concept_weight: float
    best_path_weight: float
    best_related_exercise_weight: float
    latest_review_improvement_signal: float
    latest_review_severity_change: float
    latest_submission_improvement_ratio: float
    latest_submission_regression_ratio: float


class RecommendationResponse(BaseModel):
    student_id: str
    current_exercise_id: str
    anchor_concept: str
    assigned_path: Literal["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]
    focus_concept_id: str
    critical_errors: int
    framework: RecommendationScoringFramework
    graph_summary: RecommendationGraphSummary
    reasoning: ExplanationBlock
    roadmap_summary: ExplanationBlock
    roadmap: list[RecommendationRoadmapStep]
