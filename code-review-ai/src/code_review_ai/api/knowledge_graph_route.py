import logging

from fastapi import APIRouter, Depends, HTTPException

from code_review_ai.api.knowledge_graph_deps import (
    get_knowledge_graph_service,
)
from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsRequest,
    BatchUpsertExercisesRequest,
    KnowledgeGraphConceptResponse,
    KnowledgeGraphExerciseResponse,
    KnowledgeGraphExercisesBatchResponse,
    KnowledgeGraphReviewResponse,
    KnowledgeGraphStudentResponse,
    KnowledgeGraphSubmissionResponse,
    PatchConceptRelationsRequest,
    PatchExerciseRelationsRequest,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertReviewRequest,
    UpsertStudentRequest,
    UpsertSubmissionRequest,
)
from code_review_ai.services.knowledge_graph_service import (
    KnowledgeGraphService,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/knowledgegraph/concepts/{concept_slug}",
    response_model=KnowledgeGraphConceptResponse,
)
async def upsert_concept(
    concept_slug: str,
    request: UpsertConceptRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        concept = knowledge_graph_service.upsert_concept(concept_slug, request)
        return KnowledgeGraphConceptResponse(concept=concept)
    except Exception as exc:
        logger.exception("Concept upsert failed")
        raise HTTPException(status_code=500, detail=f"Concept upsert failed: {exc}")


@router.patch(
    "/knowledgegraph/concepts/{concept_slug}/relations",
    response_model=KnowledgeGraphConceptResponse,
)
async def patch_concept_relations(
    concept_slug: str,
    request: PatchConceptRelationsRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        concept = knowledge_graph_service.patch_concept_relations(concept_slug, request)
        return KnowledgeGraphConceptResponse(concept=concept)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Concept relation update failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Concept relation update failed")
        raise HTTPException(
            status_code=500, detail=f"Concept relation update failed: {exc}"
        )


@router.put(
    "/knowledgegraph/exercises/batch",
    response_model=KnowledgeGraphExercisesBatchResponse,
)
async def batch_upsert_exercises(
    request: BatchUpsertExercisesRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        exercises = knowledge_graph_service.batch_upsert_exercises(request)
        return KnowledgeGraphExercisesBatchResponse(exercises=exercises)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Exercise batch upsert failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Exercise batch upsert failed")
        raise HTTPException(
            status_code=500, detail=f"Exercise batch upsert failed: {exc}"
        )


@router.patch(
    "/knowledgegraph/exercises/relations/batch",
    response_model=KnowledgeGraphExercisesBatchResponse,
)
async def batch_patch_exercise_relations(
    request: BatchPatchExerciseRelationsRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        exercises = knowledge_graph_service.batch_patch_exercise_relations(request)
        return KnowledgeGraphExercisesBatchResponse(exercises=exercises)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Exercise batch relation update failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Exercise batch relation update failed")
        raise HTTPException(
            status_code=500,
            detail=f"Exercise batch relation update failed: {exc}",
        )


@router.put(
    "/knowledgegraph/exercises/{exercise_id}",
    response_model=KnowledgeGraphExerciseResponse,
)
async def upsert_exercise(
    exercise_id: str,
    request: UpsertExerciseRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        exercise = knowledge_graph_service.upsert_exercise(exercise_id, request)
        return KnowledgeGraphExerciseResponse(exercise=exercise)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Exercise upsert failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Exercise upsert failed")
        raise HTTPException(status_code=500, detail=f"Exercise upsert failed: {exc}")


@router.patch(
    "/knowledgegraph/exercises/{exercise_id}/relations",
    response_model=KnowledgeGraphExerciseResponse,
)
async def patch_exercise_relations(
    exercise_id: str,
    request: PatchExerciseRelationsRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        exercise = knowledge_graph_service.patch_exercise_relations(exercise_id, request)
        return KnowledgeGraphExerciseResponse(exercise=exercise)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Exercise relation update failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Exercise relation update failed")
        raise HTTPException(
            status_code=500, detail=f"Exercise relation update failed: {exc}"
        )


@router.put(
    "/knowledgegraph/students/{student_id}",
    response_model=KnowledgeGraphStudentResponse,
)
async def upsert_student(
    student_id: str,
    request: UpsertStudentRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    del request
    try:
        student_id = knowledge_graph_service.upsert_student(student_id)
        return KnowledgeGraphStudentResponse(student_id=student_id)
    except Exception as exc:
        logger.exception("Student upsert failed")
        raise HTTPException(status_code=500, detail=f"Student upsert failed: {exc}")


@router.put(
    "/knowledgegraph/submissions/{submission_id}",
    response_model=KnowledgeGraphSubmissionResponse,
)
async def upsert_submission(
    submission_id: str,
    request: UpsertSubmissionRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        submission = knowledge_graph_service.upsert_submission(submission_id, request)
        return KnowledgeGraphSubmissionResponse(submission=submission)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Submission upsert failed")
        raise HTTPException(status_code=500, detail=f"Submission upsert failed: {exc}")


@router.put(
    "/knowledgegraph/reviews/{review_id}", response_model=KnowledgeGraphReviewResponse
)
async def upsert_review(
    review_id: str,
    request: UpsertReviewRequest,
    knowledge_graph_service: KnowledgeGraphService = Depends(
        get_knowledge_graph_service
    ),
):
    try:
        review = knowledge_graph_service.upsert_review(review_id, request)
        return KnowledgeGraphReviewResponse(review=review)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Review upsert failed")
        raise HTTPException(status_code=500, detail=f"Review upsert failed: {exc}")
