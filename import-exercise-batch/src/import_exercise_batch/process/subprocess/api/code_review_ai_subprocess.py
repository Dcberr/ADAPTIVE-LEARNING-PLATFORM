from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar

import urllib3
from import_exercise_batch.config import TagConfig
from import_exercise_batch.model import LeetCodeProblemChange
from import_exercise_batch.process.subprocess.base import BaseSubProcess
from code_review_ai_client import (
    ApiClient,
    BatchPatchExerciseRelationsItem,
    BatchPatchExerciseRelationsRequest,
    BatchUpsertExerciseItem,
    BatchUpsertExercisesRequest,
    Configuration,
    PatchConceptRelationsRequest,
    UpsertConceptRequest,
)
from code_review_ai_client.api.default_api import DefaultApi
from code_review_ai_client.exceptions import ApiException


class CodeReviewAiSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)
    _ChunkItem = TypeVar("_ChunkItem")

    def __init__(
        self,
        base_url: str,
        max_workers: int,
        max_retries: int,
        backoff_seconds: float,
        batch_upsert_chunk_size: int,
    ) -> None:
        self.base_url = base_url
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.batch_upsert_chunk_size = batch_upsert_chunk_size

    def import_exercises(self, exercises: Iterable[LeetCodeProblemChange]) -> None:
        exercise_list = list(exercises)
        if not self.base_url:
            self.logger.warning(
                "Skipping CodeReviewAI knowledge graph import because CODEREVIEWAI_API_BASE_URL is empty"
            )
            return
        self.logger.info(
            "Starting CodeReviewAI knowledge graph import for %s exercises",
            len(exercise_list),
        )
        configuration = Configuration(host=self.base_url)
        success_count = 0
        total_chunks = (
            len(exercise_list) + self.batch_upsert_chunk_size - 1
        ) // self.batch_upsert_chunk_size
        for chunk_index, chunk in enumerate(
            self._chunked(exercise_list, self.batch_upsert_chunk_size),
            start=1,
        ):
            chunk_start = (chunk_index - 1) * self.batch_upsert_chunk_size + 1
            chunk_end = chunk_start + len(chunk) - 1
            batch_request = BatchUpsertExercisesRequest(
                exercises=[
                    self._build_batch_upsert_exercise_item(exercise)
                    for exercise in chunk
                ]
            )
            self.logger.info(
                "Calling CodeReviewAI batch upsert API chunk=%s/%s records=%s range=%s-%s",
                chunk_index,
                total_chunks,
                len(chunk),
                chunk_start,
                chunk_end,
            )
            self._call_with_retry(
                action_name="batch upsert exercises",
                target_identifier=f"chunk={chunk_index}/{total_chunks}",
                call=lambda request=batch_request: self._call_batch_upsert_exercises(
                    configuration,
                    request,
                ),
            )
            success_count += len(chunk)
            self.logger.info(
                "CodeReviewAI batch upsert API chunk succeeded chunk=%s/%s success_records=%s success_total=%s/%s",
                chunk_index,
                total_chunks,
                len(chunk),
                success_count,
                len(exercise_list),
            )
        self.logger.info(
            "Completed CodeReviewAI knowledge graph import for %s exercises",
            len(exercise_list),
        )

    def import_topics(self, topics: Iterable[TagConfig]) -> None:
        topic_list = list(topics)
        if not self.base_url:
            self.logger.warning(
                "Skipping CodeReviewAI topic import because CODEREVIEWAI_API_BASE_URL is empty"
            )
            return
        self.logger.info(
            "Starting CodeReviewAI concept import for %s topics",
            len(topic_list),
        )
        self._run_topics_concurrently(
            topics=topic_list,
            action=self.put_concept,
            action_name="concept import",
        )
        self.logger.info(
            "Completed CodeReviewAI concept import for %s topics",
            len(topic_list),
        )

    def patch_topic_relations(self, topics: Iterable[TagConfig]) -> None:
        topic_list = list(topics)
        if not self.base_url:
            self.logger.warning(
                "Skipping CodeReviewAI concept relation patch because CODEREVIEWAI_API_BASE_URL is empty"
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
            "Completed CodeReviewAI concept relation patch for %s topics",
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
            "Running CodeReviewAI %s with %s workers for %s topics",
            action_name,
            worker_count,
            len(topics),
        )
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {executor.submit(action, topic): topic.slug for topic in topics}
            for future in as_completed(futures):
                topic_slug = futures[future]
                try:
                    future.result()
                except Exception:
                    self.logger.exception(
                        "CodeReviewAI %s failed for concept_slug=%s",
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
                "Skipping CodeReviewAI relation patch because CODEREVIEWAI_API_BASE_URL is empty"
            )
            return 0

        patch_inputs: list[tuple[LeetCodeProblemChange, list[str], list[str]]] = []
        for exercise in exercise_list:
            added_topic_tag_slugs = exercise.added_topic_tag_slugs()
            related_exercise_slugs = exercise.added_similar_question_slugs()
            self.logger.info(
                "Built CodeReviewAI relation patch for slug=%s added_topics=%s added_similar=%s",
                exercise.question_slug,
                len(added_topic_tag_slugs),
                len(related_exercise_slugs),
            )
            if not added_topic_tag_slugs and not related_exercise_slugs:
                continue
            patch_inputs.append(
                (exercise, added_topic_tag_slugs, related_exercise_slugs)
            )

        self._run_exercise_relation_patch_batches(patch_inputs)
        self.logger.info(
            "Patched CodeReviewAI relations for %s exercises",
            len(patch_inputs),
        )
        return len(patch_inputs)

    def _run_exercise_relation_patch_batches(
        self,
        patch_inputs: list[tuple[LeetCodeProblemChange, list[str], list[str]]],
    ) -> None:
        if not patch_inputs:
            return

        configuration = Configuration(host=self.base_url)
        total_chunks = (
            len(patch_inputs) + self.batch_upsert_chunk_size - 1
        ) // self.batch_upsert_chunk_size
        success_count = 0
        self.logger.info(
            "Running CodeReviewAI exercise relation batch patch with %s chunks for %s exercises",
            total_chunks,
            len(patch_inputs),
        )
        for chunk_index, chunk in enumerate(
            self._chunked(patch_inputs, self.batch_upsert_chunk_size),
            start=1,
        ):
            chunk_start = (chunk_index - 1) * self.batch_upsert_chunk_size + 1
            chunk_end = chunk_start + len(chunk) - 1
            batch_request = BatchPatchExerciseRelationsRequest(
                exercises=[
                    self._build_batch_patch_exercise_relations_item(
                        exercise,
                        added_topic_tag_slugs,
                        related_exercise_slugs,
                    )
                    for exercise, added_topic_tag_slugs, related_exercise_slugs in chunk
                ]
            )
            self.logger.info(
                "Calling CodeReviewAI batch relation patch API chunk=%s/%s records=%s range=%s-%s",
                chunk_index,
                total_chunks,
                len(chunk),
                chunk_start,
                chunk_end,
            )
            self._call_with_retry(
                action_name="batch patch exercise relations",
                target_identifier=f"chunk={chunk_index}/{total_chunks}",
                call=lambda request=batch_request: self._call_batch_patch_exercise_relations(
                    configuration,
                    request,
                ),
            )
            success_count += len(chunk)
            self.logger.info(
                "CodeReviewAI batch relation patch API chunk succeeded chunk=%s/%s success_records=%s success_total=%s/%s",
                chunk_index,
                total_chunks,
                len(chunk),
                success_count,
                len(patch_inputs),
            )

    def put_concept(self, topic: TagConfig) -> None:
        configuration = Configuration(host=self.base_url)
        request = UpsertConceptRequest(
            name=topic.name,
            description="",
            difficulty=1,
        )
        self.logger.info(
            "Calling CodeReviewAI concept API for concept_slug=%s base_url=%s",
            topic.slug,
            self.base_url,
        )
        self._call_with_retry(
            action_name="upsert concept",
            target_identifier=topic.slug,
            call=lambda: self._call_upsert_concept(configuration, topic, request),
        )
        self.logger.info(
            "CodeReviewAI concept API call completed for concept_slug=%s",
            topic.slug,
        )

    def patch_concept_relations(self, topic: TagConfig) -> None:
        request = PatchConceptRelationsRequest(
            prerequisite_slugs=topic.prerequisite_slugs or None,
        )
        configuration = Configuration(host=self.base_url)
        self.logger.info(
            "Calling CodeReviewAI concept relation API for concept_slug=%s prerequisite_count=%s",
            topic.slug,
            len(topic.prerequisite_slugs),
        )
        self._call_with_retry(
            action_name="patch concept relations",
            target_identifier=topic.slug,
            call=lambda: self._call_patch_concept_relations(
                configuration,
                topic,
                request,
            ),
        )
        self.logger.info(
            "CodeReviewAI concept relation API call completed for concept_slug=%s",
            topic.slug,
        )

    @staticmethod
    def _build_batch_patch_exercise_relations_item(
        exercise: LeetCodeProblemChange,
        added_topic_tag_slugs: list[str] | None,
        related_exercise_slugs: list[str] | None,
    ) -> BatchPatchExerciseRelationsItem:
        if exercise.exercise_id is None:
            raise ValueError(
                "exercise_id is required to patch CodeReviewAI exercise relations"
            )
        return BatchPatchExerciseRelationsItem(
            exercise_id=exercise.exercise_id,
            concept_slugs=added_topic_tag_slugs,
            related_exercise_slugs=related_exercise_slugs,
        )

    @staticmethod
    def _build_batch_upsert_exercise_item(
        exercise: LeetCodeProblemChange,
    ) -> BatchUpsertExerciseItem:
        if exercise.exercise_id is None:
            raise ValueError(
                "exercise_id is required to call CodeReviewAI put exercise"
            )
        return BatchUpsertExerciseItem(
            exercise_id=exercise.exercise_id,
            slug=exercise.question_slug,
            title=exercise.title,
            description=exercise.content,
            content=exercise.content,
            difficulty=exercise.difficulty,
            tags=exercise.topic_tag_slugs,
        )

    @staticmethod
    def _chunked(
        items: list[_ChunkItem],
        chunk_size: int,
    ) -> Iterable[list[_ChunkItem]]:
        for index in range(0, len(items), chunk_size):
            yield items[index : index + chunk_size]

    def _call_with_retry(
        self,
        action_name: str,
        target_identifier: str,
        call: Callable[[], None],
    ) -> None:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                call()
                if attempt > 1:
                    self.logger.info(
                        "CodeReviewAI %s succeeded on retry attempt=%s target=%s",
                        action_name,
                        attempt,
                        target_identifier,
                    )
                return
            except Exception as error:
                last_error = error
                should_retry = self._should_retry_error(error)
                self.logger.warning(
                    "CodeReviewAI %s failed on attempt=%s target=%s retry=%s error=%s",
                    action_name,
                    attempt,
                    target_identifier,
                    should_retry and attempt < self.max_retries,
                    error,
                )
                if not should_retry or attempt == self.max_retries:
                    raise
                time.sleep(self.backoff_seconds * attempt)

        if last_error is not None:
            raise last_error

    @staticmethod
    def _should_retry_error(error: Exception) -> bool:
        if isinstance(error, ApiException):
            status = error.status
            return status is None or status in {408, 429} or 500 <= status <= 599
        return isinstance(error, urllib3.exceptions.HTTPError | OSError | TimeoutError)

    @staticmethod
    def _call_upsert_concept(
        configuration: Configuration,
        topic: TagConfig,
        request: UpsertConceptRequest,
    ) -> None:
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put(
                concept_slug=topic.slug,
                upsert_concept_request=request,
            )

    @staticmethod
    def _call_patch_concept_relations(
        configuration: Configuration,
        topic: TagConfig,
        request: PatchConceptRelationsRequest,
    ) -> None:
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch(
                concept_slug=topic.slug,
                patch_concept_relations_request=request,
            )

    @staticmethod
    def _call_batch_patch_exercise_relations(
        configuration: Configuration,
        request: BatchPatchExerciseRelationsRequest,
    ) -> None:
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch(
                batch_patch_exercise_relations_request=request,
            )

    @staticmethod
    def _call_batch_upsert_exercises(
        configuration: Configuration,
        request: BatchUpsertExercisesRequest,
    ) -> None:
        with ApiClient(configuration) as api_client:
            api = DefaultApi(api_client)
            api.batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put(
                batch_upsert_exercises_request=request,
            )
