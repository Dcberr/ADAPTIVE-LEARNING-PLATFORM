from typing import TypedDict

from app.api.review_code_schema import ReviewResponse
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath
from app.models.recommendation_framework import RecommendationScoringFramework
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring
from app.models.submission_record import SubmissionRecord


class RecommendationState(TypedDict):
    student_id: str
    exercise_id: str
    base_context: dict
    context_plan: dict
    loaded_blocks: list[str]
    anchor_concept: str
    anchor_concept_weight: float
    current_concept: str
    review: ReviewResponse | None
    review_record: ReviewRecord | None
    review_history: list[ReviewRecord]
    student_profile: StudentProfileScoring | None
    latest_submission: SubmissionRecord | None
    previous_review_payload: dict | None
    previous_submission_payload: dict | None
    mastered_concepts: list[str]
    attempted_exercise_ids: list[str]
    critical_errors: int
    latest_review_improvement_signal: float
    latest_review_severity_change: float
    latest_submission_improvement_ratio: float
    latest_submission_regression_ratio: float
    exercise_graph: dict
    concept_progression: list[dict]
    assigned_path: AssignedPath
    path_decision_confidence: float
    path_decision_reason: str
    focus_concept_id: str
    reasoning: dict
    framework: RecommendationScoringFramework
    graph_summary: dict
    retrieved_candidates: list[dict]
    selected_candidates: list[dict]
    selected_exercises: list[ExerciseRecord]
    roadmap_directives: list[str]
    roadmap_summary: dict
