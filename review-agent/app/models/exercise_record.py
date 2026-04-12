from pydantic import BaseModel, Field


class ExerciseRecord(BaseModel):
    exercise_id: str
    title: str
    description: str
    content: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
