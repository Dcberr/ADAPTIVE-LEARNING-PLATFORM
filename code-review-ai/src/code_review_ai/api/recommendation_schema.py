from pydantic import BaseModel

from code_review_ai.models.exercise_record import ExerciseRecord
class RecommendationRequest(BaseModel):
    student_id: str
    exercise_id: str


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
