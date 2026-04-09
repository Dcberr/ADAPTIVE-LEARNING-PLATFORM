from pydantic import BaseModel, Field

from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath, ConceptRecord, KnowledgeGraphDocument
from app.models.student_profile import StudentProfileScoring
from app.models.student_record import StudentRecord


class UpsertConceptRequest(BaseModel):
    concept_id: str
    name: str
    description: str = ""
    difficulty: int = 1
    prerequisite_ids: list[str] = Field(default_factory=list)


class UpsertExerciseRequest(BaseModel):
    exercise_id: str
    title: str
    description: str
    content: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    recommended_paths: list[AssignedPath] = Field(default_factory=list)


class UpsertStudentRequest(BaseModel):
    student_id: str
    current_concept: str = ""
    mastered_concepts: list[str] = Field(default_factory=list)
    attempted_exercise_ids: list[str] = Field(default_factory=list)
    student_profile: StudentProfileScoring
    notes: str = ""


class KnowledgeGraphConceptResponse(BaseModel):
    concept: ConceptRecord


class KnowledgeGraphExerciseResponse(BaseModel):
    exercise: ExerciseRecord


class KnowledgeGraphStudentResponse(BaseModel):
    student: StudentRecord


class KnowledgeGraphSnapshotResponse(BaseModel):
    graph: KnowledgeGraphDocument
