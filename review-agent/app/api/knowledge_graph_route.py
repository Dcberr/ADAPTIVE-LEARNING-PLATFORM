import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.knowledge_graph_deps import get_knowledge_graph_repository
from app.api.knowledge_graph_schema import (
    KnowledgeGraphConceptResponse,
    KnowledgeGraphExerciseResponse,
    KnowledgeGraphSnapshotResponse,
    KnowledgeGraphStudentResponse,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertStudentRequest,
)
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import ConceptRecord
from app.models.student_record import StudentRecord
from app.services.knowledge_graph_repository import KnowledgeGraphRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/knowledgegraph/concepts", response_model=KnowledgeGraphConceptResponse)
async def upsert_concept(
    request: UpsertConceptRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        concept = repository.upsert_concept(
            ConceptRecord(
                concept_id=request.concept_id,
                name=request.name,
                description=request.description,
                difficulty=request.difficulty,
            ),
            prerequisite_ids=request.prerequisite_ids,
        )
        return KnowledgeGraphConceptResponse(concept=concept)
    except Exception as exc:
        logger.exception("Concept upsert failed")
        raise HTTPException(status_code=500, detail=f"Concept upsert failed: {exc}")


@router.post("/knowledgegraph/exercises", response_model=KnowledgeGraphExerciseResponse)
async def upsert_exercise(
    request: UpsertExerciseRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        exercise = repository.upsert_exercise(
            ExerciseRecord(
                exercise_id=request.exercise_id,
                title=request.title,
                description=request.description,
                content=request.content,
                difficulty=request.difficulty,
                tags=request.tags,
            ),
            concept_ids=request.concept_ids,
            recommended_paths=request.recommended_paths,
        )
        return KnowledgeGraphExerciseResponse(exercise=exercise)
    except Exception as exc:
        logger.exception("Exercise upsert failed")
        raise HTTPException(status_code=500, detail=f"Exercise upsert failed: {exc}")


@router.post("/knowledgegraph/students", response_model=KnowledgeGraphStudentResponse)
async def upsert_student(
    request: UpsertStudentRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        student = repository.upsert_student(
            student=StudentRecord(
                student_id=request.student_id,
                current_concept=request.current_concept,
                notes=request.notes,
            ),
            student_profile=request.student_profile,
            mastered_concepts=request.mastered_concepts,
            attempted_exercise_ids=request.attempted_exercise_ids,
        )
        return KnowledgeGraphStudentResponse(student=student)
    except Exception as exc:
        logger.exception("Student upsert failed")
        raise HTTPException(status_code=500, detail=f"Student upsert failed: {exc}")


@router.get("/knowledgegraph", response_model=KnowledgeGraphSnapshotResponse)
async def get_knowledge_graph_snapshot(
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        return KnowledgeGraphSnapshotResponse(graph=repository.get_graph_snapshot())
    except Exception as exc:
        logger.exception("Knowledge graph read failed")
        raise HTTPException(status_code=500, detail=f"Knowledge graph read failed: {exc}")
