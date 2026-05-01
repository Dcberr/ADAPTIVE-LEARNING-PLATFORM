from typing import TypedDict

from code_review_ai.api.recommendation_schema import (
    RecommendationReviewRequest,
    RecommendationSubmissionRequest,
)
from code_review_ai.models.exercise_record import ExerciseRecord


class RecommendationState(TypedDict):
    student_id: str
    exercise_id: str
    exercise: ExerciseRecord
    focus_concept_id: str
    review: RecommendationReviewRequest | None
    submission: RecommendationSubmissionRequest | None
    attempted_exercise_ids: list[str]
    retrieved_candidates: list[dict]
    rerank_query: dict
    rerank_overview: str
    reranked_candidates: list[dict]
