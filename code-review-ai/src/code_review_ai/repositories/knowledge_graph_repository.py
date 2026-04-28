from __future__ import annotations

import json
from datetime import datetime, timezone
from neo4j import Driver

from code_review_ai.api.review_code_schema import ReviewItem, ReviewResponse, ScoreCard
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import (
    AssignedPath,
    ConceptRecord,
    ConceptRelation,
    ExerciseConceptLink,
    ExerciseRelation,
    ExercisePathLink,
    KnowledgeGraphDocument,
    ReviewRelation,
    SubmissionRelation,
)
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.student_profile import StudentProfileScoring
from code_review_ai.models.submission_record import SubmissionRecord
from code_review_ai.models.student_record import StudentRecord


class KnowledgeGraphRepository:
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

    @staticmethod
    def _scorecard_average(scorecard: dict) -> float:
        scores: list[float] = []
        for item in scorecard.values():
            if not isinstance(item, dict):
                continue
            raw_score = item.get("score")
            if raw_score is None:
                continue
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                continue
            scores.append(max(1.0, min(5.0, score)))
        return sum(scores) / len(scores) if scores else 0.0

    @staticmethod
    def _review_severity(review_items: list[dict]) -> float:
        if not review_items:
            return 0.0

        severity_by_type = {
            "Error": 1.0,
            "Warning": 0.5,
        }
        severities = [
            severity_by_type.get(str(item.get("type", "")).strip(), 0.25)
            for item in review_items
        ]
        return sum(severities) / len(severities) if severities else 0.0

    def _calculate_review_transition_scores(
        self,
        previous_scorecard: dict,
        current_scorecard: dict,
        previous_review_items: list[dict],
        current_review_items: list[dict],
    ) -> tuple[float, float]:
        previous_average = self._scorecard_average(previous_scorecard)
        current_average = self._scorecard_average(current_scorecard)
        normalized_score_delta = (current_average - previous_average) / 4.0

        previous_severity = self._review_severity(previous_review_items)
        current_severity = self._review_severity(current_review_items)
        severity_change = max(-1.0, min(1.0, current_severity - previous_severity))

        improvement_signal = max(
            0.0,
            min(
                1.0,
                0.6 * max(normalized_score_delta, 0.0)
                + 0.4 * max(previous_severity - current_severity, 0.0),
            ),
        )
        return improvement_signal, severity_change

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
                       coalesce(e.tags, []) AS tags
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
                    tags=record["tags"] or [],
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
                       coalesce(e.tags, []) AS tags
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
                        tags=record["tags"] or [],
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
            recommended_paths = [
                {
                    "concept_id": record["concept_id"],
                    "path": record["path"],
                    "weight": float(record["weight"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:RECOMMENDED_FOR]->(c:Concept)
                    RETURN c.concept_id AS concept_id,
                           r.path AS path,
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
                RETURN coalesce(s.concept_mastery, 0.5) AS concept_mastery,
                       coalesce(s.implementation_consistency, 0.5) AS implementation_consistency,
                       coalesce(s.debugging_independence, 0.5) AS debugging_independence,
                       coalesce(s.efficiency_awareness, 0.5) AS efficiency_awareness,
                       coalesce(s.concept_transfer, 0.5) AS concept_transfer,
                       coalesce(s.learning_velocity, 0.5) AS learning_velocity,
                       coalesce(s.profile_notes, '') AS profile_notes,
                       mastered_concepts AS mastered_concepts,
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
            "recommended_paths": recommended_paths,
            "review": review,
            "review_record": review_record,
            "student_profile": StudentProfileScoring(
                concept_mastery=student_record["concept_mastery"],
                implementation_consistency=student_record["implementation_consistency"],
                debugging_independence=student_record["debugging_independence"],
                efficiency_awareness=student_record["efficiency_awareness"],
                concept_transfer=student_record["concept_transfer"],
                learning_velocity=student_record["learning_velocity"],
                notes=student_record["profile_notes"],
            ),
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
            latest_transition = session.run(
                """
                MATCH (prev:Review)-[rel:NEXT_REVIEW_OF]->(curr:Review {review_id: $review_id})
                RETURN prev.review_id AS previous_review_id,
                       coalesce(rel.improvement_signal, 0.0) AS improvement_signal,
                       coalesce(rel.severity_change, 0.0) AS severity_change
                ORDER BY coalesce(rel.linked_at, '') DESC
                LIMIT 1
                """,
                review_id=review_id,
            ).single()

        return {
            "review_history": review_history,
            "latest_review_improvement_signal": float(
                latest_transition["improvement_signal"] if latest_transition else 0.0
            ),
            "latest_review_severity_change": float(
                latest_transition["severity_change"] if latest_transition else 0.0
            ),
            "previous_review_id": (
                str(latest_transition["previous_review_id"]) if latest_transition else ""
            ),
        }

    def fetch_submission_trend_context(self, *, submission_id: str) -> dict:
        with self.driver.session() as session:
            latest_transition = session.run(
                """
                MATCH (prev:Submission)-[rel:NEXT_ATTEMPT]->(curr:Submission {submission_id: $submission_id})
                RETURN prev.submission_id AS previous_submission_id,
                       coalesce(rel.improvement_ratio, 0.0) AS improvement_ratio,
                       coalesce(rel.regression_ratio, 0.0) AS regression_ratio
                ORDER BY coalesce(rel.linked_at, '') DESC
                LIMIT 1
                """,
                submission_id=submission_id,
            ).single()
        return {
            "latest_submission_improvement_ratio": float(
                latest_transition["improvement_ratio"] if latest_transition else 0.0
            ),
            "latest_submission_regression_ratio": float(
                latest_transition["regression_ratio"] if latest_transition else 0.0
            ),
            "previous_submission_id": (
                str(latest_transition["previous_submission_id"]) if latest_transition else ""
            ),
        }

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
                    "target_concept_id": record["target_concept_id"] or "",
                    "shared_concept_ids": record["shared_concept_ids"] or [],
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
                           coalesce(r.target_concept_id, '') AS target_concept_id,
                           coalesce(r.shared_concept_ids, []) AS shared_concept_ids,
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
            path_links = [
                {
                    "concept_id": record["concept_id"],
                    "path": record["path"],
                    "weight": float(record["weight"] or 0.0),
                }
                for record in session.run(
                    """
                    MATCH (:Exercise {exercise_id: $exercise_id})-[r:RECOMMENDED_FOR]->(c:Concept)
                    WHERE $focus_concept_id = '' OR c.concept_id = $focus_concept_id
                    RETURN c.concept_id AS concept_id,
                           r.path AS path,
                           coalesce(r.weight, 1.0) AS weight
                    ORDER BY weight DESC, c.concept_id ASC
                    """,
                    exercise_id=exercise_id,
                    focus_concept_id=focus_concept_id,
                )
            ]
        return {
            "related_exercises": related_exercises,
            "path_links": path_links,
        }

    def fetch_concept_progression_context(
        self,
        *,
        current_concept: str,
        attempted_exercise_ids: list[str],
        mastered_concepts: list[str],
        limit: int = 5,
    ) -> list[dict]:
        return self.get_next_concept_candidates(
            current_concept=current_concept,
            attempted_exercise_ids=attempted_exercise_ids,
            mastered_concepts=mastered_concepts,
            limit=limit,
        )

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
        with self.driver.session() as session:
            session.run(
                """
                MERGE (c:Concept {slug: $slug})
                SET c.concept_id = $concept_id,
                    c.slug = $slug,
                    c.name = $name,
                    c.description = $description,
                    c.difficulty = $difficulty
                """,
                concept_id=concept.concept_id,
                slug=concept.slug,
                name=concept.name,
                description=concept.description,
                difficulty=concept.difficulty,
            )
        return concept

    def replace_concept_prerequisites(
        self,
        *,
        concept_slug: str,
        prerequisites: list[tuple[ConceptRecord, float]],
    ) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (:Concept)-[r:PREREQUISITE_OF]->(c:Concept {slug: $concept_slug})
                DELETE r
                """,
                concept_slug=concept_slug,
            )

            for prerequisite, strength in prerequisites:
                session.run(
                    """
                    MATCH (p:Concept {slug: $prerequisite_slug})
                    MATCH (c:Concept {slug: $concept_slug})
                    MERGE (p)-[r:PREREQUISITE_OF]->(c)
                    SET r.strength = $strength
                    """,
                    prerequisite_slug=prerequisite.slug,
                    concept_slug=concept_slug,
                    strength=strength,
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
                    e.tags = row.tags
                """,
                rows=[
                    {
                        "exercise_id": exercise.exercise_id,
                        "slug": exercise.slug,
                        "title": exercise.title,
                        "description": exercise.description,
                        "content": exercise.content,
                        "difficulty": exercise.difficulty,
                        "tags": exercise.tags,
                    }
                    for exercise in exercises
                ],
            )
        return exercises

    def replace_exercise_concepts(
        self,
        *,
        exercise_id: str,
        concepts: list[tuple[ConceptRecord, float, list[dict]]],
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
            for concept, weight, recommended_paths in item.get("concepts", []):
                tests_rows.append(
                    {
                        "exercise_id": exercise_id,
                        "concept_id": concept.concept_id,
                        "weight": weight,
                    }
                )
                for path_config in recommended_paths:
                    recommended_rows.append(
                        {
                            "exercise_id": exercise_id,
                            "concept_id": concept.concept_id,
                            "path": path_config["path"],
                            "weight": path_config.get("weight", 1.0),
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
                    MERGE (e)-[r:RECOMMENDED_FOR {path: row.path}]->(c)
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
        student_profile: StudentProfileScoring,
    ) -> StudentProfileScoring:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                SET s.current_concept = coalesce(s.current_concept, ''),
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
                concept_mastery=student_profile.concept_mastery,
                implementation_consistency=student_profile.implementation_consistency,
                debugging_independence=student_profile.debugging_independence,
                efficiency_awareness=student_profile.efficiency_awareness,
                concept_transfer=student_profile.concept_transfer,
                learning_velocity=student_profile.learning_velocity,
                profile_notes=student_profile.notes,
            )
        return student_profile

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
                RETURN coalesce(sub.created_at, '') AS created_at,
                       coalesce(sub.testcase_outputs_json, '[]') AS testcase_outputs_json
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
                       coalesce(prev.testcase_outputs_json, '[]') AS testcase_outputs_json,
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
                       coalesce(next.testcase_outputs_json, '[]') AS testcase_outputs_json,
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
                previous_outputs = json.loads(
                    previous_submission["testcase_outputs_json"] or "[]"
                )
                improvement_ratio, regression_ratio = (
                    self._calculate_attempt_transition_scores(
                        previous_outputs=previous_outputs,
                        current_outputs=testcase_outputs,
                    )
                )
                session.run(
                    """
                    MATCH (prev:Submission {submission_id: $previous_submission_id})
                    MATCH (curr:Submission {submission_id: $submission_id})
                    MERGE (prev)-[r:NEXT_ATTEMPT]->(curr)
                    SET r.student_id = $student_id,
                        r.linked_at = $linked_at,
                        r.same_exercise = true,
                        r.improvement_ratio = $improvement_ratio,
                        r.regression_ratio = $regression_ratio
                    """,
                    previous_submission_id=previous_submission["submission_id"],
                    submission_id=submission_id,
                    student_id=student_id,
                    linked_at=created_at,
                    improvement_ratio=improvement_ratio,
                    regression_ratio=regression_ratio,
                )

            if next_submission is not None:
                next_outputs = json.loads(next_submission["testcase_outputs_json"] or "[]")
                improvement_ratio, regression_ratio = (
                    self._calculate_attempt_transition_scores(
                        previous_outputs=testcase_outputs,
                        current_outputs=next_outputs,
                    )
                )
                session.run(
                    """
                    MATCH (curr:Submission {submission_id: $submission_id})
                    MATCH (next:Submission {submission_id: $next_submission_id})
                    MERGE (curr)-[r:NEXT_ATTEMPT]->(next)
                    SET r.student_id = $student_id,
                        r.linked_at = $linked_at,
                        r.same_exercise = true,
                        r.improvement_ratio = $improvement_ratio,
                        r.regression_ratio = $regression_ratio
                    """,
                    submission_id=submission_id,
                    next_submission_id=next_submission["submission_id"],
                    student_id=student_id,
                    linked_at=created_at,
                    improvement_ratio=improvement_ratio,
                    regression_ratio=regression_ratio,
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
                       coalesce(review.review_items_json, '[]') AS review_items_json,
                       coalesce(review.scorecard_json, '{}') AS scorecard_json,
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
                       coalesce(prev.created_at, '') AS created_at,
                       coalesce(prev.current_concept, '') AS current_concept,
                       coalesce(prev.review_items_json, '[]') AS review_items_json,
                       coalesce(prev.scorecard_json, '{}') AS scorecard_json
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
                       coalesce(next.created_at, '') AS created_at,
                       coalesce(next.current_concept, '') AS current_concept,
                       coalesce(next.review_items_json, '[]') AS review_items_json,
                       coalesce(next.scorecard_json, '{}') AS scorecard_json
                ORDER BY next.created_at ASC, next.review_id ASC
                LIMIT 1
                """,
                student_id=student_id,
                review_id=review_id,
                current_created_at=current_created_at,
            ).single()

            current_review_items = json.loads(
                (current_review["review_items_json"] if current_review else "[]") or "[]"
            )
            current_scorecard = json.loads(
                (current_review["scorecard_json"] if current_review else "{}") or "{}"
            )
            current_concept_value = (
                current_review["current_concept"] if current_review else current_concept
            ) or ""

            if previous_review is not None:
                previous_review_items = json.loads(
                    previous_review["review_items_json"] or "[]"
                )
                previous_scorecard = json.loads(
                    previous_review["scorecard_json"] or "{}"
                )
                improvement_signal, severity_change = (
                    self._calculate_review_transition_scores(
                        previous_scorecard=previous_scorecard,
                        current_scorecard=current_scorecard,
                        previous_review_items=previous_review_items,
                        current_review_items=current_review_items,
                    )
                )
                session.run(
                    """
                    MATCH (prev:Review {review_id: $previous_review_id})
                    MATCH (curr:Review {review_id: $review_id})
                    MERGE (prev)-[rel:NEXT_REVIEW_OF]->(curr)
                    SET rel.student_id = $student_id,
                        rel.linked_at = $linked_at,
                        rel.same_concept = $same_concept,
                        rel.improvement_signal = $improvement_signal,
                        rel.severity_change = $severity_change
                    """,
                    previous_review_id=previous_review["review_id"],
                    review_id=review_id,
                    student_id=student_id,
                    linked_at=created_at,
                    same_concept=(previous_review["current_concept"] or "")
                    == current_concept_value,
                    improvement_signal=improvement_signal,
                    severity_change=severity_change,
                )

            if next_review is not None:
                next_review_items = json.loads(next_review["review_items_json"] or "[]")
                next_scorecard = json.loads(next_review["scorecard_json"] or "{}")
                improvement_signal, severity_change = (
                    self._calculate_review_transition_scores(
                        previous_scorecard=current_scorecard,
                        current_scorecard=next_scorecard,
                        previous_review_items=current_review_items,
                        current_review_items=next_review_items,
                    )
                )
                session.run(
                    """
                    MATCH (curr:Review {review_id: $review_id})
                    MATCH (next:Review {review_id: $next_review_id})
                    MERGE (curr)-[rel:NEXT_REVIEW_OF]->(next)
                    SET rel.student_id = $student_id,
                        rel.linked_at = $linked_at,
                        rel.same_concept = $same_concept,
                        rel.improvement_signal = $improvement_signal,
                        rel.severity_change = $severity_change
                    """,
                    review_id=review_id,
                    next_review_id=next_review["review_id"],
                    student_id=student_id,
                    linked_at=created_at,
                    same_concept=current_concept_value == (next_review["current_concept"] or ""),
                    improvement_signal=improvement_signal,
                    severity_change=severity_change,
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
                       coalesce(r.exercise_id, $exercise_id) AS stored_exercise_id,
                       coalesce(r.submission_id, '') AS submission_id,
                       coalesce(s.concept_mastery, 0.5) AS concept_mastery,
                       coalesce(s.implementation_consistency, 0.5) AS implementation_consistency,
                       coalesce(s.debugging_independence, 0.5) AS debugging_independence,
                       coalesce(s.efficiency_awareness, 0.5) AS efficiency_awareness,
                       coalesce(s.concept_transfer, 0.5) AS concept_transfer,
                       coalesce(s.learning_velocity, 0.5) AS learning_velocity,
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

            latest_review_transition = session.run(
                """
                MATCH (prev:Review)-[rel:NEXT_REVIEW_OF]->(curr:Review {review_id: $review_id})
                RETURN coalesce(rel.improvement_signal, 0.0) AS improvement_signal,
                       coalesce(rel.severity_change, 0.0) AS severity_change
                ORDER BY coalesce(rel.linked_at, '') DESC
                LIMIT 1
                """,
                review_id=review.review_id,
            ).single()

            latest_submission_transition = None
            if latest_record["submission_id"]:
                latest_submission_transition = session.run(
                    """
                    MATCH (prev:Submission)-[rel:NEXT_ATTEMPT]->(curr:Submission {submission_id: $submission_id})
                    RETURN coalesce(rel.improvement_ratio, 0.0) AS improvement_ratio,
                           coalesce(rel.regression_ratio, 0.0) AS regression_ratio
                    ORDER BY coalesce(rel.linked_at, '') DESC
                    LIMIT 1
                    """,
                    submission_id=latest_record["submission_id"],
                ).single()

            return {
                "current_concept": current_concept,
                "current_concept_weight": float(
                    latest_record["current_concept_weight"] or 1.0
                ),
                "review": review,
                "review_history": review_history,
                "student_profile": student_profile,
                "mastered_concepts": latest_record["mastered_concepts"] or [],
                "attempted_exercise_ids": latest_record["attempted_exercise_ids"] or [],
                "latest_review_improvement_signal": float(
                    latest_review_transition["improvement_signal"]
                    if latest_review_transition is not None
                    else 0.0
                ),
                "latest_review_severity_change": float(
                    latest_review_transition["severity_change"]
                    if latest_review_transition is not None
                    else 0.0
                ),
                "latest_submission_improvement_ratio": float(
                    latest_submission_transition["improvement_ratio"]
                    if latest_submission_transition is not None
                    else 0.0
                ),
                "latest_submission_regression_ratio": float(
                    latest_submission_transition["regression_ratio"]
                    if latest_submission_transition is not None
                    else 0.0
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

    def get_next_concepts(self, concept_id: str) -> list[ConceptRecord]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (:Concept {concept_id: $concept_id})-[:PREREQUISITE_OF]->(next:Concept)
                RETURN next.concept_id AS concept_id,
                       coalesce(next.slug, next.concept_id) AS slug,
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
                    slug=record["slug"],
                    name=record["name"] or record["concept_id"],
                    description=record["description"],
                    difficulty=record["difficulty"],
                )
                for record in result
            ]

    def get_next_concept_candidates(
        self,
        *,
        current_concept: str,
        attempted_exercise_ids: list[str],
        mastered_concepts: list[str],
        limit: int = 5,
    ) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (:Concept {concept_id: $current_concept})-[pre:PREREQUISITE_OF]->(target:Concept)
                WHERE NOT target.concept_id IN $mastered_concepts
                OPTIONAL MATCH (e:Exercise)-[tests:TESTS]->(target)
                OPTIONAL MATCH (e)-[path_rel:RECOMMENDED_FOR {path: 'NEXT_CONCEPT'}]->(target)
                WHERE e IS NULL OR NOT e.exercise_id IN $attempted_exercise_ids
                WITH target, pre, e, tests, path_rel
                RETURN target.concept_id AS concept_id,
                       coalesce(target.name, target.concept_id) AS name,
                       coalesce(target.description, '') AS description,
                       coalesce(target.difficulty, 1) AS difficulty,
                       coalesce(pre.strength, 1.0) AS prerequisite_strength,
                       coalesce(max(path_rel.weight), 0.0) AS best_path_weight,
                       coalesce(max(tests.weight), 0.0) AS best_tests_weight
                ORDER BY prerequisite_strength DESC, best_path_weight DESC, best_tests_weight DESC, difficulty ASC
                LIMIT $limit
                """,
                current_concept=current_concept,
                attempted_exercise_ids=attempted_exercise_ids,
                mastered_concepts=mastered_concepts,
                limit=limit,
            )
            return [
                {
                    "concept_id": record["concept_id"],
                    "name": record["name"],
                    "description": record["description"],
                    "difficulty": record["difficulty"],
                    "prerequisite_strength": float(record["prerequisite_strength"] or 0.0),
                    "best_path_weight": float(record["best_path_weight"] or 0.0),
                    "best_tests_weight": float(record["best_tests_weight"] or 0.0),
                }
                for record in result
            ]

    def retrieve_candidates(
        self,
        *,
        student_id: str,
        current_exercise_id: str,
        current_concept: str,
        target_concept: str,
        assigned_path: AssignedPath,
        attempted_exercise_ids: list[str],
        limit: int = 5,
    ) -> list[dict]:
        query = self._candidate_query(assigned_path)
        params = {
            "student_id": student_id,
            "current_exercise_id": current_exercise_id,
            "current_concept": current_concept,
            "target_concept": target_concept,
            "assigned_path": assigned_path,
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
                        "path_weight": float(record["path_weight"] or 0.0),
                        "tests_weight": float(record["tests_weight"] or 0.0),
                        "related_weight": float(record["related_weight"] or 0.0),
                        "relation_type": record["relation_type"] or "",
                        "difficulty_gap": float(record["difficulty_gap"] or 0.0),
                        "progression_score": float(record["progression_score"] or 0.0),
                        "similarity_score": float(record["similarity_score"] or 0.0),
                        "exercise": ExerciseRecord(
                            exercise_id=record["exercise_id"],
                            slug=record["slug"] or "",
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
                    slug=record["slug"] or record["concept_id"],
                    name=record["name"] or record["concept_id"],
                    description=record["description"],
                    difficulty=record["difficulty"],
                )
                for record in session.run(
                    """
                    MATCH (c:Concept)
                    RETURN c.concept_id AS concept_id,
                           coalesce(c.slug, c.concept_id) AS slug,
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
                    strength=record["strength"],
                )
                for record in session.run(
                    """
                    MATCH (p:Concept)-[r:PREREQUISITE_OF]->(c:Concept)
                    RETURN p.concept_id AS prerequisite_id,
                           c.concept_id AS concept_id,
                           coalesce(r.strength, 1.0) AS strength
                    """
                )
            ]
            exercises = [
                ExerciseRecord(
                    exercise_id=record["exercise_id"],
                    slug=record["slug"] or "",
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
                           coalesce(e.slug, '') AS slug,
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
                    concept_id=record["concept_id"],
                    path=record["path"],
                    weight=record["weight"],
                )
                for record in session.run(
                    """
                    MATCH (e:Exercise)-[r:RECOMMENDED_FOR]->(c:Concept)
                    RETURN e.exercise_id AS exercise_id,
                           c.concept_id AS concept_id,
                           r.path AS path,
                           coalesce(r.weight, 1.0) AS weight
                    """
                )
            ]
            exercise_relations = [
                ExerciseRelation(
                    exercise_id=record["exercise_id"],
                    related_exercise_id=record["related_exercise_id"],
                    weight=record["weight"],
                    relation_type=record["relation_type"],
                    target_concept_id=record["target_concept_id"],
                    shared_concept_ids=record["shared_concept_ids"] or [],
                    difficulty_gap=record["difficulty_gap"],
                    progression_score=record["progression_score"],
                    similarity_score=record["similarity_score"],
                )
                for record in session.run(
                    """
                    MATCH (e:Exercise)-[r:RELATED_TO]->(related:Exercise)
                    RETURN e.exercise_id AS exercise_id,
                           related.exercise_id AS related_exercise_id,
                           coalesce(r.weight, 1.0) AS weight,
                           coalesce(r.relation_type, '') AS relation_type,
                           coalesce(r.target_concept_id, '') AS target_concept_id,
                           coalesce(r.shared_concept_ids, []) AS shared_concept_ids,
                           coalesce(r.difficulty_gap, 0.0) AS difficulty_gap,
                           coalesce(r.progression_score, 0.0) AS progression_score,
                           coalesce(r.similarity_score, 0.0) AS similarity_score
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
            submissions = [
                SubmissionRecord(
                    submission_id=record["submission_id"],
                    student_id=record["student_id"],
                    exercise_id=record["exercise_id"],
                    code=record["code"],
                    testcase_outputs=json.loads(
                        record["testcase_outputs_json"] or "[]"
                    ),
                    created_at=record["created_at"],
                )
                for record in session.run(
                    """
                    MATCH (s:Student)-[:SUBMITTED]->(sub:Submission)
                    OPTIONAL MATCH (sub)-[:FOR_EXERCISE]->(e:Exercise)
                    RETURN sub.submission_id AS submission_id,
                           s.student_id AS student_id,
                           coalesce(e.exercise_id, coalesce(sub.exercise_id, '')) AS exercise_id,
                           coalesce(sub.code, '') AS code,
                           coalesce(sub.testcase_outputs_json, '[]') AS testcase_outputs_json,
                           coalesce(sub.created_at, '') AS created_at
                    ORDER BY sub.created_at DESC, sub.submission_id ASC
                    """
                )
            ]
            submission_relations = [
                SubmissionRelation(
                    previous_submission_id=record["previous_submission_id"],
                    next_submission_id=record["next_submission_id"],
                    student_id=record["student_id"],
                    linked_at=record["linked_at"],
                    same_exercise=record["same_exercise"],
                    improvement_ratio=record["improvement_ratio"],
                    regression_ratio=record["regression_ratio"],
                )
                for record in session.run(
                    """
                    MATCH (prev:Submission)-[r:NEXT_ATTEMPT]->(curr:Submission)
                    RETURN prev.submission_id AS previous_submission_id,
                           curr.submission_id AS next_submission_id,
                           coalesce(r.student_id, '') AS student_id,
                           coalesce(r.linked_at, '') AS linked_at,
                           coalesce(r.same_exercise, true) AS same_exercise,
                           coalesce(r.improvement_ratio, 0.0) AS improvement_ratio,
                           coalesce(r.regression_ratio, 0.0) AS regression_ratio
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
            review_relations = [
                ReviewRelation(
                    previous_review_id=record["previous_review_id"],
                    next_review_id=record["next_review_id"],
                    student_id=record["student_id"],
                    linked_at=record["linked_at"],
                    same_concept=record["same_concept"],
                    improvement_signal=record["improvement_signal"],
                    severity_change=record["severity_change"],
                )
                for record in session.run(
                    """
                    MATCH (prev:Review)-[r:NEXT_REVIEW_OF]->(next:Review)
                    RETURN prev.review_id AS previous_review_id,
                           next.review_id AS next_review_id,
                           coalesce(r.student_id, '') AS student_id,
                           coalesce(r.linked_at, '') AS linked_at,
                           coalesce(r.same_concept, false) AS same_concept,
                           coalesce(r.improvement_signal, 0.0) AS improvement_signal,
                           coalesce(r.severity_change, 0.0) AS severity_change
                    """
                )
            ]

        return KnowledgeGraphDocument(
            concepts=concepts,
            concept_relations=relations,
            exercises=exercises,
            exercise_concept_links=exercise_concept_links,
            exercise_path_links=exercise_path_links,
            exercise_relations=exercise_relations,
            students=students,
            submissions=submissions,
            submission_relations=submission_relations,
            reviews=reviews,
            review_relations=review_relations,
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
                MATCH (:Concept {concept_id: $current_concept})-[pre:PREREQUISITE_OF]->(target:Concept {concept_id: $target_concept})
                MATCH (e:Exercise)-[tests:TESTS]->(target)
                MATCH (e)-[path_rel:RECOMMENDED_FOR {path: $assigned_path}]->(target)
                OPTIONAL MATCH (current:Exercise {exercise_id: $current_exercise_id})-[related:RELATED_TO]->(e)
                WHERE NOT e.exercise_id IN $attempted_exercise_ids
                  AND NOT EXISTS {
                    MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
                  }
                RETURN target.concept_id AS target_concept,
                       target.name AS concept_name,
                       coalesce(target.description, '') AS concept_description,
                       coalesce(path_rel.weight, 0.0) AS path_weight,
                       coalesce(tests.weight, 0.0) AS tests_weight,
                       coalesce(related.weight, 0.0) AS related_weight,
                       coalesce(related.relation_type, '') AS relation_type,
                       coalesce(related.difficulty_gap, 0.0) AS difficulty_gap,
                       coalesce(related.progression_score, coalesce(pre.strength, 0.0)) AS progression_score,
                       coalesce(related.similarity_score, 0.0) AS similarity_score,
                       e.exercise_id AS exercise_id,
                       e.title AS title,
                       coalesce(e.description, '') AS description,
                       coalesce(e.content, '') AS content,
                       e.difficulty AS difficulty,
                       coalesce(e.tags, []) AS tags
                ORDER BY path_weight DESC, tests_weight DESC, progression_score DESC, related_weight DESC, e.title ASC
                LIMIT $limit
            """

        return """
            MATCH (target:Concept {concept_id: $target_concept})
            MATCH (e:Exercise)-[tests:TESTS]->(target)
            MATCH (e)-[path_rel:RECOMMENDED_FOR {path: $assigned_path}]->(target)
            OPTIONAL MATCH (current:Exercise {exercise_id: $current_exercise_id})-[related:RELATED_TO]->(e)
            WHERE NOT e.exercise_id IN $attempted_exercise_ids
              AND NOT EXISTS {
                MATCH (:Student {student_id: $student_id})-[:ATTEMPTED|ASSIGNED]->(e)
              }
            RETURN target.concept_id AS target_concept,
                   target.name AS concept_name,
                   coalesce(target.description, '') AS concept_description,
                   coalesce(path_rel.weight, 0.0) AS path_weight,
                   coalesce(tests.weight, 0.0) AS tests_weight,
                   coalesce(related.weight, 0.0) AS related_weight,
                   coalesce(related.relation_type, '') AS relation_type,
                   coalesce(related.difficulty_gap, 0.0) AS difficulty_gap,
                   coalesce(related.progression_score, 0.0) AS progression_score,
                   coalesce(related.similarity_score, 0.0) AS similarity_score,
                   e.exercise_id AS exercise_id,
                   e.title AS title,
                   coalesce(e.description, '') AS description,
                   coalesce(e.content, '') AS content,
                   e.difficulty AS difficulty,
                   coalesce(e.tags, []) AS tags
            ORDER BY path_weight DESC, tests_weight DESC, related_weight DESC, progression_score DESC, e.title ASC
            LIMIT $limit
        """

    @staticmethod
    def _derive_profile_from_scorecard(scorecard: dict) -> StudentProfileScoring:
        def score(name: str) -> float:
            raw_score = float(scorecard.get(name, {}).get("score", 3))
            return max(0.0, min(1.0, (raw_score - 1.0) / 4.0))

        def average(*values: float) -> float:
            return round(max(0.0, min(1.0, sum(values) / len(values))), 4)

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

        def blended(field_name: str, incoming: float) -> float:
            existing_value = getattr(existing, "get", None)
            previous = existing.get(field_name) if callable(existing_value) else None
            if previous is None:
                return incoming
            return round(max(0.0, min(1.0, previous * 0.4 + incoming * 0.6)), 4)

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
