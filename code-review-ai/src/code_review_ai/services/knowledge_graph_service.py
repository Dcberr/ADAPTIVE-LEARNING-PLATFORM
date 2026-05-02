from __future__ import annotations

from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsItem,
    BatchPatchExerciseRelationsRequest,
    BatchSyncExercisesToVectorRequest,
    BatchUpsertExercisesRequest,
    PatchConceptRelationsRequest,
    PatchExerciseRelationsRequest,
    UpsertConceptRequest,
    UpsertExerciseRequest,
    UpsertReviewRequest,
    UpsertSubmissionRequest,
)
from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.services.exercise_embedding_service import ExerciseEmbeddingService
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.services.exercise_vector_service import ExerciseVectorService


class KnowledgeGraphService:
    def __init__(
        self,
        *,
        neo4j_repository: Neo4jRepository,
        exercise_embedding_service: ExerciseEmbeddingService,
        exercise_vector_service: ExerciseVectorService,
        exercise_relation_scoring_service: ExerciseRelationScoringService,
        prerequisite_weight_agent: PrerequisiteWeightAgent,
    ):
        self.neo4j_repository = neo4j_repository
        self.exercise_embedding_service = exercise_embedding_service
        self.exercise_vector_service = exercise_vector_service
        self.exercise_relation_scoring_service = exercise_relation_scoring_service
        self.prerequisite_weight_agent = prerequisite_weight_agent

    def upsert_concept(
        self, concept_slug: str, request: UpsertConceptRequest
    ) -> ConceptRecord:
        main_concept = ConceptRecord(
            concept_id=concept_slug,
            slug=concept_slug,
            name=request.name,
            description=request.description,
            difficulty=request.difficulty,
        )
        return self.neo4j_repository.upsert_concepts([main_concept])[0]

    def patch_concept_relations(
        self, concept_slug: str, request: PatchConceptRelationsRequest
    ) -> ConceptRecord:
        concept_matches = self.neo4j_repository.get_concepts_by_slugs([concept_slug]).get(
            concept_slug, []
        )
        if not concept_matches:
            raise ValueError(f"concept '{concept_slug}' not found")
        concept = concept_matches[0]

        if request.prerequisite_slugs is not None:
            prerequisite_slug_map = self.neo4j_repository.get_concepts_by_slugs(
                request.prerequisite_slugs
            )
            missing_prerequisites = [
                prerequisite_slug
                for prerequisite_slug in request.prerequisite_slugs
                if not prerequisite_slug_map.get(prerequisite_slug)
            ]
            if missing_prerequisites:
                raise ValueError(
                    "prerequisite concept slug(s) not found: "
                    + ", ".join(missing_prerequisites)
                )
            prerequisite_records: list[ConceptRecord] = []
            seen_concept_ids: set[str] = {concept.concept_id}
            for prerequisite_slug in request.prerequisite_slugs:
                for prerequisite in prerequisite_slug_map.get(prerequisite_slug, []):
                    if prerequisite.concept_id in seen_concept_ids:
                        continue
                    prerequisite_records.append(prerequisite)
                    seen_concept_ids.add(prerequisite.concept_id)

            prerequisite_strengths = self.prerequisite_weight_agent.evaluate(
                main_concept=concept,
                prerequisites=prerequisite_records,
            )
            self.neo4j_repository.replace_concept_prerequisites_batch(
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

        return concept

    def batch_upsert_exercises(
        self, request: BatchUpsertExercisesRequest
    ) -> list[ExerciseRecord]:
        concept_slug_map = self.neo4j_repository.get_concepts_by_slugs(
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
            raise ValueError(
                "concept slug(s) not found: " + ", ".join(missing_concept_slugs)
            )

        exercises = self.exercise_embedding_service.hydrate_exercises(
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
        exercises = self.neo4j_repository.upsert_exercises(exercises)
        self.neo4j_repository.replace_exercise_concepts_batch(
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
                        *self.exercise_relation_scoring_service.evaluate_exercise_concepts(
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
        self.exercise_vector_service.upsert_exercises(exercises)
        return exercises

    def sync_exercises_to_vector(
        self, request: BatchSyncExercisesToVectorRequest
    ) -> list[ExerciseRecord]:
        exercise_ids = list(
            dict.fromkeys(
                exercise_id.strip()
                for exercise_id in request.exercise_ids
                if exercise_id.strip()
            )
        )
        if not exercise_ids:
            return []

        exercises_by_id = self.neo4j_repository.get_exercises_by_ids(exercise_ids)
        missing_exercise_ids = [
            exercise_id for exercise_id in exercise_ids if exercise_id not in exercises_by_id
        ]
        if missing_exercise_ids:
            raise ValueError("exercise(s) not found: " + ", ".join(missing_exercise_ids))

        exercises = self.exercise_embedding_service.hydrate_exercises(
            [exercises_by_id[exercise_id] for exercise_id in exercise_ids]
        )
        self.exercise_vector_service.upsert_exercises(exercises)
        return exercises

    def batch_patch_exercise_relations(
        self, request: BatchPatchExerciseRelationsRequest
    ) -> list[ExerciseRecord]:
        exercises_by_id = self.neo4j_repository.get_exercises_by_ids(
            [item.exercise_id for item in request.exercises]
        )
        missing_exercise_ids = [
            item.exercise_id
            for item in request.exercises
            if item.exercise_id not in exercises_by_id
        ]
        if missing_exercise_ids:
            raise ValueError("exercise(s) not found: " + ", ".join(missing_exercise_ids))

        concept_slug_map = self.neo4j_repository.get_concepts_by_slugs(
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
        related_exercises_by_slug = self.neo4j_repository.get_exercises_by_slugs(
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
                    raise ValueError(
                        "concept slug(s) not found: " + ", ".join(missing_concept_slugs)
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

            should_update_related_exercises = item.related_exercise_slugs is not None
            related_exercise_records: list[ExerciseRecord] = []
            if should_update_related_exercises:
                missing_related_exercise_slugs = [
                    related_exercise_slug
                    for related_exercise_slug in (item.related_exercise_slugs or [])
                    if not related_exercises_by_slug.get(related_exercise_slug)
                ]
                if missing_related_exercise_slugs:
                    raise ValueError(
                        "related exercise slug(s) not found: "
                        + ", ".join(missing_related_exercise_slugs)
                    )

                seen_related_ids: set[str] = {item.exercise_id}
                for related_exercise_slug in item.related_exercise_slugs or []:
                    for record in related_exercises_by_slug.get(related_exercise_slug, []):
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
            ) = self.exercise_relation_scoring_service.evaluate(
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

        self.neo4j_repository.upsert_exercises(
            [
                evaluated_item["exercise"]
                for evaluated_item in evaluated_items
                if evaluated_item["should_update_concepts"]
            ]
        )

        self.neo4j_repository.replace_exercise_concepts_batch(
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

        self.neo4j_repository.replace_exercise_related_exercises_batch(
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

        return response_exercises

    def upsert_exercise(
        self, exercise_id: str, request: UpsertExerciseRequest
    ) -> ExerciseRecord:
        exercises = self.batch_upsert_exercises(
            BatchUpsertExercisesRequest(
                exercises=[
                    {
                        "exercise_id": exercise_id,
                        "slug": request.slug,
                        "title": request.title,
                        "description": request.description,
                        "content": request.content,
                        "difficulty": request.difficulty,
                        "concept_slugs": request.concept_slugs,
                    }
                ]
            )
        )
        return exercises[0]

    def sync_exercise_to_vector(self, exercise_id: str) -> ExerciseRecord:
        exercises = self.sync_exercises_to_vector(
            BatchSyncExercisesToVectorRequest(exercise_ids=[exercise_id])
        )
        return exercises[0]

    def patch_exercise_relations(
        self, exercise_id: str, request: PatchExerciseRelationsRequest
    ) -> ExerciseRecord:
        exercises = self.batch_patch_exercise_relations(
            BatchPatchExerciseRelationsRequest(
                exercises=[
                    BatchPatchExerciseRelationsItem(
                        exercise_id=exercise_id,
                        concept_slugs=request.concept_slugs,
                        related_exercise_slugs=request.related_exercise_slugs,
                    )
                ]
            )
        )
        return exercises[0]

    def upsert_student(self, student_id: str) -> str:
        self.neo4j_repository.upsert_student(student_id=student_id)
        return student_id

    def upsert_submission(
        self, submission_id: str, request: UpsertSubmissionRequest
    ) -> SubmissionRecord:
        return self.neo4j_repository.upsert_submission(
            submission_id=submission_id,
            student_id=request.student_id,
            exercise_id=request.exercise_id,
            code=request.code,
            testcase_outputs=[item.model_dump() for item in request.testcase_outputs],
        )

    def upsert_review(
        self, review_id: str, request: UpsertReviewRequest
    ) -> ReviewRecord:
        return self.neo4j_repository.upsert_review(
            review_id=review_id,
            submission_id=request.submission_id,
            summary=request.summary,
            detail=request.detail,
            review_items=[item.model_dump() for item in request.review_items],
            scorecard=request.scorecard.model_dump(),
            current_concept=request.current_concept,
        )
