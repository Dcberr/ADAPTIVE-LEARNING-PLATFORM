from typing import TypedDict

from code_review_ai.api.review_code_schema import ReviewResponse
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord


class RecommendationState(TypedDict):
    student_id: str
    exercise_id: str
    base_context: dict
    focus_concept_id: str
    focus_concept_weight: float
    review: ReviewResponse | None
    review_record: ReviewRecord | None
    review_history: list[ReviewRecord]
    submission_record: SubmissionRecord | None
    submission_history: list[SubmissionRecord]
    attempted_exercise_ids: list[str]
    retrieved_candidates: list[dict]
    rerank_query: dict
    rerank_overview: str
    reranked_candidates: list[dict]
