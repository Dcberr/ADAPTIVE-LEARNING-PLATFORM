import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.knowledge_graph_deps import get_knowledge_graph_repository
from app.api.knowledge_graph_schema import (
    KnowledgeGraphConceptResponse,
    KnowledgeGraphReviewResponse,
    KnowledgeGraphExerciseResponse,
    KnowledgeGraphSnapshotResponse,
    KnowledgeGraphStudentResponse,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertReviewRequest,
    UpsertSubmissionRequest,
    UpsertStudentProfileRequest,
    KnowledgeGraphSubmissionResponse,
)
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import ConceptRecord
from app.services.knowledge_graph_repository import KnowledgeGraphRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.patch(
    "/knowledgegraph/concepts/{concept_id}",
    response_model=KnowledgeGraphConceptResponse,
)
async def upsert_concept(
    concept_id: str,
    request: UpsertConceptRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        concept = repository.upsert_concept(
            ConceptRecord(
                concept_id=concept_id,
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


@router.patch(
    "/knowledgegraph/exercises/{exercise_id}",
    response_model=KnowledgeGraphExerciseResponse,
)
async def upsert_exercise(
    exercise_id: str,
    request: UpsertExerciseRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        exercise = repository.upsert_exercise(
            ExerciseRecord(
                exercise_id=exercise_id,
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


@router.patch(
    "/knowledgegraph/students/{student_id}",
    response_model=KnowledgeGraphStudentResponse,
)
async def upsert_student(
    student_id: str,
    request: UpsertStudentProfileRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        student_profile = repository.upsert_student(
            student_id=student_id,
            student_profile=request.student_profile,
        )
        return KnowledgeGraphStudentResponse(
            student_id=student_id,
            student_profile=student_profile,
        )
    except Exception as exc:
        logger.exception("Student upsert failed")
        raise HTTPException(status_code=500, detail=f"Student upsert failed: {exc}")


@router.patch(
    "/knowledgegraph/submissions/{submission_id}",
    response_model=KnowledgeGraphSubmissionResponse,
)
async def upsert_submission(
    submission_id: str,
    request: UpsertSubmissionRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        submission = repository.upsert_submission(
            submission_id=submission_id,
            student_id=request.student_id,
            exercise_id=request.exercise_id,
            code=request.code,
            testcase_outputs=[item.model_dump() for item in request.testcase_outputs],
        )
        return KnowledgeGraphSubmissionResponse(submission=submission)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Submission upsert failed")
        raise HTTPException(status_code=500, detail=f"Submission upsert failed: {exc}")


@router.patch(
    "/knowledgegraph/reviews/{review_id}", response_model=KnowledgeGraphReviewResponse
)
async def upsert_review(
    review_id: str,
    request: UpsertReviewRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        review = repository.upsert_review(
            review_id=review_id,
            submission_id=request.submission_id,
            summary=request.summary,
            detail=request.detail,
            review_items=[item.model_dump() for item in request.review_items],
            scorecard=request.scorecard.model_dump(),
            current_concept=request.current_concept,
        )
        return KnowledgeGraphReviewResponse(review=review)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Review upsert failed")
        raise HTTPException(status_code=500, detail=f"Review upsert failed: {exc}")


@router.get("/knowledgegraph", response_model=KnowledgeGraphSnapshotResponse)
async def get_knowledge_graph_snapshot(
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        return KnowledgeGraphSnapshotResponse(graph=repository.get_graph_snapshot())
    except Exception as exc:
        logger.exception("Knowledge graph read failed")
        raise HTTPException(
            status_code=500, detail=f"Knowledge graph read failed: {exc}"
        )
