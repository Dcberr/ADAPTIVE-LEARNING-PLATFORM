from __future__ import annotations

import json
from datetime import datetime, timezone
from neo4j import Driver

from code_review_ai.api.review_code_schema import ReviewItem, ReviewResponse, ScoreCard
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import (
    AssignedPath,
    ConceptRecord,
)
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord


class Neo4jRepository:
    """Neo4j-backed repository for GraphRAG recommendation data."""

    def __init__(self, driver: Driver):
        self.driver = driver

    @staticmethod
    def _did_testcase_pass(testcase_output: dict) -> bool:
        expect = str(testcase_output.get("expect", "")).strip()
        output = str(testcase_output.get("output", "")).strip()
        return expect == output

    def _calculate_attempt_transition_scores(
        self,
        previous_outputs: list[dict],
        current_outputs: list[dict],
    ) -> tuple[float, float]:
        previous_failed = {
            index
            for index, item in enumerate(previous_outputs)
            if not self._did_testcase_pass(item)
        }
        current_failed = {
            index
            for index, item in enumerate(current_outputs)
            if not self._did_testcase_pass(item)
        }

        fixed_count = len(previous_failed - current_failed)
        newly_broken_count = len(current_failed - previous_failed)

        previous_total = max(len(previous_outputs), 1)
        current_total = max(len(current_outputs), 1)
        previous_pass_rate = (previous_total - len(previous_failed)) / previous_total
        current_pass_rate = (current_total - len(current_failed)) / current_total
        score_delta = current_pass_rate - previous_pass_rate

        fixed_ratio = fixed_count / max(len(previous_failed), 1)
        broken_ratio = newly_broken_count / max(len(previous_failed), 1)

        improvement_ratio = max(
            0.0,
            min(1.0, 0.5 * max(score_delta, 0.0) + 0.5 * fixed_ratio),
        )
        regression_ratio = max(
            0.0,
            min(1.0, 0.5 * max(-score_delta, 0.0) + 0.5 * broken_ratio),
        )
        return improvement_ratio, regression_ratio

    def get_concepts_by_ids(self, concept_ids: list[str]) -> dict[str, ConceptRecord]:
        unique_ids = list(dict.fromkeys(concept_ids))
        if not unique_ids:
            return {}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (c:Concept)
                WHERE c.concept_id IN $concept_ids
                RETURN c.concept_id AS concept_id,
                       coalesce(c.slug, c.concept_id) AS slug,
                       coalesce(c.name, c.concept_id) AS name,
                       coalesce(c.description, '') AS description,
                       coalesce(c.difficulty, 1) AS difficulty
                """,
                concept_ids=unique_ids,
            )
            return {
                record["concept_id"]: ConceptRecord(
                    concept_id=record["concept_id"],
                    slug=record["slug"],
                    name=record["name"],
                    description=record["description"],
                    difficulty=record["difficulty"],
                )
                for record in rows
            }

    def get_concepts_by_slugs(
        self, concept_slugs: list[str]
    ) -> dict[str, list[ConceptRecord]]:
        unique_slugs = list(dict.fromkeys(concept_slugs))
        if not unique_slugs:
            return {}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (c:Concept)
                WHERE c.slug IN $concept_slugs
                RETURN c.slug AS slug,
                       c.concept_id AS concept_id,
                       coalesce(c.name, c.concept_id) AS name,
                       coalesce(c.description, '') AS description,
                       coalesce(c.difficulty, 1) AS difficulty
                ORDER BY slug ASC, concept_id ASC
                """,
                concept_slugs=unique_slugs,
            )
            concept_map: dict[str, list[ConceptRecord]] = {
                slug: [] for slug in unique_slugs
            }
            for record in rows:
                slug = record["slug"]
                concept_map.setdefault(slug, []).append(
                    ConceptRecord(
                        concept_id=record["concept_id"],
                        slug=record["slug"],
                        name=record["name"],
                        description=record["description"],
                        difficulty=record["difficulty"],
                    )
                )
            return concept_map

    def get_exercises_by_ids(self, exercise_ids: list[str]) -> dict[str, ExerciseRecord]:
        unique_ids = list(dict.fromkeys(exercise_ids))
        if not unique_ids:
            return {}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (e:Exercise)
                WHERE e.exercise_id IN $exercise_ids
                RETURN e.exercise_id AS exercise_id,
                       coalesce(e.slug, '') AS slug,
                       coalesce(e.title, '') AS title,
                       coalesce(e.description, '') AS description,
                       coalesce(e.content, '') AS content,
                       coalesce(e.difficulty, '') AS difficulty,
                       coalesce(e.concept_slugs, []) AS concept_slugs,
                       coalesce(e.embedding, []) AS embedding,
                       coalesce(e.embedding_model, '') AS embedding_model,
                       coalesce(e.content_hash, '') AS content_hash
                """,
                exercise_ids=unique_ids,
            )
            return {
                record["exercise_id"]: ExerciseRecord(
                    exercise_id=record["exercise_id"],
                    slug=record["slug"],
                    title=record["title"],
                    description=record["description"],
                    content=record["content"],
                    difficulty=record["difficulty"],
                    concept_slugs=record["concept_slugs"] or [],
                    embedding=record["embedding"] or [],
                    embedding_model=record["embedding_model"] or "",
                    content_hash=record["content_hash"] or "",
                )
                for record in rows
            }

    def get_exercises_by_slugs(
        self, exercise_slugs: list[str]
    ) -> dict[str, list[ExerciseRecord]]:
        unique_slugs = list(dict.fromkeys(exercise_slugs))
        if not unique_slugs:
            return {}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (e:Exercise)
                WHERE e.slug IN $exercise_slugs
                RETURN e.slug AS slug,
                       e.exercise_id AS exercise_id,
                       coalesce(e.title, '') AS title,
                       coalesce(e.description, '') AS description,
                       coalesce(e.content, '') AS content,
                       coalesce(e.difficulty, '') AS difficulty,
                       coalesce(e.concept_slugs, []) AS concept_slugs,
                       coalesce(e.embedding, []) AS embedding,
                       coalesce(e.embedding_model, '') AS embedding_model,
                       coalesce(e.content_hash, '') AS content_hash
                ORDER BY slug ASC, exercise_id ASC
                """,
                exercise_slugs=unique_slugs,
            )
            exercise_map: dict[str, list[ExerciseRecord]] = {
                slug: [] for slug in unique_slugs
            }
            for record in rows:
                slug = record["slug"]
                exercise_map.setdefault(slug, []).append(
                    ExerciseRecord(
                        exercise_id=record["exercise_id"],
                        slug=record["slug"],
                        title=record["title"],
                        description=record["description"],
                        content=record["content"],
                        difficulty=record["difficulty"],
                        concept_slugs=record["concept_slugs"] or [],
                        embedding=record["embedding"] or [],
                        embedding_model=record["embedding_model"] or "",
                        content_hash=record["content_hash"] or "",
                    )
                )
            return exercise_map

    def get_concept_ids_for_exercises(self, exercise_ids: list[str]) -> list[str]:
        unique_ids = list(dict.fromkeys(exercise_ids))
        if not unique_ids:
            return []

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (e:Exercise)-[r:TESTS]->(c:Concept)
                WHERE e.exercise_id IN $exercise_ids
                RETURN c.concept_id AS concept_id,
                       max(coalesce(r.weight, 1.0)) AS max_weight
                ORDER BY max_weight DESC, concept_id ASC
                """,
                exercise_ids=unique_ids,
            )
            return [record["concept_id"] for record in rows]

    def get_concept_ids_by_exercise(self, exercise_ids: list[str]) -> dict[str, list[str]]:
        unique_ids = list(dict.fromkeys(exercise_ids))
        if not unique_ids:
            return {}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (e:Exercise)-[r:TESTS]->(c:Concept)
                WHERE e.exercise_id IN $exercise_ids
                RETURN e.exercise_id AS exercise_id,
                       c.concept_id AS concept_id,
                       coalesce(r.weight, 1.0) AS weight
                ORDER BY exercise_id ASC, weight DESC, concept_id ASC
                """,
                exercise_ids=unique_ids,
            )
            concept_map: dict[str, list[str]] = {exercise_id: [] for exercise_id in unique_ids}
            for record in rows:
                concept_map.setdefault(record["exercise_id"], []).append(record["concept_id"])
            return concept_map

    def fetch_recommendation_base_context(
        self,
        *,
        student_id: str,
        exercise_id: str,
    ) -> dict:
        exercise = self.get_exercises_by_ids([exercise_id]).get(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise '{exercise_id}' was not found in Neo4j.")

        with self.driver.session() as session:
            tested_concepts = [
                {
                    "concept_id": record["concept_id"],
                    "weight": float(record["weight"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:TESTS]->(c:Concept)
                    RETURN c.concept_id AS concept_id,
                           coalesce(r.weight, 1.0) AS weight
                    ORDER BY weight DESC, c.concept_id ASC
                    """,
                    exercise_id=exercise_id,
                )
            ]
            recommended_concepts = [
                {
                    "concept_id": record["concept_id"],
                    "weight": float(record["weight"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:RECOMMENDED_FOR]->(c:Concept)
                    RETURN c.concept_id AS concept_id,
                           coalesce(r.weight, 1.0) AS weight
                    ORDER BY weight DESC, c.concept_id ASC
                    """,
                    exercise_id=exercise_id,
                )
            ]
            student_record = session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                OPTIONAL MATCH (s)-[:MASTERED]->(mastered:Concept)
                WITH s, collect(DISTINCT mastered.concept_id) AS mastered_concepts
                OPTIONAL MATCH (s)-[:ATTEMPTED]->(attempted:Exercise)
                RETURN mastered_concepts AS mastered_concepts,
                       collect(DISTINCT attempted.exercise_id) AS attempted_exercise_ids
                LIMIT 1
                """,
                student_id=student_id,
            ).single()
            if student_record is None:
                raise ValueError(f"Student '{student_id}' was not found in Neo4j.")

            latest_review_record = session.run(
                """
                MATCH (:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(r:Review {exercise_id: $exercise_id})
                RETURN r.review_id AS review_id,
                       coalesce(r.summary, '') AS summary,
                       coalesce(r.detail, '') AS detail,
                       coalesce(r.review_items_json, '[]') AS review_items_json,
                       coalesce(r.scorecard_json, '{}') AS scorecard_json,
                       coalesce(r.created_at, '') AS created_at,
                       coalesce(r.current_concept, '') AS current_concept,
                       coalesce(r.submission_id, '') AS submission_id
                ORDER BY r.created_at DESC
                LIMIT 1
                """,
                student_id=student_id,
                exercise_id=exercise_id,
            ).single()
            if latest_review_record is None:
                raise ValueError(
                    f"No stored review found for student '{student_id}' and exercise '{exercise_id}'."
                )

            latest_submission_record = session.run(
                """
                MATCH (:Student {student_id: $student_id})-[:SUBMITTED]->(sub:Submission)-[:FOR_EXERCISE]->(:Exercise {exercise_id: $exercise_id})
                RETURN sub.submission_id AS submission_id,
                       coalesce(sub.code, '') AS code,
                       coalesce(sub.testcase_outputs_json, '[]') AS testcase_outputs_json,
                       coalesce(sub.created_at, '') AS created_at
                ORDER BY sub.created_at DESC
                LIMIT 1
                """,
                student_id=student_id,
                exercise_id=exercise_id,
            ).single()

        review = ReviewResponse(
            review_id=latest_review_record["review_id"],
            summary=latest_review_record["summary"],
            detail=latest_review_record["detail"],
            review_items=[
                ReviewItem.model_validate(item)
                for item in json.loads(latest_review_record["review_items_json"])
            ],
            scorecard=ScoreCard.model_validate(
                json.loads(latest_review_record["scorecard_json"])
            ),
        )
        review_record = ReviewRecord(
            review_id=latest_review_record["review_id"],
            student_id=student_id,
            exercise_id=exercise_id,
            submission_id=latest_review_record["submission_id"],
            current_concept=latest_review_record["current_concept"],
            created_at=latest_review_record["created_at"],
            summary=latest_review_record["summary"],
            detail=latest_review_record["detail"],
        )
        latest_submission = None
        if latest_submission_record is not None:
            latest_submission = SubmissionRecord.model_validate(
                {
                    "submission_id": latest_submission_record["submission_id"],
                    "student_id": student_id,
                    "exercise_id": exercise_id,
                    "code": latest_submission_record["code"],
                    "testcase_outputs": json.loads(
                        latest_submission_record["testcase_outputs_json"] or "[]"
                    ),
                    "created_at": latest_submission_record["created_at"],
                }
            )

        current_concept = latest_review_record["current_concept"] or (
            tested_concepts[0]["concept_id"] if tested_concepts else ""
        )
        current_concept_weight = 1.0
        for concept in tested_concepts:
            if concept["concept_id"] == current_concept:
                current_concept_weight = float(concept["weight"] or 1.0)
                break

        return {
            "exercise": exercise,
            "tested_concepts": tested_concepts,
                "recommended_concepts": recommended_concepts,
            "review": review,
            "review_record": review_record,
            "latest_submission": latest_submission,
            "current_concept": current_concept,
            "current_concept_weight": current_concept_weight,
            "mastered_concepts": student_record["mastered_concepts"] or [],
            "attempted_exercise_ids": student_record["attempted_exercise_ids"] or [],
            "critical_errors": sum(1 for item in review.review_items if item.type == "Error"),
        }

    def fetch_review_trend_context(
        self,
        *,
        review_id: str,
        student_id: str,
        history_limit: int = 3,
    ) -> dict:
        with self.driver.session() as session:
            review_history = [
                ReviewRecord(
                    review_id=record["review_id"],
                    student_id=record["student_id"],
                    exercise_id=record["exercise_id"],
                    submission_id=record["submission_id"],
                    current_concept=record["current_concept"],
                    created_at=record["created_at"],
                    summary=record["summary"],
                    detail=record["detail"],
                )
                for record in session.run(
                    """
                    MATCH path = (prev:Review)-[:NEXT_REVIEW_OF*1..5]->(current:Review {review_id: $review_id})
                    RETURN prev.review_id AS review_id,
                           coalesce(prev.student_id, $student_id) AS student_id,
                           coalesce(prev.exercise_id, '') AS exercise_id,
                           coalesce(prev.submission_id, '') AS submission_id,
                           coalesce(prev.current_concept, '') AS current_concept,
                           coalesce(prev.created_at, '') AS created_at,
                           coalesce(prev.summary, '') AS summary,
                           coalesce(prev.detail, '') AS detail,
                           length(path) AS depth
                    ORDER BY depth ASC, prev.created_at DESC
                    LIMIT $history_limit
                    """,
                    review_id=review_id,
                    student_id=student_id,
                    history_limit=history_limit,
                )
            ]

        return {
            "review_history": review_history,
            "previous_review_id": review_history[0].review_id if review_history else "",
        }

    def fetch_submission_trend_context(self, *, submission_id: str) -> dict:
        with self.driver.session() as session:
            latest_transition = session.run(
                """
                MATCH (prev:Submission)-[rel:NEXT_ATTEMPT]->(curr:Submission {submission_id: $submission_id})
                RETURN prev.submission_id AS previous_submission_id,
                       coalesce(prev.testcase_outputs_json, '[]') AS previous_testcase_outputs_json,
                       coalesce(curr.testcase_outputs_json, '[]') AS current_testcase_outputs_json
                ORDER BY coalesce(rel.linked_at, '') DESC
                LIMIT 1
                """,
                submission_id=submission_id,
            ).single()

        improvement_ratio = 0.0
        regression_ratio = 0.0
        previous_submission_id = ""
        if latest_transition is not None:
            previous_submission_id = str(latest_transition["previous_submission_id"] or "")
            previous_outputs = json.loads(
                latest_transition["previous_testcase_outputs_json"] or "[]"
            )
            current_outputs = json.loads(
                latest_transition["current_testcase_outputs_json"] or "[]"
            )
            improvement_ratio, regression_ratio = self._calculate_attempt_transition_scores(
                previous_outputs=previous_outputs,
                current_outputs=current_outputs,
            )
        return {
            "latest_submission_improvement_ratio": float(improvement_ratio),
            "latest_submission_regression_ratio": float(regression_ratio),
            "previous_submission_id": previous_submission_id,
        }

    def fetch_submission_history_context(
        self,
        *,
        submission_id: str,
        history_limit: int = 3,
    ) -> dict:
        with self.driver.session() as session:
            submission_history = [
                SubmissionRecord.model_validate(
                    {
                        "submission_id": record["submission_id"],
                        "student_id": record["student_id"],
                        "exercise_id": record["exercise_id"],
                        "code": record["code"],
                        "testcase_outputs": json.loads(
                            record["testcase_outputs_json"] or "[]"
                        ),
                        "created_at": record["created_at"],
                    }
                )
                for record in session.run(
                    """
                    MATCH path = (prev:Submission)-[:NEXT_ATTEMPT*1..5]->(current:Submission {submission_id: $submission_id})
                    RETURN prev.submission_id AS submission_id,
                           coalesce(prev.student_id, '') AS student_id,
                           coalesce(prev.exercise_id, '') AS exercise_id,
                           coalesce(prev.code, '') AS code,
                           coalesce(prev.testcase_outputs_json, '[]') AS testcase_outputs_json,
                           coalesce(prev.created_at, '') AS created_at,
                           length(path) AS depth
                    ORDER BY depth ASC, prev.created_at DESC
                    LIMIT $history_limit
                    """,
                    submission_id=submission_id,
                    history_limit=history_limit,
                )
            ]
        return {"submission_history": submission_history}

    def fetch_exercise_graph_context(
        self,
        *,
        exercise_id: str,
        focus_concept_id: str = "",
        limit: int = 6,
    ) -> dict:
        with self.driver.session() as session:
            related_exercises = [
                {
                    "exercise_id": record["exercise_id"],
                    "title": record["title"],
                    "weight": float(record["weight"] or 0.0),
                    "relation_type": record["relation_type"] or "",
                    "difficulty_gap": float(record["difficulty_gap"] or 0.0),
                    "progression_score": float(record["progression_score"] or 0.0),
                    "similarity_score": float(record["similarity_score"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:RELATED_TO]->(e:Exercise)
                    RETURN e.exercise_id AS exercise_id,
                           coalesce(e.title, '') AS title,
                           coalesce(r.weight, 1.0) AS weight,
                           coalesce(r.relation_type, '') AS relation_type,
                           coalesce(r.difficulty_gap, 0.0) AS difficulty_gap,
                           coalesce(r.progression_score, 0.0) AS progression_score,
                           coalesce(r.similarity_score, 0.0) AS similarity_score
                    ORDER BY weight DESC, progression_score DESC, similarity_score DESC
                    LIMIT $limit
                    """,
                    exercise_id=exercise_id,
                    limit=limit,
                )
            ]
            recommended_links = [
                {
                    "concept_id": record["concept_id"],
                    "weight": float(record["weight"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:RECOMMENDED_FOR]->(c:Concept)
                    WHERE $focus_concept_id = '' OR c.concept_id = $focus_concept_id
                    RETURN c.concept_id AS concept_id,
                           coalesce(r.weight, 1.0) AS weight
                    ORDER BY weight DESC, c.concept_id ASC
                    """,
                    exercise_id=exercise_id,
                    focus_concept_id=focus_concept_id,
                )
            ]
        return {
            "related_exercises": related_exercises,
            "recommended_links": recommended_links,
            "best_related_exercise_weight": max(
                (exercise["weight"] for exercise in related_exercises),
                default=0.0,
            ),
            "best_recommended_weight": max(
                (link["weight"] for link in recommended_links),
                default=0.0,
            ),
        }

    def fetch_student_history_context(self, *, student_id: str) -> dict:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                OPTIONAL MATCH (s)-[:ATTEMPTED]->(attempted:Exercise)
                WITH s, collect(DISTINCT attempted.exercise_id) AS attempted_exercise_ids
                OPTIONAL MATCH (s)-[:ASSIGNED]->(assigned:Exercise)
                RETURN attempted_exercise_ids AS attempted_exercise_ids,
                       collect(DISTINCT assigned.exercise_id) AS assigned_exercise_ids
                LIMIT 1
                """,
                student_id=student_id,
            ).single()
        return {
            "attempted_exercise_ids": record["attempted_exercise_ids"] if record else [],
            "assigned_exercise_ids": record["assigned_exercise_ids"] if record else [],
        }

    def get_review_payload(self, review_id: str) -> dict | None:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (review:Review {review_id: $review_id})
                RETURN review.review_id AS review_id,
                       coalesce(review.student_id, '') AS student_id,
                       coalesce(review.exercise_id, '') AS exercise_id,
                       coalesce(review.submission_id, '') AS submission_id,
                       coalesce(review.current_concept, '') AS current_concept,
                       coalesce(review.created_at, '') AS created_at,
                       coalesce(review.summary, '') AS summary,
                       coalesce(review.detail, '') AS detail,
                       coalesce(review.review_items_json, '[]') AS review_items_json,
                       coalesce(review.scorecard_json, '{}') AS scorecard_json
                LIMIT 1
                """,
                review_id=review_id,
            ).single()
        if record is None:
            return None

        return {
            "review": ReviewRecord(
                review_id=record["review_id"],
                student_id=record["student_id"],
                exercise_id=record["exercise_id"],
                submission_id=record["submission_id"],
                current_concept=record["current_concept"],
                created_at=record["created_at"],
                summary=record["summary"],
                detail=record["detail"],
            ),
            "review_items": json.loads(record["review_items_json"] or "[]"),
            "scorecard": json.loads(record["scorecard_json"] or "{}"),
        }

    def get_submission_payload(self, submission_id: str) -> dict | None:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (sub:Submission {submission_id: $submission_id})
                RETURN sub.submission_id AS submission_id,
                       coalesce(sub.student_id, '') AS student_id,
                       coalesce(sub.exercise_id, '') AS exercise_id,
                       coalesce(sub.code, '') AS code,
                       coalesce(sub.testcase_outputs_json, '[]') AS testcase_outputs_json,
                       coalesce(sub.created_at, '') AS created_at
                LIMIT 1
                """,
                submission_id=submission_id,
            ).single()
        if record is None:
            return None

        return {
            "submission": SubmissionRecord.model_validate(
                {
                    "submission_id": record["submission_id"],
                    "student_id": record["student_id"],
                    "exercise_id": record["exercise_id"],
                    "code": record["code"],
                    "testcase_outputs": json.loads(record["testcase_outputs_json"] or "[]"),
                    "created_at": record["created_at"],
                }
            )
        }

    def upsert_concept(
        self,
        concept: ConceptRecord,
    ) -> ConceptRecord:
        self.upsert_concepts([concept])
        return concept

    def upsert_concepts(
        self,
        concepts: list[ConceptRecord],
    ) -> list[ConceptRecord]:
        if not concepts:
            return []

        with self.driver.session() as session:
            session.run(
                """
                UNWIND $rows AS row
                MERGE (c:Concept {slug: row.slug})
                SET c.concept_id = row.concept_id,
                    c.slug = row.slug,
                    c.name = row.name,
                    c.description = row.description,
                    c.difficulty = row.difficulty
                """,
                rows=[
                    {
                        "concept_id": concept.concept_id,
                        "slug": concept.slug,
                        "name": concept.name,
                        "description": concept.description,
                        "difficulty": concept.difficulty,
                    }
                    for concept in concepts
                ],
            )
        return concepts

    def replace_concept_prerequisites(
        self,
        *,
        concept_slug: str,
        prerequisites: list[tuple[ConceptRecord, float]],
    ) -> None:
        self.replace_concept_prerequisites_batch(
            [
                {
                    "concept_slug": concept_slug,
                    "prerequisites": prerequisites,
                }
            ]
        )

    def replace_concept_prerequisites_batch(
        self,
        items: list[dict],
    ) -> None:
        if not items:
            return

        concept_slugs = list(
            dict.fromkeys(str(item["concept_slug"]) for item in items if item.get("concept_slug"))
        )
        rows: list[dict] = []
        for item in items:
            concept_slug = str(item["concept_slug"])
            for prerequisite, strength in item.get("prerequisites", []):
                rows.append(
                    {
                        "concept_slug": concept_slug,
                        "prerequisite_slug": prerequisite.slug,
                        "strength": strength,
                    }
                )

        with self.driver.session() as session:
            session.run(
                """
                MATCH (:Concept)-[r:PREREQUISITE_OF]->(c:Concept)
                WHERE c.slug IN $concept_slugs
                DELETE r
                """,
                concept_slugs=concept_slugs,
            )
            if rows:
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (p:Concept {slug: row.prerequisite_slug})
                    MATCH (c:Concept {slug: row.concept_slug})
                    MERGE (p)-[r:PREREQUISITE_OF]->(c)
                    SET r.strength = row.strength
                    """,
                    rows=rows,
                )

    def upsert_exercise(
        self,
        exercise: ExerciseRecord,
    ) -> ExerciseRecord:
        self.upsert_exercises([exercise])
        return exercise

    def upsert_exercises(
        self,
        exercises: list[ExerciseRecord],
    ) -> list[ExerciseRecord]:
        if not exercises:
            return []

        with self.driver.session() as session:
            session.run(
                """
                UNWIND $rows AS row
                MERGE (e:Exercise {exercise_id: row.exercise_id})
                SET e.slug = row.slug,
                    e.title = row.title,
                    e.description = row.description,
                    e.content = row.content,
                    e.difficulty = row.difficulty,
                    e.concept_slugs = row.concept_slugs,
                    e.embedding = row.embedding,
                    e.embedding_model = row.embedding_model,
                    e.content_hash = row.content_hash
                """,
                rows=[
                    {
                        "exercise_id": exercise.exercise_id,
                        "slug": exercise.slug,
                        "title": exercise.title,
                        "description": exercise.description,
                        "content": exercise.content,
                        "difficulty": exercise.difficulty,
                        "concept_slugs": list(
                            dict.fromkeys(
                                [
                                    item.strip()
                                    for item in exercise.concept_slugs
                                    if item.strip()
                                ]
                            )
                        ),
                        "embedding": exercise.embedding,
                        "embedding_model": exercise.embedding_model,
                        "content_hash": exercise.content_hash,
                    }
                    for exercise in exercises
                ],
            )
        return exercises

    def replace_exercise_concepts(
        self,
        *,
        exercise_id: str,
        concepts: list[tuple[ConceptRecord, float, float]],
    ) -> None:
        self.replace_exercise_concepts_batch(
            [
                {
                    "exercise_id": exercise_id,
                    "concepts": concepts,
                }
            ]
        )

    def replace_exercise_concepts_batch(
        self,
        items: list[dict],
    ) -> None:
        if not items:
            return

        exercise_ids = list(
            dict.fromkeys(str(item["exercise_id"]) for item in items if item.get("exercise_id"))
        )
        tests_rows: list[dict] = []
        recommended_rows: list[dict] = []
        for item in items:
            exercise_id = str(item["exercise_id"])
            for concept, weight, recommended_weight in item.get("concepts", []):
                tests_rows.append(
                    {
                        "exercise_id": exercise_id,
                        "concept_id": concept.concept_id,
                        "weight": weight,
                    }
                )
                recommended_rows.append(
                    {
                        "exercise_id": exercise_id,
                        "concept_id": concept.concept_id,
                        "weight": recommended_weight,
                    }
                )

        with self.driver.session() as session:
            session.run(
                """
                MATCH (e:Exercise)-[r:TESTS]->(:Concept)
                WHERE e.exercise_id IN $exercise_ids
                DELETE r
                """,
                exercise_ids=exercise_ids,
            )
            session.run(
                """
                MATCH (e:Exercise)-[r:RECOMMENDED_FOR]->(:Concept)
                WHERE e.exercise_id IN $exercise_ids
                DELETE r
                """,
                exercise_ids=exercise_ids,
            )
            if tests_rows:
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (c:Concept {concept_id: row.concept_id})
                    MATCH (e:Exercise {exercise_id: row.exercise_id})
                    MERGE (e)-[r:TESTS]->(c)
                    SET r.weight = row.weight
                    """,
                    rows=tests_rows,
                )
            if recommended_rows:
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (e:Exercise {exercise_id: row.exercise_id})
                    MATCH (c:Concept {concept_id: row.concept_id})
                    MERGE (e)-[r:RECOMMENDED_FOR]->(c)
                    SET r.weight = row.weight
                    """,
                    rows=recommended_rows,
                )

    def replace_exercise_related_exercises(
        self,
        *,
        exercise_id: str,
        related_exercises: list[tuple[ExerciseRecord, dict]],
    ) -> None:
        self.replace_exercise_related_exercises_batch(
            [
                {
                    "exercise_id": exercise_id,
                    "related_exercises": related_exercises,
                }
            ]
        )

    def replace_exercise_related_exercises_batch(
        self,
        items: list[dict],
    ) -> None:
        if not items:
            return

        exercise_ids = list(
            dict.fromkeys(str(item["exercise_id"]) for item in items if item.get("exercise_id"))
        )
        rows: list[dict] = []
        for item in items:
            exercise_id = str(item["exercise_id"])
            for related_exercise, relation_config in item.get("related_exercises", []):
                rows.append(
                    {
                        "exercise_id": exercise_id,
                        "related_exercise_id": related_exercise.exercise_id,
                        "weight": relation_config.get("weight", 1.0),
                        "relation_type": relation_config.get("relation_type", ""),
                        "difficulty_gap": relation_config.get("difficulty_gap", 0.0),
                        "progression_score": relation_config.get("progression_score", 0.0),
                        "similarity_score": relation_config.get("similarity_score", 0.0),
                    }
                )

        with self.driver.session() as session:
            session.run(
                """
                MATCH (e:Exercise)-[r:RELATED_TO]->(:Exercise)
                WHERE e.exercise_id IN $exercise_ids
                DELETE r
                """,
                exercise_ids=exercise_ids,
            )
            if rows:
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (related:Exercise {exercise_id: row.related_exercise_id})
                    MATCH (main:Exercise {exercise_id: row.exercise_id})
                    MERGE (main)-[r:RELATED_TO]->(related)
                    SET r.weight = row.weight,
                        r.relation_type = row.relation_type,
                        r.difficulty_gap = row.difficulty_gap,
                        r.progression_score = row.progression_score,
                        r.similarity_score = row.similarity_score
                    """,
                    rows=rows,
                )

    def upsert_student(
        self,
        *,
        student_id: str,
    ) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                SET s.current_concept = coalesce(s.current_concept, ''),
                    s.notes = coalesce(s.notes, '')
                """,
                student_id=student_id,
            )

    def upsert_submission(
        self,
        *,
        submission_id: str,
        student_id: str,
        exercise_id: str,
        code: str,
        testcase_outputs: list[dict],
    ) -> SubmissionRecord:
        created_at = datetime.now(timezone.utc).isoformat()
        with self.driver.session() as session:
            student_exists = session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                RETURN s.student_id AS student_id
                LIMIT 1
                """,
                student_id=student_id,
            ).single()
            if student_exists is None:
                raise ValueError(f"Student '{student_id}' does not exist in the graph.")

            exercise_exists = session.run(
                """
                MATCH (e:Exercise {exercise_id: $exercise_id})
                RETURN e.exercise_id AS exercise_id
                LIMIT 1
                """,
                exercise_id=exercise_id,
            ).single()
            if exercise_exists is None:
                raise ValueError(f"Exercise '{exercise_id}' does not exist in the graph.")

            session.run(
                """
                MERGE (sub:Submission {submission_id: $submission_id})
                ON CREATE SET sub.created_at = $created_at
                SET sub.student_id = $student_id,
                    sub.exercise_id = $exercise_id,
                    sub.code = $code,
                    sub.testcase_outputs_json = $testcase_outputs_json
                """,
                submission_id=submission_id,
                student_id=student_id,
                exercise_id=exercise_id,
                code=code,
                testcase_outputs_json=json.dumps(testcase_outputs),
                created_at=created_at,
            )
            session.run(
                """
                MATCH (:Student)-[r:SUBMITTED]->(sub:Submission {submission_id: $submission_id})
                DELETE r
                """,
                submission_id=submission_id,
            )
            session.run(
                """
                MATCH (sub:Submission {submission_id: $submission_id})-[r:FOR_EXERCISE]->(:Exercise)
                DELETE r
                """,
                submission_id=submission_id,
            )
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (sub:Submission {submission_id: $submission_id})
                MERGE (s)-[:SUBMITTED]->(sub)
                WITH sub
                MATCH (e:Exercise {exercise_id: $exercise_id})
                MERGE (sub)-[:FOR_EXERCISE]->(e)
                """,
                student_id=student_id,
                submission_id=submission_id,
                exercise_id=exercise_id,
            )

            current_submission = session.run(
                """
                MATCH (sub:Submission {submission_id: $submission_id})
                RETURN coalesce(sub.created_at, '') AS created_at
                LIMIT 1
                """,
                submission_id=submission_id,
            ).single()
            current_created_at = current_submission["created_at"] or created_at

            session.run(
                """
                MATCH (:Submission)-[r:NEXT_ATTEMPT]->(sub:Submission {submission_id: $submission_id})
                DELETE r
                """,
                submission_id=submission_id,
            )
            session.run(
                """
                MATCH (sub:Submission {submission_id: $submission_id})-[r:NEXT_ATTEMPT]->(:Submission)
                DELETE r
                """,
                submission_id=submission_id,
            )

            previous_submission = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:SUBMITTED]->(prev:Submission)
                WHERE prev.submission_id <> $submission_id
                  AND coalesce(prev.exercise_id, '') = $exercise_id
                  AND coalesce(prev.created_at, '') < $current_created_at
                RETURN prev.submission_id AS submission_id,
                       coalesce(prev.created_at, '') AS created_at
                ORDER BY prev.created_at DESC, prev.submission_id DESC
                LIMIT 1
                """,
                student_id=student_id,
                submission_id=submission_id,
                exercise_id=exercise_id,
                current_created_at=current_created_at,
            ).single()

            next_submission = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:SUBMITTED]->(next:Submission)
                WHERE next.submission_id <> $submission_id
                  AND coalesce(next.exercise_id, '') = $exercise_id
                  AND coalesce(next.created_at, '') > $current_created_at
                RETURN next.submission_id AS submission_id,
                       coalesce(next.created_at, '') AS created_at
                ORDER BY next.created_at ASC, next.submission_id ASC
                LIMIT 1
                """,
                student_id=student_id,
                submission_id=submission_id,
                exercise_id=exercise_id,
                current_created_at=current_created_at,
            ).single()

            if previous_submission is not None:
                session.run(
                    """
                    MATCH (prev:Submission {submission_id: $previous_submission_id})
                    MATCH (curr:Submission {submission_id: $submission_id})
                    MERGE (prev)-[r:NEXT_ATTEMPT]->(curr)
                    SET r.student_id = $student_id,
                        r.linked_at = $linked_at,
                        r.same_exercise = true
                    """,
                    previous_submission_id=previous_submission["submission_id"],
                    submission_id=submission_id,
                    student_id=student_id,
                    linked_at=created_at,
                )

            if next_submission is not None:
                session.run(
                    """
                    MATCH (curr:Submission {submission_id: $submission_id})
                    MATCH (next:Submission {submission_id: $next_submission_id})
                    MERGE (curr)-[r:NEXT_ATTEMPT]->(next)
                    SET r.student_id = $student_id,
                        r.linked_at = $linked_at,
                        r.same_exercise = true
                    """,
                    submission_id=submission_id,
                    next_submission_id=next_submission["submission_id"],
                    student_id=student_id,
                    linked_at=created_at,
                )

            stored = session.run(
                """
                MATCH (sub:Submission {submission_id: $submission_id})
                RETURN sub.submission_id AS submission_id,
                       coalesce(sub.student_id, '') AS student_id,
                       coalesce(sub.exercise_id, '') AS exercise_id,
                       coalesce(sub.code, '') AS code,
                       coalesce(sub.testcase_outputs_json, '[]') AS testcase_outputs_json,
                       coalesce(sub.created_at, '') AS created_at
                """,
                submission_id=submission_id,
            ).single()

        return SubmissionRecord(
            submission_id=stored["submission_id"],
            student_id=stored["student_id"],
            exercise_id=stored["exercise_id"],
            code=stored["code"],
            testcase_outputs=json.loads(stored["testcase_outputs_json"] or "[]"),
            created_at=stored["created_at"],
        )

    def upsert_review(
        self,
        *,
        review_id: str,
        submission_id: str,
        summary: str,
        detail: str,
        review_items: list[dict],
        scorecard: dict,
        current_concept: str = "",
    ) -> ReviewRecord:
        created_at = datetime.now(timezone.utc).isoformat()
        with self.driver.session() as session:
            submission_record = session.run(
                """
                MATCH (s:Student)-[:SUBMITTED]->(sub:Submission {submission_id: $submission_id})
                OPTIONAL MATCH (sub)-[:FOR_EXERCISE]->(e:Exercise)
                RETURN s.student_id AS student_id,
                       coalesce(e.exercise_id, coalesce(sub.exercise_id, '')) AS exercise_id
                LIMIT 1
                """,
                submission_id=submission_id,
            ).single()
            if submission_record is None:
                raise ValueError(
                    f"Submission '{submission_id}' does not exist in the graph."
                )

            student_id = submission_record["student_id"]
            exercise_id = submission_record["exercise_id"]

            session.run(
                """
                MERGE (r:Review {review_id: $review_id})
                ON CREATE SET r.created_at = $created_at
                SET r.summary = $summary,
                    r.detail = $detail,
                    r.student_id = $student_id,
                    r.exercise_id = $exercise_id,
                    r.submission_id = $submission_id,
                    r.current_concept = $current_concept,
                    r.review_items_json = $review_items_json,
                    r.scorecard_json = $scorecard_json
                """,
                review_id=review_id,
                created_at=created_at,
                summary=summary,
                detail=detail,
                student_id=student_id,
                exercise_id=exercise_id,
                submission_id=submission_id,
                current_concept=current_concept,
                review_items_json=json.dumps(review_items),
                scorecard_json=json.dumps(scorecard),
            )
            session.run(
                """
                MATCH (:Student)-[r:RECEIVED_REVIEW]->(review:Review {review_id: $review_id})
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (:Submission)-[r:RECEIVED_REVIEW]->(review:Review {review_id: $review_id})
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (review:Review {review_id: $review_id})-[r:REVIEWS_SUBMISSION]->(:Submission)
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (review:Review {review_id: $review_id})-[r:REVIEWS_EXERCISE]->(:Exercise)
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (:Review)-[r:NEXT_REVIEW_OF]->(review:Review {review_id: $review_id})
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (review:Review {review_id: $review_id})-[r:NEXT_REVIEW_OF]->(:Review)
                DELETE r
                """,
                review_id=review_id,
            )
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (sub:Submission {submission_id: $submission_id})
                MATCH (review:Review {review_id: $review_id})
                MERGE (s)-[:RECEIVED_REVIEW]->(review)
                MERGE (sub)-[:RECEIVED_REVIEW]->(review)
                MERGE (review)-[:REVIEWS_SUBMISSION]->(sub)
                """,
                student_id=student_id,
                submission_id=submission_id,
                review_id=review_id,
            )
            if exercise_id:
                session.run(
                    """
                    MATCH (review:Review {review_id: $review_id})
                    MATCH (e:Exercise {exercise_id: $exercise_id})
                    MERGE (review)-[:REVIEWS_EXERCISE]->(e)
                    """,
                    review_id=review_id,
                    exercise_id=exercise_id,
                )
            current_review = session.run(
                """
                MATCH (review:Review {review_id: $review_id})
                RETURN coalesce(review.created_at, '') AS created_at,
                       coalesce(review.current_concept, '') AS current_concept
                LIMIT 1
                """,
                review_id=review_id,
            ).single()
            current_created_at = (current_review["created_at"] or created_at) if current_review else created_at

            previous_review = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(prev:Review)
                WHERE prev.review_id <> $review_id
                  AND coalesce(prev.created_at, '') < $current_created_at
                RETURN prev.review_id AS review_id,
                       coalesce(prev.current_concept, '') AS current_concept
                ORDER BY prev.created_at DESC, prev.review_id DESC
                LIMIT 1
                """,
                student_id=student_id,
                review_id=review_id,
                current_created_at=current_created_at,
            ).single()

            next_review = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(next:Review)
                WHERE next.review_id <> $review_id
                  AND coalesce(next.created_at, '') > $current_created_at
                RETURN next.review_id AS review_id,
                       coalesce(next.current_concept, '') AS current_concept
                ORDER BY next.created_at ASC, next.review_id ASC
                LIMIT 1
                """,
                student_id=student_id,
                review_id=review_id,
                current_created_at=current_created_at,
            ).single()

            current_concept_value = (
                current_review["current_concept"] if current_review else current_concept
            ) or ""

            if previous_review is not None:
                session.run(
                    """
                    MATCH (prev:Review {review_id: $previous_review_id})
                    MATCH (curr:Review {review_id: $review_id})
                    MERGE (prev)-[rel:NEXT_REVIEW_OF]->(curr)
                    SET rel.student_id = $student_id,
                        rel.linked_at = $linked_at,
                        rel.same_concept = $same_concept
                    """,
                    previous_review_id=previous_review["review_id"],
                    review_id=review_id,
                    student_id=student_id,
                    linked_at=created_at,
                    same_concept=(previous_review["current_concept"] or "")
                    == current_concept_value,
                )

            if next_review is not None:
                session.run(
                    """
                    MATCH (curr:Review {review_id: $review_id})
                    MATCH (next:Review {review_id: $next_review_id})
                    MERGE (curr)-[rel:NEXT_REVIEW_OF]->(next)
                    SET rel.student_id = $student_id,
                        rel.linked_at = $linked_at,
                        rel.same_concept = $same_concept
                    """,
                    review_id=review_id,
                    next_review_id=next_review["review_id"],
                    student_id=student_id,
                    linked_at=created_at,
                    same_concept=current_concept_value == (next_review["current_concept"] or ""),
                )

            stored = session.run(
                """
                MATCH (review:Review {review_id: $review_id})
                RETURN review.review_id AS review_id,
                       coalesce(review.student_id, '') AS student_id,
                       coalesce(review.exercise_id, '') AS exercise_id,
                       coalesce(review.submission_id, '') AS submission_id,
                       coalesce(review.current_concept, '') AS current_concept,
                       coalesce(review.created_at, '') AS created_at,
                       coalesce(review.summary, '') AS summary,
                       coalesce(review.detail, '') AS detail
                """,
                review_id=review_id,
            ).single()

        return ReviewRecord(
            review_id=stored["review_id"],
            student_id=stored["student_id"],
            exercise_id=stored["exercise_id"],
            submission_id=stored["submission_id"],
            current_concept=stored["current_concept"],
            created_at=stored["created_at"],
            summary=stored["summary"],
            detail=stored["detail"],
        )

    def get_recommendation_context(
        self,
        *,
        student_id: str,
        exercise_id: str,
        history_limit: int = 3,
    ) -> dict:
        with self.driver.session() as session:
            latest_record = session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                OPTIONAL MATCH (s)-[:MASTERED]->(mastered:Concept)
                WITH s, collect(DISTINCT mastered.concept_id) AS mastered_concepts
                OPTIONAL MATCH (s)-[:ATTEMPTED]->(attempted:Exercise)
                WITH s, mastered_concepts, collect(DISTINCT attempted.exercise_id) AS attempted_exercise_ids
                MATCH (s)-[:RECEIVED_REVIEW]->(r:Review {exercise_id: $exercise_id})
                OPTIONAL MATCH (r)-[:REVIEWS_EXERCISE]->(e:Exercise {exercise_id: $exercise_id})
                OPTIONAL MATCH (e)-[tests:TESTS]->(c:Concept)
                WITH s, r, mastered_concepts, attempted_exercise_ids, c, tests
                ORDER BY coalesce(tests.weight, 1.0) DESC, coalesce(c.difficulty, 1) ASC, c.name ASC
                RETURN r.review_id AS review_id,
                       coalesce(r.summary, '') AS summary,
                       coalesce(r.detail, '') AS detail,
                       coalesce(r.review_items_json, '[]') AS review_items_json,
                       coalesce(r.scorecard_json, '{}') AS scorecard_json,
                       coalesce(r.created_at, '') AS created_at,
                       coalesce(r.current_concept, head(collect(c.concept_id)), '') AS current_concept,
                       coalesce(
                           max(
                               CASE
                                   WHEN coalesce(r.current_concept, '') <> ''
                                        AND c.concept_id = r.current_concept
                                   THEN coalesce(tests.weight, 1.0)
                                   WHEN coalesce(r.current_concept, '') = ''
                                   THEN coalesce(tests.weight, 1.0)
                                   ELSE 0.0
                               END
                           ),
                           1.0
                       ) AS current_concept_weight,
                       coalesce(r.submission_id, '') AS submission_id,
                       mastered_concepts AS mastered_concepts,
                       attempted_exercise_ids AS attempted_exercise_ids
                ORDER BY r.created_at DESC
                LIMIT 1
                """,
                student_id=student_id,
                exercise_id=exercise_id,
            ).single()
            if latest_record is None:
                raise ValueError(
                    f"No stored review found for student '{student_id}' and exercise '{exercise_id}'."
                )

            current_concept = latest_record["current_concept"]
            if not current_concept:
                raise ValueError(
                    f"Exercise '{exercise_id}' is not linked to a concept in Neo4j."
                )

            review = ReviewResponse(
                review_id=latest_record["review_id"],
                summary=latest_record["summary"],
                detail=latest_record["detail"],
                review_items=[
                    ReviewItem.model_validate(item)
                    for item in json.loads(latest_record["review_items_json"])
                ],
                scorecard=ScoreCard.model_validate(
                    json.loads(latest_record["scorecard_json"])
                ),
            )
            review_history = [
                ReviewRecord(
                    review_id=record["review_id"],
                    student_id=record["student_id"],
                    exercise_id=record["exercise_id"],
                    submission_id=record["submission_id"],
                    current_concept=record["current_concept"],
                    created_at=record["created_at"],
                    summary=record["summary"],
                    detail=record["detail"],
                )
                for record in session.run(
                    """
                    MATCH path = (prev:Review)-[:NEXT_REVIEW_OF*1..5]->(current:Review {review_id: $review_id})
                    RETURN prev.review_id AS review_id,
                           coalesce(prev.student_id, $student_id) AS student_id,
                           coalesce(prev.exercise_id, '') AS exercise_id,
                           coalesce(prev.submission_id, '') AS submission_id,
                           coalesce(prev.current_concept, '') AS current_concept,
                           coalesce(prev.created_at, '') AS created_at,
                           coalesce(prev.summary, '') AS summary,
                           coalesce(prev.detail, '') AS detail,
                           length(path) AS depth
                    ORDER BY depth ASC, prev.created_at DESC
                    LIMIT $history_limit
                    """,
                    review_id=review.review_id,
                    student_id=student_id,
                    history_limit=history_limit,
                )
            ]

            latest_submission_transition = None
            if latest_record["submission_id"]:
                latest_submission_transition = session.run(
                    """
                    MATCH (prev:Submission)-[rel:NEXT_ATTEMPT]->(curr:Submission {submission_id: $submission_id})
                    RETURN coalesce(prev.testcase_outputs_json, '[]') AS previous_testcase_outputs_json,
                           coalesce(curr.testcase_outputs_json, '[]') AS current_testcase_outputs_json
                    ORDER BY coalesce(rel.linked_at, '') DESC
                    LIMIT 1
                    """,
                    submission_id=latest_record["submission_id"],
                ).single()

            latest_submission_improvement_ratio = 0.0
            latest_submission_regression_ratio = 0.0
            if latest_submission_transition is not None:
                previous_outputs = json.loads(
                    latest_submission_transition["previous_testcase_outputs_json"] or "[]"
                )
                current_outputs = json.loads(
                    latest_submission_transition["current_testcase_outputs_json"] or "[]"
                )
                (
                    latest_submission_improvement_ratio,
                    latest_submission_regression_ratio,
                ) = self._calculate_attempt_transition_scores(
                    previous_outputs=previous_outputs,
                    current_outputs=current_outputs,
                )

            return {
                "current_concept": current_concept,
                "current_concept_weight": float(
                    latest_record["current_concept_weight"] or 1.0
                ),
                "review": review,
                "review_history": review_history,
                "mastered_concepts": latest_record["mastered_concepts"] or [],
                "attempted_exercise_ids": latest_record["attempted_exercise_ids"] or [],
                "latest_submission_improvement_ratio": float(
                    latest_submission_improvement_ratio
                ),
                "latest_submission_regression_ratio": float(
                    latest_submission_regression_ratio
                ),
            }

    def get_latest_review_with_history(
        self,
        *,
        student_id: str,
        current_concept: str = "",
        history_limit: int = 3,
    ) -> tuple[ReviewResponse, list[ReviewRecord]]:
        with self.driver.session() as session:
            latest_record = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(r:Review)
                WHERE $current_concept = '' OR coalesce(r.current_concept, '') = $current_concept
                RETURN r.review_id AS review_id,
                       coalesce(r.summary, '') AS summary,
                       coalesce(r.detail, '') AS detail,
                       coalesce(r.review_items_json, '[]') AS review_items_json,
                       coalesce(r.scorecard_json, '{}') AS scorecard_json,
                       coalesce(r.created_at, '') AS created_at
                ORDER BY r.created_at DESC
                LIMIT 1
                """,
                student_id=student_id,
                current_concept=current_concept,
            ).single()
            if latest_record is None:
                raise ValueError(
                    f"No stored review found for student '{student_id}'"
                    + (f" and concept '{current_concept}'." if current_concept else ".")
                )

            review = ReviewResponse(
                review_id=latest_record["review_id"],
                summary=latest_record["summary"],
                detail=latest_record["detail"],
                review_items=[
                    ReviewItem.model_validate(item)
                    for item in json.loads(latest_record["review_items_json"])
                ],
                scorecard=ScoreCard.model_validate(
                    json.loads(latest_record["scorecard_json"])
                ),
            )

            history_result = session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(r:Review)
                WHERE r.review_id <> $review_id
                  AND ($current_concept = '' OR coalesce(r.current_concept, '') = $current_concept)
                RETURN r.review_id AS review_id,
                       s.student_id AS student_id,
                       coalesce(r.exercise_id, '') AS exercise_id,
                       coalesce(r.submission_id, '') AS submission_id,
                       coalesce(r.current_concept, '') AS current_concept,
                       coalesce(r.created_at, '') AS created_at,
                       coalesce(r.summary, '') AS summary,
                       coalesce(r.detail, '') AS detail
                ORDER BY r.created_at DESC
                LIMIT $history_limit
                """,
                student_id=student_id,
                review_id=review.review_id,
                current_concept=current_concept,
                history_limit=history_limit,
            )
            history = [
                ReviewRecord(
                    review_id=record["review_id"],
                    student_id=record["student_id"],
                    exercise_id=record["exercise_id"],
                    submission_id=record["submission_id"],
                    current_concept=record["current_concept"],
                    created_at=record["created_at"],
                    summary=record["summary"],
                    detail=record["detail"],
                )
                for record in history_result
            ]
            return review, history

    def retrieve_candidates(
        self,
        *,
        student_id: str,
        current_exercise_id: str,
        current_concept: str,
        target_concept: str,
        attempted_exercise_ids: list[str],
        candidate_exercise_ids: list[str] | None = None,
        limit: int = 5,
        allow_indirect_paths: bool = False,
    ) -> list[dict]:
        query = self._candidate_query(allow_indirect_paths=allow_indirect_paths)
        params = {
            "student_id": student_id,
            "current_exercise_id": current_exercise_id,
            "current_concept": current_concept,
            "target_concept": target_concept,
            "attempted_exercise_ids": attempted_exercise_ids,
            "candidate_exercise_ids": candidate_exercise_ids or [],
            "limit": limit,
        }
        with self.driver.session() as session:
            result = session.run(query, **params)
            rows = []
            for record in result:
                rows.append(
                    {
                        "target_concept": record["target_concept"],
                        "concept_name": record["concept_name"],
                        "concept_description": record["concept_description"],
                        "recommended_weight": float(
                            record["recommended_weight"] or 0.0
                        ),
                        "tests_weight": float(record["tests_weight"] or 0.0),
                        "related_weight": float(record["related_weight"] or 0.0),
                        "relation_type": record["relation_type"] or "",
                        "difficulty_gap": float(record["difficulty_gap"] or 0.0),
                        "progression_score": float(record["progression_score"] or 0.0),
                        "similarity_score": float(record["similarity_score"] or 0.0),
                        "root_connection_mode": record["root_connection_mode"]
                        or "fallback",
                        "root_connection_weight": float(
                            record["root_connection_weight"] or 0.0
                        ),
                        "root_hop_count": int(record["root_hop_count"] or 0),
                        "path_relation_types": record["path_relation_types"] or [],
                        "exercise": ExerciseRecord(
                            exercise_id=record["exercise_id"],
                            slug=record["slug"] or "",
                            title=record["title"],
                            description=record["description"],
                            content=record["content"],
                            difficulty=record["difficulty"],
                            concept_slugs=record["concept_slugs"] or [],
                        ),
                    }
                )
            return rows

    def store_recommendation_roadmap(
        self,
        *,
        student_id: str,
        assigned_path: AssignedPath,
        target_concept: str,
        exercise_ids: list[str],
        review_id: str | None = None,
    ) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[r:ASSIGNED]->(:Exercise)
                DELETE r
                """,
                student_id=student_id,
            )
            for order, exercise_id in enumerate(exercise_ids, start=1):
                session.run(
                    """
                    MATCH (s:Student {student_id: $student_id})
                    MATCH (e:Exercise {exercise_id: $exercise_id})
                    MERGE (s)-[r:ASSIGNED]->(e)
                    SET r.path = $assigned_path,
                        r.target_concept = $target_concept,
                        r.sequence = $sequence
                    """,
                    student_id=student_id,
                    exercise_id=exercise_id,
                    assigned_path=assigned_path,
                    target_concept=target_concept,
                    sequence=order,
                )
                if review_id:
                    session.run(
                        """
                        MATCH (r:Review {review_id: $review_id})
                        MATCH (e:Exercise {exercise_id: $exercise_id})
                        MERGE (r)-[rel:RECOMMENDS]->(e)
                        SET rel.path = $assigned_path,
                            rel.target_concept = $target_concept,
                            rel.sequence = $sequence,
                            rel.student_id = $student_id
                        """,
                        review_id=review_id,
                        student_id=student_id,
                        exercise_id=exercise_id,
                        assigned_path=assigned_path,
                        target_concept=target_concept,
                        sequence=order,
                    )

    def _candidate_query(self, *, allow_indirect_paths: bool) -> str:
        if not allow_indirect_paths:
            return """
            MATCH (target:Concept {concept_id: $target_concept})
            MATCH (e:Exercise)-[tests:TESTS]->(target)
            MATCH (e)-[recommended_rel:RECOMMENDED_FOR]->(target)
            OPTIONAL MATCH (current:Exercise {exercise_id: $current_exercise_id})-[direct:RELATED_TO]->(e)
            WHERE NOT e.exercise_id IN $attempted_exercise_ids
              AND (size($candidate_exercise_ids) = 0 OR e.exercise_id IN $candidate_exercise_ids)
              AND NOT EXISTS {
                MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
              }
            RETURN target.concept_id AS target_concept,
                   target.name AS concept_name,
                   coalesce(target.description, '') AS concept_description,
                   coalesce(recommended_rel.weight, 0.0) AS recommended_weight,
                   coalesce(tests.weight, 0.0) AS tests_weight,
                   coalesce(direct.weight, 0.0) AS related_weight,
                   coalesce(direct.relation_type, '') AS relation_type,
                   coalesce(direct.difficulty_gap, 0.0) AS difficulty_gap,
                   coalesce(direct.progression_score, 0.0) AS progression_score,
                   coalesce(direct.similarity_score, 0.0) AS similarity_score,
                   CASE
                       WHEN direct IS NOT NULL THEN 'direct'
                       ELSE 'fallback'
                   END AS root_connection_mode,
                   coalesce(direct.weight, 0.0) AS root_connection_weight,
                   CASE
                       WHEN direct IS NOT NULL THEN 1
                       ELSE 0
                   END AS root_hop_count,
                   CASE
                       WHEN direct IS NOT NULL THEN [coalesce(direct.relation_type, '')]
                       ELSE []
                   END AS path_relation_types,
                   e.exercise_id AS exercise_id,
                   e.title AS title,
                   coalesce(e.description, '') AS description,
                   coalesce(e.content, '') AS content,
                   e.difficulty AS difficulty,
                   coalesce(e.concept_slugs, []) AS concept_slugs
            ORDER BY recommended_weight DESC, tests_weight DESC, related_weight DESC, progression_score DESC, e.title ASC
            LIMIT $limit
        """
        return """
            MATCH (target:Concept {concept_id: $target_concept})
            MATCH (e:Exercise)-[tests:TESTS]->(target)
            MATCH (e)-[recommended_rel:RECOMMENDED_FOR]->(target)
            OPTIONAL MATCH (current:Exercise {exercise_id: $current_exercise_id})-[direct:RELATED_TO]->(e)
            CALL {
                WITH current, e
                OPTIONAL MATCH p=(current)-[:RELATED_TO*2..3]->(e)
                WITH [candidate IN collect(
                    CASE
                        WHEN p IS NULL THEN NULL
                        ELSE {
                            weight: reduce(
                                score = 1.0,
                                rel IN relationships(p) |
                                score * coalesce(rel.weight, 1.0)
                            ) * pow(0.9, length(p) - 1),
                            hop_count: length(p),
                            relation_types: [rel IN relationships(p) | coalesce(rel.relation_type, '')],
                            difficulty_gap: reduce(
                                gap = 0.0,
                                rel IN relationships(p) |
                                gap + coalesce(rel.difficulty_gap, 0.0)
                            ),
                            progression_score: reduce(
                                total = 0.0,
                                rel IN relationships(p) |
                                total + coalesce(rel.progression_score, 0.0)
                            ) / toFloat(length(p)),
                            similarity_score: reduce(
                                total = 0.0,
                                rel IN relationships(p) |
                                total + coalesce(rel.similarity_score, 0.0)
                            ) / toFloat(length(p))
                        }
                    END
                ) WHERE candidate IS NOT NULL] AS indirect_candidates
                RETURN CASE
                    WHEN size(indirect_candidates) = 0 THEN NULL
                    ELSE reduce(
                        best = indirect_candidates[0],
                        candidate IN indirect_candidates[1..] |
                        CASE
                            WHEN candidate.weight > best.weight THEN candidate
                            ELSE best
                        END
                    )
                END AS indirect
            }
            WHERE NOT e.exercise_id IN $attempted_exercise_ids
              AND (size($candidate_exercise_ids) = 0 OR e.exercise_id IN $candidate_exercise_ids)
              AND NOT EXISTS {
                MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
              }
            RETURN target.concept_id AS target_concept,
                   target.name AS concept_name,
                   coalesce(target.description, '') AS concept_description,
                   coalesce(recommended_rel.weight, 0.0) AS recommended_weight,
                   coalesce(tests.weight, 0.0) AS tests_weight,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.weight, 0.0)
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.weight, 0.0)
                       ELSE 0.0
                   END AS related_weight,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.relation_type, '')
                       WHEN indirect IS NOT NULL THEN 'INDIRECT_PATH'
                       ELSE ''
                   END AS relation_type,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.difficulty_gap, 0.0)
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.difficulty_gap, 0.0)
                       ELSE 0.0
                   END AS difficulty_gap,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.progression_score, 0.0)
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.progression_score, 0.0)
                       ELSE 0.0
                   END AS progression_score,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.similarity_score, 0.0)
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.similarity_score, 0.0)
                       ELSE 0.0
                   END AS similarity_score,
                   CASE
                       WHEN direct IS NOT NULL THEN 'direct'
                       WHEN indirect IS NOT NULL THEN 'indirect'
                       ELSE 'fallback'
                   END AS root_connection_mode,
                   CASE
                       WHEN direct IS NOT NULL THEN coalesce(direct.weight, 0.0)
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.weight, 0.0)
                       ELSE 0.0
                   END AS root_connection_weight,
                   CASE
                       WHEN direct IS NOT NULL THEN 1
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.hop_count, 0)
                       ELSE 0
                   END AS root_hop_count,
                   CASE
                       WHEN direct IS NOT NULL THEN [coalesce(direct.relation_type, '')]
                       WHEN indirect IS NOT NULL THEN coalesce(indirect.relation_types, [])
                       ELSE []
                   END AS path_relation_types,
                   e.exercise_id AS exercise_id,
                   e.title AS title,
                   coalesce(e.description, '') AS description,
                   coalesce(e.content, '') AS content,
                   e.difficulty AS difficulty,
                   coalesce(e.concept_slugs, []) AS concept_slugs
            ORDER BY recommended_weight DESC, tests_weight DESC, related_weight DESC, progression_score DESC, e.title ASC
            LIMIT $limit
        """
