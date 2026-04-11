from typing import Literal

from pydantic import BaseModel

from app.models.exercise_record import ExerciseRecord
from app.models.recommendation_framework import RecommendationScoringFramework


class RecommendationRequest(BaseModel):
    student_id: str
    exercise_id: str


class RecommendationExercise(ExerciseRecord):
    path: Literal["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]
    target_concept: str
    directive: str


class RecommendationRoadmapStep(BaseModel):
    step: int
    focus: str
    exercise: RecommendationExercise


class RecommendationResponse(BaseModel):
    student_id: str
    assigned_path: Literal["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]
    target_concept: str
    critical_errors: int
    framework: RecommendationScoringFramework
    reasoning: str
    roadmap_summary: str
    roadmap: list[RecommendationRoadmapStep]
