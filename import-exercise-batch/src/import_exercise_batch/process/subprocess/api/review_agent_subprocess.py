from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from import_exercise_batch.config import TagConfig
from import_exercise_batch.model import LeetCodeProblemChange
from import_exercise_batch.process.subprocess.base import BaseSubProcess
from reviewagent_client import (
    ApiClient,
    Configuration,
    PatchConceptRelationsRequest,
    PatchExerciseRelationsRequest,
    UpsertConceptRequest,
    UpsertExerciseRequest,
)
from reviewagent_client.api.default_api import DefaultApi


class ReviewAgentSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, max_workers: int) -> None:
        self.base_url = base_url
        self.max_workers = max_workers

    def import_exercises(self, exercises: Iterable[LeetCodeProblemChange]) -> None:
        exercise_list = list(exercises)
        if not self.base_url:
            self.logger.warning(
                "Skipping review agent knowledge graph import because REVIEW_AGENT_API_BASE_URL is empty"
            )
            return
        self.logger.info(
            "Starting review agent knowledge graph import for %s exercises",
            len(exercise_list),
        )
        self._run_exercises_concurrently(
            exercises=exercise_list,
            action=self.put_exercise,
            action_name="exercise import",
        )
        self.logger.info(
            "Completed review agent knowledge graph import for %s exercises",
            len(exercise_list),
        )

    def import_topics(self, topics: Iterable[TagConfig]) -> None:
        topic_list = list(topics)
        if not self.base_url:
            self.logger.warning(
                "Skipping review agent topic import because REVIEW_AGENT_API_BASE_URL is empty"
            )
            return
        self.logger.info(
            "Starting review agent concept import for %s topics",
            len(topic_list),
        )
        self._run_topics_concurrently(
            topics=topic_list,
            action=self.put_concept,
            action_name="concept import",
        )
        self.logger.info(
            "Completed review agent concept import for %s topics",
            len(topic_list),
        )

    def patch_topic_relations(self, topics: Iterable[TagConfig]) -> None:
        topic_list = list(topics)
        if not self.base_url:
            self.logger.warning(
                "Skipping review agent concept relation patch because REVIEW_AGENT_API_BASE_URL is empty"
            )
            return
        patched_count = 0
        for topic in topic_list:
            if not topic.prerequisite_slugs:
                self.logger.info(
                    "Skipping concept relation patch for concept_slug=%s because no prerequisites were found",
                    topic.slug,
                )
                continue
            patched_count += 1
        topics_to_patch = [topic for topic in topic_list if topic.prerequisite_slugs]
        self._run_topics_concurrently(
            topics=topics_to_patch,
            action=self.patch_concept_relations,
            action_name="concept relation patch",
        )
        self.logger.info(
            "Completed review agent concept relation patch for %s topics",
            patched_count,
        )

    def _run_topics_concurrently(
        self,
        topics: list[TagConfig],
        action: Callable[[TagConfig], None],
        action_name: str,
    ) -> None:
        if not topics:
            return

        worker_count = min(self.max_workers, len(topics))
        self.logger.info(
            "Running review agent %s with %s workers for %s topics",
            action_name,
            worker_count,
            len(topics),
        )
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(action, topic): topic.slug
                for topic in topics
            }
            for future in as_completed(futures):
                topic_slug = futures[future]
                try:
                    future.result()
                except Exception:
                    self.logger.exception(
                        "Review agent %s failed for concept_slug=%s",
                        action_name,
                        topic_slug,
                    )
                    raise

    def patch_exercise_relations_batch(
        self,
        exercises: Iterable[LeetCodeProblemChange],
    ) -> int:
        exercise_list = list(exercises)
        if not self.base_url:
            self.logger.warning(
                "Skipping review agent relation patch because REVIEW_AGENT_API_BASE_URL is empty"
            )
            return 0

        patch_inputs: list[tuple[LeetCodeProblemChange, list[str]]] = []
        for exercise in exercise_list:
            related_exercise_slugs = exercise.added_similar_question_slugs()
            self.logger.info(
                "Built review agent relation patch for slug=%s added_similar=%s",
                exercise.question_slug,
                len(related_exercise_slugs),
            )
            if not related_exercise_slugs:
                continue
            patch_inputs.append((exercise, related_exercise_slugs))

        self._run_exercise_relation_patches_concurrently(patch_inputs)
        self.logger.info(
            "Patched review agent relations for %s exercises",
            len(patch_inputs),
        )
        return len(patch_inputs)

    def _run_exercises_concurrently(
        self,
        exercises: list[LeetCodeProblemChange],
        action: Callable[[LeetCodeProblemChange], None],
        action_name: str,
    ) -> None:
        if not exercises:
            return

        worker_count = min(self.max_workers, len(exercises))
        self.logger.info(
            "Running review agent %s with %s workers for %s exercises",
            action_name,
            worker_count,
            len(exercises),
        )
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(action, exercise): exercise
                for exercise in exercises
            }
            for future in as_completed(futures):
                exercise = futures[future]
                try:
                    future.result()
                except Exception:
                    self.logger.exception(
                        "Review agent %s failed for slug=%s exercise_id=%s",
                        action_name,
                        exercise.question_slug,
                        exercise.exercise_id,
                    )
                    raise

    def _run_exercise_relation_patches_concurrently(
        self,
        patch_inputs: list[tuple[LeetCodeProblemChange, list[str]]],
    ) -> None:
        if not patch_inputs:
            return

        worker_count = min(self.max_workers, len(patch_inputs))
        self.logger.info(
            "Running review agent exercise relation patch with %s workers for %s exercises",
            worker_count,
            len(patch_inputs),
        )
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    self.patch_exercise_relations,
                    exercise,
                    related_exercise_slugs,
                ): exercise
                for exercise, related_exercise_slugs in patch_inputs
            }
            for future in as_completed(futures):
                exercise = futures[future]
                try:
                    future.result()
                except Exception:
                    self.logger.exception(
                        "Review agent exercise relation patch failed for slug=%s exercise_id=%s",
                        exercise.question_slug,
                        exercise.exercise_id,
                    )
                    raise

    def put_concept(self, topic: TagConfig) -> None:
        configuration = Configuration(host=self.base_url)
        request = UpsertConceptRequest(
            name=topic.name,
            description="",
            difficulty=1,
        )
        self.logger.info(
            "Calling review agent concept API for concept_slug=%s base_url=%s",
            topic.slug,
            self.base_url,
        )
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put(
                concept_slug=topic.slug,
                upsert_concept_request=request,
            )
        self.logger.info(
            "Review agent concept API call completed for concept_slug=%s",
            topic.slug,
        )

    def patch_concept_relations(self, topic: TagConfig) -> None:
        request = PatchConceptRelationsRequest(
            prerequisite_slugs=topic.prerequisite_slugs or None,
        )
        configuration = Configuration(host=self.base_url)
        self.logger.info(
            "Calling review agent concept relation API for concept_slug=%s prerequisite_count=%s",
            topic.slug,
            len(topic.prerequisite_slugs),
        )
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch(
                concept_slug=topic.slug,
                patch_concept_relations_request=request,
            )
        self.logger.info(
            "Review agent concept relation API call completed for concept_slug=%s",
            topic.slug,
        )

    def patch_exercise_relations(
        self,
        exercise: LeetCodeProblemChange,
        related_exercise_slugs: list[str] | None,
    ) -> None:
        if exercise.exercise_id is None:
            raise ValueError(
                "exercise_id is required to patch review agent exercise relations"
            )
        if not self.base_url:
            self.logger.warning(
                "Skipping review agent relation patch because REVIEW_AGENT_API_BASE_URL is empty"
            )
            return
        if not related_exercise_slugs:
            self.logger.info(
                "Skipping review agent relation patch for slug=%s because no added relations were found",
                exercise.question_slug,
            )
            return

        request = PatchExerciseRelationsRequest(
            related_exercise_slugs=related_exercise_slugs,
        )
        configuration = Configuration(host=self.base_url)
        self.logger.info(
            "Calling review agent relation patch for slug=%s exercise_id=%s related_slug_count=%s",
            exercise.question_slug,
            exercise.exercise_id,
            len(related_exercise_slugs),
        )
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch(
                exercise_id=exercise.exercise_id,
                patch_exercise_relations_request=request,
            )
        self.logger.info(
            "Review agent relation patch completed for slug=%s exercise_id=%s",
            exercise.question_slug,
            exercise.exercise_id,
        )

    def put_exercise(self, exercise: LeetCodeProblemChange) -> None:
        if exercise.exercise_id is None:
            raise ValueError(
                "exercise_id is required to call review agent put exercise"
            )

        configuration = Configuration(host=self.base_url)
        request = UpsertExerciseRequest(
            slug=exercise.question_slug,
            title=exercise.title,
            description=exercise.content,
            content=exercise.content,
            difficulty=exercise.difficulty,
            tags=exercise.topic_tag_slugs,
        )

        self.logger.info(
            "Calling review agent API for slug=%s exercise_id=%s base_url=%s",
            exercise.question_slug,
            exercise.exercise_id,
            self.base_url,
        )
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put(
                exercise_id=exercise.exercise_id,
                upsert_exercise_request=request,
            )
        self.logger.info(
            "Review agent API call completed for slug=%s exercise_id=%s",
            exercise.question_slug,
            exercise.exercise_id,
        )
