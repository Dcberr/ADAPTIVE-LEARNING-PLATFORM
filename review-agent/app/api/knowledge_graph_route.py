import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.knowledge_graph_deps import get_knowledge_graph_repository
from app.api.knowledge_graph_schema import (
    KnowledgeGraphConceptResponse,
    KnowledgeGraphReviewResponse,
    KnowledgeGraphExerciseResponse,
    KnowledgeGraphSnapshotResponse,
    KnowledgeGraphStudentProfileResponse,
    KnowledgeGraphStudentResponse,
    RecalculateStudentProfileRequest,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertReviewRequest,
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


@router.post("/knowledgegraph/reviews", response_model=KnowledgeGraphReviewResponse)
async def upsert_review(
    request: UpsertReviewRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        review = repository.upsert_review(
            student_id=request.student_id,
            exercise_id=request.exercise_id,
            submission_id=request.submission_id,
            summary=request.summary,
            detail=request.detail,
            review_items=[item.model_dump() for item in request.review_items],
            scorecard=request.scorecard.model_dump(),
            current_concept=request.current_concept,
            review_id=request.review_id,
        )
        return KnowledgeGraphReviewResponse(review=review)
    except Exception as exc:
        logger.exception("Review upsert failed")
        raise HTTPException(status_code=500, detail=f"Review upsert failed: {exc}")


@router.patch(
    "/knowledgegraph/students/{student_id}/profile",
    response_model=KnowledgeGraphStudentProfileResponse,
)
async def recalculate_student_profile(
    student_id: str,
    request: RecalculateStudentProfileRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        student_profile = repository.recalculate_student_profile_from_review(
            student_id=student_id,
            exercise_id=request.exercise_id,
            current_concept=request.current_concept,
            scorecard=request.scorecard.model_dump(),
        )
        return KnowledgeGraphStudentProfileResponse(
            student_id=student_id,
            exercise_id=request.exercise_id,
            current_concept=request.current_concept,
            student_profile=student_profile,
        )
    except Exception as exc:
        logger.exception("Student profile recalculation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Student profile recalculation failed: {exc}",
        )


@router.get("/knowledgegraph", response_model=KnowledgeGraphSnapshotResponse)
async def get_knowledge_graph_snapshot(
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        return KnowledgeGraphSnapshotResponse(graph=repository.get_graph_snapshot())
    except Exception as exc:
        logger.exception("Knowledge graph read failed")
        raise HTTPException(status_code=500, detail=f"Knowledge graph read failed: {exc}")
