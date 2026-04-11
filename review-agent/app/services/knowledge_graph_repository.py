from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from neo4j import Driver

from app.api.review_code_schema import ReviewItem, ReviewResponse, ScoreCard
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import (
    AssignedPath,
    ConceptRecord,
    ConceptRelation,
    ExerciseConceptLink,
    ExercisePathLink,
    KnowledgeGraphDocument,
)
from app.models.review_record import ReviewRecord
from app.models.student_profile import StudentProfileScoring
from app.models.student_record import StudentRecord


class KnowledgeGraphRepository:
    """Neo4j-backed repository for GraphRAG recommendation data."""

    def __init__(self, driver: Driver):
        self.driver = driver

    def upsert_concept(
        self, concept: ConceptRecord, prerequisite_ids: list[str] | None = None
    ) -> ConceptRecord:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (c:Concept {concept_id: $concept_id})
                SET c.name = $name,
                    c.description = $description,
                    c.difficulty = $difficulty
                """,
                concept_id=concept.concept_id,
                name=concept.name,
                description=concept.description,
                difficulty=concept.difficulty,
            )

            for prerequisite_id in prerequisite_ids or []:
                session.run(
                    """
                    MERGE (p:Concept {concept_id: $prerequisite_id})
                    ON CREATE SET p.name = $prerequisite_id, p.description = '', p.difficulty = 1
                    WITH p
                    MATCH (c:Concept {concept_id: $concept_id})
                    MERGE (p)-[:PREREQUISITE_OF]->(c)
                    """,
                    prerequisite_id=prerequisite_id,
                    concept_id=concept.concept_id,
                )

        return concept

    def upsert_exercise(
        self,
        exercise: ExerciseRecord,
        concept_ids: list[str],
        recommended_paths: list[AssignedPath],
    ) -> ExerciseRecord:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (e:Exercise {exercise_id: $exercise_id})
                SET e.title = $title,
                    e.description = $description,
                    e.content = $content,
                    e.difficulty = $difficulty,
                    e.tags = $tags
                """,
                exercise_id=exercise.exercise_id,
                title=exercise.title,
                description=exercise.description,
                content=exercise.content,
                difficulty=exercise.difficulty,
                tags=exercise.tags,
            )

            session.run(
                """
                MATCH (e:Exercise {exercise_id: $exercise_id})-[r:TESTS]->(:Concept)
                DELETE r
                """,
                exercise_id=exercise.exercise_id,
            )
            session.run(
                """
                MATCH (e:Exercise {exercise_id: $exercise_id})-[r:RECOMMENDED_FOR]->(:Concept)
                DELETE r
                """,
                exercise_id=exercise.exercise_id,
            )

            for concept_id in concept_ids:
                session.run(
                    """
                    MERGE (c:Concept {concept_id: $concept_id})
                    ON CREATE SET c.name = $concept_id, c.description = '', c.difficulty = 1
                    WITH c
                    MATCH (e:Exercise {exercise_id: $exercise_id})
                    MERGE (e)-[:TESTS {weight: 1.0}]->(c)
                    """,
                    concept_id=concept_id,
                    exercise_id=exercise.exercise_id,
                )
                for path in recommended_paths:
                    session.run(
                        """
                        MATCH (e:Exercise {exercise_id: $exercise_id})
                        MATCH (c:Concept {concept_id: $concept_id})
                        MERGE (e)-[:RECOMMENDED_FOR {path: $path}]->(c)
                        """,
                        exercise_id=exercise.exercise_id,
                        concept_id=concept_id,
                        path=path,
                    )

        return exercise

    def upsert_student(
        self,
        *,
        student: StudentRecord,
        student_profile: StudentProfileScoring,
        mastered_concepts: list[str],
        attempted_exercise_ids: list[str],
    ) -> StudentRecord:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                SET s.current_concept = $current_concept,
                    s.notes = $notes,
                    s.concept_mastery = $concept_mastery,
                    s.implementation_consistency = $implementation_consistency,
                    s.debugging_independence = $debugging_independence,
                    s.efficiency_awareness = $efficiency_awareness,
                    s.concept_transfer = $concept_transfer,
                    s.learning_velocity = $learning_velocity,
                    s.profile_notes = $profile_notes
                """,
                student_id=student.student_id,
                current_concept=student.current_concept,
                notes=student.notes,
                concept_mastery=student_profile.concept_mastery,
                implementation_consistency=student_profile.implementation_consistency,
                debugging_independence=student_profile.debugging_independence,
                efficiency_awareness=student_profile.efficiency_awareness,
                concept_transfer=student_profile.concept_transfer,
                learning_velocity=student_profile.learning_velocity,
                profile_notes=student_profile.notes,
            )

            session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[r:MASTERED]->(:Concept)
                DELETE r
                """,
                student_id=student.student_id,
            )
            for concept_id in mastered_concepts:
                session.run(
                    """
                    MERGE (c:Concept {concept_id: $concept_id})
                    ON CREATE SET c.name = $concept_id, c.description = '', c.difficulty = 1
                    WITH c
                    MATCH (s:Student {student_id: $student_id})
                    MERGE (s)-[:MASTERED]->(c)
                    """,
                    student_id=student.student_id,
                    concept_id=concept_id,
                )

            for exercise_id in attempted_exercise_ids:
                session.run(
                    """
                    MATCH (s:Student {student_id: $student_id})
                    MATCH (e:Exercise {exercise_id: $exercise_id})
                    MERGE (s)-[:ATTEMPTED]->(e)
                    """,
                    student_id=student.student_id,
                    exercise_id=exercise_id,
                )

        return student

    def upsert_review(
        self,
        *,
        student_id: str,
        exercise_id: str,
        submission_id: str,
        summary: str,
        detail: str,
        review_items: list[dict],
        scorecard: dict,
        current_concept: str = "",
        review_id: str | None = None,
    ) -> ReviewRecord:
        resolved_review_id = review_id or str(uuid4())
        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                ON CREATE SET s.current_concept = $current_concept, s.notes = ''
                MERGE (e:Exercise {exercise_id: $exercise_id})
                ON CREATE SET e.title = $exercise_id,
                              e.description = '',
                              e.content = '',
                              e.difficulty = 'unknown',
                              e.tags = []
                WITH s
                MERGE (r:Review {review_id: $review_id})
                SET r.summary = $summary,
                    r.detail = $detail,
                    r.student_id = $student_id,
                    r.exercise_id = $exercise_id,
                    r.submission_id = $submission_id,
                    r.current_concept = $current_concept,
                    r.created_at = $created_at,
                    r.review_items_json = $review_items_json,
                    r.scorecard_json = $scorecard_json
                MERGE (s)-[:RECEIVED_REVIEW]->(r)
                WITH r, $exercise_id AS exercise_id
                MATCH (e:Exercise {exercise_id: exercise_id})
                MERGE (r)-[:REVIEWS_EXERCISE]->(e)
                """,
                student_id=student_id,
                exercise_id=exercise_id,
                submission_id=submission_id,
                current_concept=current_concept,
                review_id=resolved_review_id,
                summary=summary,
                detail=detail,
                created_at=datetime.now(timezone.utc).isoformat(),
                review_items_json=json.dumps(review_items),
                scorecard_json=json.dumps(scorecard),
            )
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})-[:RECEIVED_REVIEW]->(new_review:Review {review_id: $review_id})
                OPTIONAL MATCH (s)-[:RECEIVED_REVIEW]->(prev:Review)
                WHERE prev.review_id <> $review_id
                WITH new_review, prev
                ORDER BY prev.created_at DESC
                WITH new_review, head(collect(prev)) AS latest_prev
                FOREACH (_ IN CASE WHEN latest_prev IS NULL THEN [] ELSE [1] END |
                  MERGE (latest_prev)-[rel:NEXT_REVIEW_OF]->(new_review)
                  SET rel.student_id = $student_id,
                      rel.linked_at = $linked_at,
                      rel.same_concept = coalesce(latest_prev.current_concept, '') = coalesce(new_review.current_concept, '')
                )
                """,
                student_id=student_id,
                review_id=resolved_review_id,
                linked_at=datetime.now(timezone.utc).isoformat(),
            )
        return ReviewRecord(
            review_id=resolved_review_id,
            student_id=student_id,
            exercise_id=exercise_id,
            submission_id=submission_id,
            current_concept=current_concept,
            summary=summary,
            detail=detail,
        )

    def recalculate_student_profile_from_review(
        self,
        *,
        student_id: str,
        exercise_id: str,
        current_concept: str,
        scorecard: dict,
    ) -> StudentProfileScoring:
        derived_profile = self._derive_profile_from_scorecard(scorecard)
        with self.driver.session() as session:
            existing = session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                RETURN s.concept_mastery AS concept_mastery,
                       s.implementation_consistency AS implementation_consistency,
                       s.debugging_independence AS debugging_independence,
                       s.efficiency_awareness AS efficiency_awareness,
                       s.concept_transfer AS concept_transfer,
                       s.learning_velocity AS learning_velocity,
                       coalesce(s.profile_notes, '') AS profile_notes
                """,
                student_id=student_id,
            ).single()

            blended_profile = self._blend_student_profile(existing, derived_profile)
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                SET s.current_concept = $current_concept,
                    s.notes = coalesce(s.notes, ''),
                    s.concept_mastery = $concept_mastery,
                    s.implementation_consistency = $implementation_consistency,
                    s.debugging_independence = $debugging_independence,
                    s.efficiency_awareness = $efficiency_awareness,
                    s.concept_transfer = $concept_transfer,
                    s.learning_velocity = $learning_velocity,
                    s.profile_notes = $profile_notes
                """,
                student_id=student_id,
                current_concept=current_concept,
                concept_mastery=blended_profile.concept_mastery,
                implementation_consistency=blended_profile.implementation_consistency,
                debugging_independence=blended_profile.debugging_independence,
                efficiency_awareness=blended_profile.efficiency_awareness,
                concept_transfer=blended_profile.concept_transfer,
                learning_velocity=blended_profile.learning_velocity,
                profile_notes=blended_profile.notes,
            )
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (e:Exercise {exercise_id: $exercise_id})
                MERGE (s)-[:ATTEMPTED]->(e)
                """,
                student_id=student_id,
                exercise_id=exercise_id,
            )
        return blended_profile

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
                       coalesce(r.exercise_id, $exercise_id) AS stored_exercise_id,
                       coalesce(r.submission_id, '') AS submission_id,
                       coalesce(s.concept_mastery, 3) AS concept_mastery,
                       coalesce(s.implementation_consistency, 3) AS implementation_consistency,
                       coalesce(s.debugging_independence, 3) AS debugging_independence,
                       coalesce(s.efficiency_awareness, 3) AS efficiency_awareness,
                       coalesce(s.concept_transfer, 3) AS concept_transfer,
                       coalesce(s.learning_velocity, 3) AS learning_velocity,
                       coalesce(s.profile_notes, '') AS profile_notes,
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

            student_profile = StudentProfileScoring(
                concept_mastery=latest_record["concept_mastery"],
                implementation_consistency=latest_record["implementation_consistency"],
                debugging_independence=latest_record["debugging_independence"],
                efficiency_awareness=latest_record["efficiency_awareness"],
                concept_transfer=latest_record["concept_transfer"],
                learning_velocity=latest_record["learning_velocity"],
                notes=latest_record["profile_notes"],
            )
            return {
                "current_concept": current_concept,
                "review": review,
                "review_history": review_history,
                "student_profile": student_profile,
                "mastered_concepts": latest_record["mastered_concepts"] or [],
                "attempted_exercise_ids": latest_record["attempted_exercise_ids"] or [],
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

    def get_next_concepts(self, concept_id: str) -> list[ConceptRecord]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (:Concept {concept_id: $concept_id})-[:PREREQUISITE_OF]->(next:Concept)
                RETURN next.concept_id AS concept_id,
                       next.name AS name,
                       coalesce(next.description, '') AS description,
                       coalesce(next.difficulty, 1) AS difficulty
                ORDER BY next.difficulty ASC, next.name ASC
                """,
                concept_id=concept_id,
            )
            return [
                ConceptRecord(
                    concept_id=record["concept_id"],
                    name=record["name"] or record["concept_id"],
                    description=record["description"],
                    difficulty=record["difficulty"],
                )
                for record in result
            ]

    def retrieve_candidates(
        self,
        *,
        student_id: str,
        current_concept: str,
        assigned_path: AssignedPath,
        mastered_concepts: list[str],
        attempted_exercise_ids: list[str],
        limit: int = 5,
    ) -> list[dict]:
        query = self._candidate_query(assigned_path)
        params = {
            "student_id": student_id,
            "current_concept": current_concept,
            "assigned_path": assigned_path,
            "mastered_concepts": mastered_concepts,
            "attempted_exercise_ids": attempted_exercise_ids,
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
                        "exercise": ExerciseRecord(
                            exercise_id=record["exercise_id"],
                            title=record["title"],
                            description=record["description"],
                            content=record["content"],
                            difficulty=record["difficulty"],
                            tags=record["tags"] or [],
                        ),
                    }
                )
            return rows

    def get_graph_snapshot(self) -> KnowledgeGraphDocument:
        with self.driver.session() as session:
            concepts = [
                ConceptRecord(
                    concept_id=record["concept_id"],
                    name=record["name"] or record["concept_id"],
                    description=record["description"],
                    difficulty=record["difficulty"],
                )
                for record in session.run(
                    """
                    MATCH (c:Concept)
                    RETURN c.concept_id AS concept_id,
                           c.name AS name,
                           coalesce(c.description, '') AS description,
                           coalesce(c.difficulty, 1) AS difficulty
                    ORDER BY c.name ASC
                    """
                )
            ]
            relations = [
                ConceptRelation(
                    prerequisite_id=record["prerequisite_id"],
                    concept_id=record["concept_id"],
                )
                for record in session.run(
                    """
                    MATCH (p:Concept)-[:PREREQUISITE_OF]->(c:Concept)
                    RETURN p.concept_id AS prerequisite_id, c.concept_id AS concept_id
                    """
                )
            ]
            exercises = [
                ExerciseRecord(
                    exercise_id=record["exercise_id"],
                    title=record["title"],
                    description=record["description"],
                    content=record["content"],
                    difficulty=record["difficulty"],
                    tags=record["tags"] or [],
                )
                for record in session.run(
                    """
                    MATCH (e:Exercise)
                    RETURN e.exercise_id AS exercise_id,
                           e.title AS title,
                           coalesce(e.description, '') AS description,
                           coalesce(e.content, '') AS content,
                           e.difficulty AS difficulty,
                           coalesce(e.tags, []) AS tags
                    ORDER BY e.title ASC
                    """
                )
            ]
            exercise_concept_links = [
                ExerciseConceptLink(
                    exercise_id=record["exercise_id"],
                    concept_id=record["concept_id"],
                    weight=record["weight"],
                )
                for record in session.run(
                    """
                    MATCH (e:Exercise)-[r:TESTS]->(c:Concept)
                    RETURN e.exercise_id AS exercise_id,
                           c.concept_id AS concept_id,
                           coalesce(r.weight, 1.0) AS weight
                    """
                )
            ]
            exercise_path_links = [
                ExercisePathLink(
                    exercise_id=record["exercise_id"],
                    path=record["path"],
                )
                for record in session.run(
                    """
                    MATCH (e:Exercise)-[r:RECOMMENDED_FOR]->(:Concept)
                    RETURN e.exercise_id AS exercise_id, r.path AS path
                    """
                )
            ]
            students = [
                StudentRecord(
                    student_id=record["student_id"],
                    current_concept=record["current_concept"],
                    notes=record["notes"],
                )
                for record in session.run(
                    """
                    MATCH (s:Student)
                    RETURN s.student_id AS student_id,
                           coalesce(s.current_concept, '') AS current_concept,
                           coalesce(s.notes, '') AS notes
                    ORDER BY s.student_id ASC
                    """
                )
            ]
            reviews = [
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
                    MATCH (s:Student)-[:RECEIVED_REVIEW]->(r:Review)
                    RETURN r.review_id AS review_id,
                           s.student_id AS student_id,
                           coalesce(r.exercise_id, '') AS exercise_id,
                           coalesce(r.submission_id, '') AS submission_id,
                           coalesce(r.current_concept, '') AS current_concept,
                           coalesce(r.created_at, '') AS created_at,
                           coalesce(r.summary, '') AS summary,
                           coalesce(r.detail, '') AS detail
                    ORDER BY r.created_at DESC, r.review_id ASC
                    """
                )
            ]

        return KnowledgeGraphDocument(
            concepts=concepts,
            concept_relations=relations,
            exercises=exercises,
            exercise_concept_links=exercise_concept_links,
            exercise_path_links=exercise_path_links,
            students=students,
            reviews=reviews,
        )

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

    def _candidate_query(self, assigned_path: AssignedPath) -> str:
        if assigned_path == "NEXT_CONCEPT":
            return """
                MATCH (:Concept {concept_id: $current_concept})-[:PREREQUISITE_OF]->(target:Concept)
                WHERE NOT target.concept_id IN $mastered_concepts
                MATCH (e:Exercise)-[:TESTS]->(target)
                MATCH (e)-[:RECOMMENDED_FOR {path: $assigned_path}]->(target)
                WHERE NOT e.exercise_id IN $attempted_exercise_ids
                  AND NOT EXISTS {
                    MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
                  }
                RETURN target.concept_id AS target_concept,
                       target.name AS concept_name,
                       coalesce(target.description, '') AS concept_description,
                       e.exercise_id AS exercise_id,
                       e.title AS title,
                       coalesce(e.description, '') AS description,
                       coalesce(e.content, '') AS content,
                       e.difficulty AS difficulty,
                       coalesce(e.tags, []) AS tags
                ORDER BY target.difficulty ASC, e.title ASC
                LIMIT $limit
            """

        return """
            MATCH (target:Concept {concept_id: $current_concept})
            MATCH (e:Exercise)-[:TESTS]->(target)
            MATCH (e)-[:RECOMMENDED_FOR {path: $assigned_path}]->(target)
            WHERE NOT e.exercise_id IN $attempted_exercise_ids
              AND NOT EXISTS {
                MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
              }
            RETURN target.concept_id AS target_concept,
                   target.name AS concept_name,
                   coalesce(target.description, '') AS concept_description,
                   e.exercise_id AS exercise_id,
                   e.title AS title,
                   coalesce(e.description, '') AS description,
                   coalesce(e.content, '') AS content,
                   e.difficulty AS difficulty,
                   coalesce(e.tags, []) AS tags
            ORDER BY e.title ASC
            LIMIT $limit
        """

    @staticmethod
    def _derive_profile_from_scorecard(scorecard: dict) -> StudentProfileScoring:
        def score(name: str) -> int:
            return int(scorecard.get(name, {}).get("score", 3))

        def average(*values: int) -> int:
            return max(1, min(5, round(sum(values) / len(values))))

        return StudentProfileScoring(
            concept_mastery=average(
                score("logic_traceability"),
                score("control_flow_understanding"),
                score("input_output_awareness"),
                score("edge_case_awareness"),
            ),
            implementation_consistency=average(
                score("construct_appropriateness"),
                score("variable_understanding"),
                score("logic_traceability"),
            ),
            debugging_independence=average(
                score("self_correction_path"),
                score("debugging_readiness"),
            ),
            efficiency_awareness=average(
                score("construct_appropriateness"),
                score("generalization_score"),
            ),
            concept_transfer=average(
                score("generalization_score"),
                score("problem_solving_creativity"),
            ),
            learning_velocity=average(
                score("self_correction_path"),
                score("problem_solving_creativity"),
                score("debugging_readiness"),
            ),
            notes="Auto-derived from stored review scorecards.",
        )

    def _blend_student_profile(
        self, existing: object, derived: StudentProfileScoring
    ) -> StudentProfileScoring:
        if existing is None:
            return derived

        def blended(field_name: str, incoming: int) -> int:
            existing_value = getattr(existing, "get", None)
            previous = existing.get(field_name) if callable(existing_value) else None
            if previous is None:
                return incoming
            return max(1, min(5, round(previous * 0.4 + incoming * 0.6)))

        notes = "Blended from the latest stored review and previous student profile."
        return StudentProfileScoring(
            concept_mastery=blended("concept_mastery", derived.concept_mastery),
            implementation_consistency=blended(
                "implementation_consistency",
                derived.implementation_consistency,
            ),
            debugging_independence=blended(
                "debugging_independence",
                derived.debugging_independence,
            ),
            efficiency_awareness=blended(
                "efficiency_awareness",
                derived.efficiency_awareness,
            ),
            concept_transfer=blended("concept_transfer", derived.concept_transfer),
            learning_velocity=blended(
                "learning_velocity",
                derived.learning_velocity,
            ),
            notes=notes,
        )
