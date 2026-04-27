import logging

from fastapi import APIRouter, Depends, HTTPException

from code_review_ai.api.knowledge_graph_deps import get_knowledge_graph_repository
from code_review_ai.api.knowledge_graph_deps import get_exercise_weight_agent
from code_review_ai.api.knowledge_graph_deps import get_prerequisite_weight_agent
from code_review_ai.api.knowledge_graph_schema import (
    KnowledgeGraphConceptResponse,
    PatchConceptRelationsRequest,
    PatchExerciseRelationsRequest,
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
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from code_review_ai.agents.exercise_weight_agent import ExerciseWeightAgent
from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/knowledgegraph/concepts/{concept_slug}",
    response_model=KnowledgeGraphConceptResponse,
)
async def upsert_concept(
    concept_slug: str,
    request: UpsertConceptRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        main_concept = ConceptRecord(
            concept_id=concept_slug,
            slug=concept_slug,
            name=request.name,
            description=request.description,
            difficulty=request.difficulty,
        )
        concept = repository.upsert_concept(main_concept)
        return KnowledgeGraphConceptResponse(concept=concept)
    except HTTPException:
        raise
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
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    prerequisite_weight_agent: PrerequisiteWeightAgent = Depends(
        get_prerequisite_weight_agent
    ),
):
    try:
        concept_matches = repository.get_concepts_by_slugs([concept_slug]).get(
            concept_slug, []
        )
        if not concept_matches:
            raise HTTPException(
                status_code=404,
                detail=f"Concept relation update failed: concept '{concept_slug}' not found",
            )
        concept = concept_matches[0]

        if request.prerequisite_slugs is not None:
            prerequisite_slug_map = repository.get_concepts_by_slugs(
                request.prerequisite_slugs
            )
            missing_prerequisites = [
                prerequisite_slug
                for prerequisite_slug in request.prerequisite_slugs
                if not prerequisite_slug_map.get(prerequisite_slug)
            ]
            if missing_prerequisites:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Concept relation update failed: prerequisite concept slug(s) not found: "
                        + ", ".join(missing_prerequisites)
                    ),
                )
            prerequisite_records: list[ConceptRecord] = []
            seen_concept_ids: set[str] = {concept.concept_id}
            for prerequisite_slug in request.prerequisite_slugs:
                for prerequisite in prerequisite_slug_map.get(prerequisite_slug, []):
                    if prerequisite.concept_id in seen_concept_ids:
                        continue
                    prerequisite_records.append(prerequisite)
                    seen_concept_ids.add(prerequisite.concept_id)

            prerequisite_strengths = prerequisite_weight_agent.evaluate(
                main_concept=concept,
                prerequisites=prerequisite_records,
            )
            repository.replace_concept_prerequisites(
                concept_slug=concept_slug,
                prerequisites=[
                    (
                        prerequisite,
                        prerequisite_strengths.get(
                            prerequisite.concept_id,
                            PrerequisiteWeightAgent.DEFAULT_STRENGTH,
                        ),
                    )
                    for prerequisite in prerequisite_records
                ],
            )

        return KnowledgeGraphConceptResponse(concept=concept)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Concept relation update failed")
        raise HTTPException(
            status_code=500, detail=f"Concept relation update failed: {exc}"
        )


@router.put(
    "/knowledgegraph/exercises/{exercise_id}",
    response_model=KnowledgeGraphExerciseResponse,
)
async def upsert_exercise(
    exercise_id: str,
    request: UpsertExerciseRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        main_exercise = ExerciseRecord(
            exercise_id=exercise_id,
            slug=request.slug,
            title=request.title,
            description=request.description,
            content=request.content,
            difficulty=request.difficulty,
            tags=request.tags,
        )
        exercise = repository.upsert_exercise(main_exercise)
        return KnowledgeGraphExerciseResponse(exercise=exercise)
    except HTTPException:
        raise
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
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    exercise_weight_agent: ExerciseWeightAgent = Depends(get_exercise_weight_agent),
):
    try:
        exercise = repository.get_exercises_by_ids([exercise_id]).get(exercise_id)
        if exercise is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exercise relation update failed: exercise '{exercise_id}' not found",
            )

        concept_records: list[ConceptRecord]
        should_update_concepts = request.concept_slugs is not None
        if should_update_concepts:
            concept_slug_map = repository.get_concepts_by_slugs(request.concept_slugs or [])
            ignored_concept_slugs = [
                concept_slug
                for concept_slug in (request.concept_slugs or [])
                if not concept_slug_map.get(concept_slug)
            ]
            if ignored_concept_slugs:
                logger.info(
                    "Ignoring missing concept slug(s) while updating exercise '%s' relations: %s",
                    exercise_id,
                    ", ".join(ignored_concept_slugs),
                )

            concept_records = []
            seen_concept_ids: set[str] = set()
            for concept_slug in request.concept_slugs or []:
                for record in concept_slug_map.get(concept_slug, []):
                    if record.concept_id in seen_concept_ids:
                        continue
                    concept_records.append(record)
                    seen_concept_ids.add(record.concept_id)
        else:
            existing_concept_ids = repository.get_concept_ids_by_exercise([exercise_id]).get(
                exercise_id, []
            )
            existing_concepts = repository.get_concepts_by_ids(existing_concept_ids)
            concept_records = [
                existing_concepts[concept_id]
                for concept_id in existing_concept_ids
                if concept_id in existing_concepts
            ]

        related_exercise_records: list[ExerciseRecord] = []
        should_update_related_exercises = (
            request.related_exercise_ids is not None
            or request.related_exercise_slugs is not None
        )
        if should_update_related_exercises:
            related_exercise_map = repository.get_exercises_by_ids(
                request.related_exercise_ids or []
            )
            missing_related_exercises = [
                related_exercise_id
                for related_exercise_id in (request.related_exercise_ids or [])
                if related_exercise_id not in related_exercise_map
            ]
            if missing_related_exercises:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Exercise relation update failed: related exercise(s) not found: "
                        + ", ".join(missing_related_exercises)
                    ),
                )

            related_exercise_slug_map = repository.get_exercises_by_slugs(
                request.related_exercise_slugs or []
            )
            missing_related_exercise_slugs = [
                exercise_slug
                for exercise_slug in (request.related_exercise_slugs or [])
                if not related_exercise_slug_map.get(exercise_slug)
            ]
            if missing_related_exercise_slugs:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Exercise relation update failed: related exercise slug(s) not found: "
                        + ", ".join(missing_related_exercise_slugs)
                    ),
                )

            related_exercise_records = []
            seen_related_ids: set[str] = {exercise_id}
            for related_exercise_id in request.related_exercise_ids or []:
                record = related_exercise_map[related_exercise_id]
                if record.exercise_id in seen_related_ids:
                    continue
                related_exercise_records.append(record)
                seen_related_ids.add(record.exercise_id)
            for exercise_slug in request.related_exercise_slugs or []:
                for record in related_exercise_slug_map.get(exercise_slug, []):
                    if record.exercise_id in seen_related_ids:
                        continue
                    related_exercise_records.append(record)
                    seen_related_ids.add(record.exercise_id)

        (
            concept_weights,
            concept_recommended_paths,
            related_exercise_weights,
        ) = exercise_weight_agent.evaluate(
            main_exercise=exercise,
            concepts=concept_records,
            related_exercises=related_exercise_records,
        )

        if should_update_concepts:
            repository.replace_exercise_concepts(
                exercise_id=exercise_id,
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
            )

        if should_update_related_exercises:
            repository.replace_exercise_related_exercises(
                exercise_id=exercise_id,
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
