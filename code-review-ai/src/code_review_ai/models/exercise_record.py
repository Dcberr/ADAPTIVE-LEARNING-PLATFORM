from pydantic import BaseModel, Field


class ExerciseRecord(BaseModel):
    exercise_id: str
    slug: str = ""
    title: str
    description: str
    content: str
    difficulty: str
    concept_slugs: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list, exclude=True)
    embedding_model: str = Field(default="", exclude=True)
    content_hash: str = Field(default="", exclude=True)
