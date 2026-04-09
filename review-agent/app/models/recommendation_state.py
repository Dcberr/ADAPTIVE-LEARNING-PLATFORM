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
    current_concept: str
    review: ReviewResponse | None
    review_history: list[ReviewRecord]
    student_profile: StudentProfileScoring | None
    mastered_concepts: list[str]
    attempted_exercise_ids: list[str]
    critical_errors: int
    assigned_path: AssignedPath
    target_concept: str
    reasoning: str
    framework: RecommendationScoringFramework
    retrieved_candidates: list[dict]
    selected_exercises: list[ExerciseRecord]
    roadmap_directives: list[str]
