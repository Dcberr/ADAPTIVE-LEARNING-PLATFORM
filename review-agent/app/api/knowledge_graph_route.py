import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.knowledge_graph_deps import get_knowledge_graph_repository
from app.api.knowledge_graph_deps import get_exercise_weight_agent
from app.api.knowledge_graph_deps import get_prerequisite_weight_agent
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
from app.agents.exercise_weight_agent import ExerciseWeightAgent
from app.agents.prerequisite_weight_agent import PrerequisiteWeightAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/knowledgegraph/concepts/{concept_id}",
    response_model=KnowledgeGraphConceptResponse,
)
async def upsert_concept(
    concept_id: str,
    request: UpsertConceptRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    prerequisite_weight_agent: PrerequisiteWeightAgent = Depends(
        get_prerequisite_weight_agent
    ),
):
    try:
        prerequisite_map = repository.get_concepts_by_ids(request.prerequisite_ids)
        missing_prerequisites = [
            concept_id
            for concept_id in request.prerequisite_ids
            if concept_id not in prerequisite_map
        ]
        if missing_prerequisites:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Concept upsert failed: prerequisite concept(s) not found: "
                    + ", ".join(missing_prerequisites)
                ),
            )

        main_concept = ConceptRecord(
            concept_id=concept_id,
            name=request.name,
            description=request.description,
            difficulty=request.difficulty,
        )
        prerequisite_strengths = prerequisite_weight_agent.evaluate(
            main_concept=main_concept,
            prerequisites=[
                prerequisite_map[prerequisite_id]
                for prerequisite_id in request.prerequisite_ids
            ],
        )
        concept = repository.upsert_concept(
            main_concept,
            prerequisites=[
                (
                    prerequisite_map[prerequisite_id],
                    prerequisite_strengths.get(
                        prerequisite_id,
                        PrerequisiteWeightAgent.DEFAULT_STRENGTH,
                    ),
                )
                for prerequisite_id in request.prerequisite_ids
            ],
        )
        return KnowledgeGraphConceptResponse(concept=concept)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Concept upsert failed")
        raise HTTPException(status_code=500, detail=f"Concept upsert failed: {exc}")


@router.put(
    "/knowledgegraph/exercises/{exercise_id}",
    response_model=KnowledgeGraphExerciseResponse,
)
async def upsert_exercise(
    exercise_id: str,
    request: UpsertExerciseRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    exercise_weight_agent: ExerciseWeightAgent = Depends(get_exercise_weight_agent),
):
    try:
        main_exercise = ExerciseRecord(
            exercise_id=exercise_id,
            title=request.title,
            description=request.description,
            content=request.content,
            difficulty=request.difficulty,
            tags=request.tags,
        )
        concept_map = repository.get_concepts_by_ids(request.concept_ids)
        missing_concepts = [
            concept_id for concept_id in request.concept_ids if concept_id not in concept_map
        ]
        if missing_concepts:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Exercise upsert failed: concept(s) not found: "
                    + ", ".join(missing_concepts)
                ),
            )

        related_exercise_map = repository.get_exercises_by_ids(request.related_exercise_ids)
        missing_related_exercises = [
            exercise_id
            for exercise_id in request.related_exercise_ids
            if exercise_id not in related_exercise_map
        ]
        if missing_related_exercises:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Exercise upsert failed: related exercise(s) not found: "
                    + ", ".join(missing_related_exercises)
                ),
            )

        concept_records = [
            concept_map[concept_id] for concept_id in request.concept_ids
        ]
        related_exercise_records = [
            related_exercise_map[exercise_id]
            for exercise_id in request.related_exercise_ids
        ]
        (
            concept_weights,
            concept_recommended_paths,
            related_exercise_weights,
        ) = exercise_weight_agent.evaluate(
            main_exercise=main_exercise,
            concepts=concept_records,
            related_exercises=related_exercise_records,
        )
        exercise = repository.upsert_exercise(
            main_exercise,
            concepts=[
                (
                    concept_record,
                    concept_weights.get(
                        concept_record.concept_id, ExerciseWeightAgent.DEFAULT_WEIGHT
                    ),
                    concept_recommended_paths.get(concept_record.concept_id, []),
                )
                for concept_record in concept_records
            ],
            related_exercises=[
                (
                    related_record,
                    related_exercise_weights.get(
                        related_record.exercise_id,
                        dict(ExerciseWeightAgent.DEFAULT_RELATION_METADATA),
                    ),
                )
                for related_record in related_exercise_records
            ],
        )
        return KnowledgeGraphExerciseResponse(exercise=exercise)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Exercise upsert failed")
        raise HTTPException(status_code=500, detail=f"Exercise upsert failed: {exc}")


@router.put(
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


@router.put(
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


@router.put(
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
