from typing import TypedDict

from app.api.review_code_schema import ReviewResponse
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath
from app.models.recommendation_framework import RecommendationScoringFramework
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring


class RecommendationState(TypedDict):
    student_id: str
    exercise_id: str
    planner_start_entity: str
    planner_query_plan_id: str
    planner_confidence: float
    planner_rationale: str
    planner_target_concept_hint: str
    anchor_concept: str
    anchor_concept_weight: float
    current_concept: str
    review: ReviewResponse | None
    review_history: list[ReviewRecord]
    student_profile: StudentProfileScoring | None
    mastered_concepts: list[str]
    attempted_exercise_ids: list[str]
    critical_errors: int
    latest_review_improvement_signal: float
    latest_review_severity_change: float
    latest_submission_improvement_ratio: float
    latest_submission_regression_ratio: float
    assigned_path: AssignedPath
    target_concept: str
    reasoning: str
    framework: RecommendationScoringFramework
    graph_summary: dict
    retrieved_candidates: list[dict]
    target_concept_candidates: list[dict]
    selected_exercises: list[ExerciseRecord]
    roadmap_directives: list[str]
    roadmap_summary: str
