import logging

from fastapi import APIRouter, Depends, HTTPException

from code_review_ai.api.knowledge_graph_deps import get_knowledge_graph_repository
from code_review_ai.api.knowledge_graph_deps import get_exercise_embedding_service
from code_review_ai.api.knowledge_graph_deps import get_exercise_relation_scoring_service
from code_review_ai.api.knowledge_graph_deps import get_prerequisite_weight_agent
from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsItem,
    BatchPatchExerciseRelationsRequest,
    BatchUpsertExercisesRequest,
    KnowledgeGraphConceptResponse,
    PatchConceptRelationsRequest,
    PatchExerciseRelationsRequest,
    KnowledgeGraphReviewResponse,
    KnowledgeGraphExercisesBatchResponse,
    KnowledgeGraphExerciseResponse,
    KnowledgeGraphStudentResponse,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertReviewRequest,
    UpsertSubmissionRequest,
    UpsertStudentRequest,
    KnowledgeGraphSubmissionResponse,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from code_review_ai.services.exercise_embedding_service import ExerciseEmbeddingService
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
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
        concept = repository.upsert_concepts([main_concept])[0]
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
            repository.replace_concept_prerequisites_batch(
                [
                    {
                        "concept_slug": concept_slug,
                        "prerequisites": [
                            (
                                prerequisite,
                                prerequisite_strengths.get(
                                    prerequisite.concept_id,
                                    PrerequisiteWeightAgent.DEFAULT_STRENGTH,
                                ),
                            )
                            for prerequisite in prerequisite_records
                        ],
                    }
                ]
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
    "/knowledgegraph/exercises/batch",
    response_model=KnowledgeGraphExercisesBatchResponse,
)
async def batch_upsert_exercises(
    request: BatchUpsertExercisesRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    exercise_embedding_service: ExerciseEmbeddingService = Depends(
        get_exercise_embedding_service
    ),
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
):
    try:
        concept_slug_map = repository.get_concepts_by_slugs(
            [
                concept_slug
                for item in request.exercises
                for concept_slug in item.concept_slugs
            ]
        )
        missing_concept_slugs = sorted(
            {
                concept_slug
                for item in request.exercises
                for concept_slug in item.concept_slugs
                if not concept_slug_map.get(concept_slug)
            }
        )
        if missing_concept_slugs:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Exercise batch upsert failed: concept slug(s) not found: "
                    + ", ".join(missing_concept_slugs)
                ),
            )

        exercises = exercise_embedding_service.hydrate_exercises(
            [
                ExerciseRecord(
                    exercise_id=item.exercise_id,
                    slug=item.slug,
                    title=item.title,
                    description=item.description,
                    content=item.content,
                    difficulty=item.difficulty,
                    concept_slugs=item.concept_slugs,
                )
                for item in request.exercises
            ]
        )
        exercises = repository.upsert_exercises(exercises)
        repository.replace_exercise_concepts_batch(
            [
                {
                    "exercise_id": exercise.exercise_id,
                    "concepts": [
                        (
                            concept_record,
                            concept_weights[concept_record.concept_id],
                            recommended_weights[concept_record.concept_id],
                        )
                        for concept_record in concept_records
                    ],
                }
                for exercise, concept_records, concept_weights, recommended_weights in [
                    (
                        exercise,
                        [
                            record
                            for concept_slug in exercise.concept_slugs
                            for record in concept_slug_map.get(concept_slug, [])
                        ],
                        *exercise_relation_scoring_service.evaluate_exercise_concepts(
                            main_exercise=exercise,
                            concepts=[
                                record
                                for concept_slug in exercise.concept_slugs
                                for record in concept_slug_map.get(concept_slug, [])
                            ],
                        ),
                    )
                    for exercise in exercises
                ]
            ]
        )
        return KnowledgeGraphExercisesBatchResponse(exercises=exercises)
    except HTTPException:
        raise
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
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
):
    try:
        exercises_by_id = repository.get_exercises_by_ids(
            [item.exercise_id for item in request.exercises]
        )
        missing_exercise_ids = [
            item.exercise_id
            for item in request.exercises
            if item.exercise_id not in exercises_by_id
        ]
        if missing_exercise_ids:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Exercise relation update failed: exercise(s) not found: "
                    + ", ".join(missing_exercise_ids)
                ),
            )

        concept_slug_map = repository.get_concepts_by_slugs(
            list(
                dict.fromkeys(
                    [
                        concept_slug
                        for exercise in exercises_by_id.values()
                        for concept_slug in exercise.concept_slugs
                    ]
                    + [
                        concept_slug
                        for item in request.exercises
                        for concept_slug in (item.concept_slugs or [])
                    ]
                )
            )
        )

        related_exercise_slugs = [
            related_exercise_slug
            for item in request.exercises
            for related_exercise_slug in (item.related_exercise_slugs or [])
        ]
        related_exercises_by_slug = repository.get_exercises_by_slugs(
            related_exercise_slugs
        )

        prepared_items = []
        response_exercises: list[ExerciseRecord] = []
        for item in request.exercises:
            stored_exercise = exercises_by_id[item.exercise_id]

            should_update_concepts = item.concept_slugs is not None
            if should_update_concepts:
                missing_concept_slugs = [
                    concept_slug
                    for concept_slug in (item.concept_slugs or [])
                    if not concept_slug_map.get(concept_slug)
                ]
                if missing_concept_slugs:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Exercise relation update failed: concept slug(s) not found: "
                            + ", ".join(missing_concept_slugs)
                        ),
                    )

                merged_concept_slugs = list(
                    dict.fromkeys(
                        [
                            concept_slug.strip()
                            for concept_slug in (
                                list(stored_exercise.concept_slugs)
                                + list(item.concept_slugs or [])
                            )
                            if concept_slug.strip()
                        ]
                    )
                )
                exercise = stored_exercise.model_copy(
                    update={"concept_slugs": merged_concept_slugs}
                )
                concept_records = [
                    record
                    for concept_slug in merged_concept_slugs
                    for record in concept_slug_map.get(concept_slug, [])
                ]
            else:
                exercise = stored_exercise
                concept_records = []

            response_exercises.append(exercise)

            should_update_related_exercises = (
                item.related_exercise_slugs is not None
            )
            related_exercise_records: list[ExerciseRecord] = []
            if should_update_related_exercises:
                missing_related_exercise_slugs = [
                    related_exercise_slug
                    for related_exercise_slug in (item.related_exercise_slugs or [])
                    if not related_exercises_by_slug.get(related_exercise_slug)
                ]
                if missing_related_exercise_slugs:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Exercise relation update failed: related exercise slug(s) not found: "
                            + ", ".join(missing_related_exercise_slugs)
                        ),
                    )

                seen_related_ids: set[str] = {item.exercise_id}
                for related_exercise_slug in item.related_exercise_slugs or []:
                    for record in related_exercises_by_slug.get(
                        related_exercise_slug, []
                    ):
                        if record.exercise_id in seen_related_ids:
                            continue
                        related_exercise_records.append(record)
                        seen_related_ids.add(record.exercise_id)

            prepared_items.append(
                {
                    "exercise": exercise,
                    "concept_records": concept_records,
                    "should_update_concepts": should_update_concepts,
                    "related_exercise_records": related_exercise_records,
                    "related_concept_slugs_by_exercise": {
                        record.exercise_id: record.concept_slugs
                        for record in related_exercise_records
                    },
                    "should_update_related_exercises": should_update_related_exercises,
                }
            )

        evaluated_items = []
        for prepared_item in prepared_items:
            (
                concept_weights,
                concept_recommended_weights,
                related_exercise_weights,
            ) = exercise_relation_scoring_service.evaluate(
                main_exercise=prepared_item["exercise"],
                concepts=prepared_item["concept_records"],
                related_exercises=prepared_item["related_exercise_records"],
                main_concept_slugs=prepared_item["exercise"].concept_slugs,
                related_concept_slugs_by_exercise=prepared_item[
                    "related_concept_slugs_by_exercise"
                ],
            )
            evaluated_items.append(
                {
                    **prepared_item,
                    "concept_weights": concept_weights,
                    "concept_recommended_weights": concept_recommended_weights,
                    "related_exercise_weights": related_exercise_weights,
                }
            )

        repository.upsert_exercises(
            [
                evaluated_item["exercise"]
                for evaluated_item in evaluated_items
                if evaluated_item["should_update_concepts"]
            ]
        )

        repository.replace_exercise_concepts_batch(
            [
                {
                    "exercise_id": evaluated_item["exercise"].exercise_id,
                    "concepts": [
                        (
                            concept_record,
                            evaluated_item["concept_weights"][concept_record.concept_id],
                            evaluated_item["concept_recommended_weights"][
                                concept_record.concept_id
                            ],
                        )
                        for concept_record in evaluated_item["concept_records"]
                    ],
                }
                for evaluated_item in evaluated_items
                if evaluated_item["should_update_concepts"]
            ]
        )

        repository.replace_exercise_related_exercises_batch(
            [
                {
                    "exercise_id": evaluated_item["exercise"].exercise_id,
                    "related_exercises": [
                        (
                            related_record,
                            evaluated_item["related_exercise_weights"][
                                related_record.exercise_id
                            ],
                        )
                        for related_record in evaluated_item["related_exercise_records"]
                    ],
                }
                for evaluated_item in evaluated_items
                if evaluated_item["should_update_related_exercises"]
            ]
        )

        return KnowledgeGraphExercisesBatchResponse(exercises=response_exercises)
    except HTTPException:
        raise
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
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
    exercise_embedding_service: ExerciseEmbeddingService = Depends(
        get_exercise_embedding_service
    ),
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
):
    try:
        concept_slug_map = repository.get_concepts_by_slugs(request.concept_slugs)
        missing_concept_slugs = [
            concept_slug
            for concept_slug in request.concept_slugs
            if not concept_slug_map.get(concept_slug)
        ]
        if missing_concept_slugs:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Exercise upsert failed: concept slug(s) not found: "
                    + ", ".join(missing_concept_slugs)
                ),
            )
        main_exercise = ExerciseRecord(
            exercise_id=exercise_id,
            slug=request.slug,
            title=request.title,
            description=request.description,
            content=request.content,
            difficulty=request.difficulty,
            concept_slugs=request.concept_slugs,
        )
        main_exercise = exercise_embedding_service.hydrate_exercises([main_exercise])[0]
        exercise = repository.upsert_exercise(main_exercise)
        concept_records = [
            record
            for concept_slug in request.concept_slugs
            for record in concept_slug_map.get(concept_slug, [])
        ]
        concept_weights, recommended_weights = (
            exercise_relation_scoring_service.evaluate_exercise_concepts(
                main_exercise=exercise,
                concepts=concept_records,
            )
        )
        repository.replace_exercise_concepts(
            exercise_id=exercise.exercise_id,
            concepts=[
                (
                    concept_record,
                    concept_weights[concept_record.concept_id],
                    recommended_weights[concept_record.concept_id],
                )
                for concept_record in concept_records
            ],
        )
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
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
):
    try:
        response = await batch_patch_exercise_relations(
            request=BatchPatchExerciseRelationsRequest(
                exercises=[
                    BatchPatchExerciseRelationsItem(
                        exercise_id=exercise_id,
                        concept_slugs=request.concept_slugs,
                        related_exercise_slugs=request.related_exercise_slugs,
                    )
                ]
            ),
            repository=repository,
            exercise_relation_scoring_service=exercise_relation_scoring_service,
        )
        return KnowledgeGraphExerciseResponse(exercise=response.exercises[0])
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
    request: UpsertStudentRequest,
    repository: KnowledgeGraphRepository = Depends(get_knowledge_graph_repository),
):
    try:
        repository.upsert_student(student_id=student_id)
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
