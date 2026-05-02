from __future__ import annotations

import logging
from collections.abc import Iterable

from import_exercise_batch.model import LeetCodeProblem, LeetCodeProblemChange
from import_exercise_batch.config import ImportExercisesSettings
from import_exercise_batch.process.mainprocess.base import BaseMainProcess
from import_exercise_batch.process.subprocess.api import (
    CodeReviewAiSubProcess,
    CodeReviewSubProcess,
)
from import_exercise_batch.process.subprocess.csv import ExerciseCsvSubProcess
from import_exercise_batch.process.subprocess.database import ExerciseDatabaseSubProcess
from import_exercise_batch.process.subprocess.leetcode import LeetCodeFetchSubProcess


class ImportExercisesMainProcess(BaseMainProcess):
    logger = logging.getLogger(__name__)

    def __init__(self, settings: ImportExercisesSettings) -> None:
        self.settings = settings
        self.database_subprocess = ExerciseDatabaseSubProcess(
            settings.database.postgres_dsn
        )
        self.csv_subprocess = ExerciseCsvSubProcess(settings.database.import_csv_path)
        self.leetcode_subprocess = LeetCodeFetchSubProcess(settings.leetcode)
        self.leetcode_subprocess.set_allowed_topic_tag_slugs(
            {tag.slug for tag in settings.tags}
        )
        self.code_review_subprocess = CodeReviewSubProcess(
            settings.code_review_api.base_url,
            settings.code_review_api.max_retries,
            settings.code_review_api.backoff_seconds,
            settings.code_review_api.batch_import_chunk_size,
        )
        self.code_review_ai_subprocess = CodeReviewAiSubProcess(
            settings.code_review_ai_api.base_url,
            settings.code_review_ai_api.max_workers,
            settings.code_review_ai_api.max_retries,
            settings.code_review_ai_api.backoff_seconds,
            settings.code_review_ai_api.put_exercise_chunk_size,
            settings.code_review_ai_api.patch_exercise_relations_chunk_size,
        )

    def run(self) -> None:
        self.logger.info("Starting import exercises batch")
        with self.database_subprocess.get_connection() as connection:
            self.database_subprocess.truncate_tmp_import_exercises(connection)

            exercises_by_slug = {}
            for tag in self.settings.tags:
                if not tag.enable:
                    continue
                resolved_limit = self.leetcode_subprocess.resolve_limit(tag.limit)
                fetched_exercises = self.leetcode_subprocess.get_exercises_by_tag(
                    tag=tag.slug,
                    limit=resolved_limit,
                )
                complete_exercises = self._filter_exercises_with_full_payload(
                    fetched_exercises,
                    tag_slug=tag.slug,
                )
                self.logger.info(
                    "Fetched %s complete exercises from LeetCode for tag=%s limit=%s",
                    len(complete_exercises),
                    tag.slug,
                    resolved_limit,
                )
                for exercise in complete_exercises:
                    exercises_by_slug.setdefault(exercise.question_slug, exercise)

            exercises = list(exercises_by_slug.values())

            self.logger.info("Fetched %s total exercises from LeetCode", len(exercises))

            csv_path = self.csv_subprocess.write(exercises)
            self.logger.info(
                "Wrote %s exercises to CSV at %s", len(exercises), csv_path
            )
            self.database_subprocess.load_csv_to_tmp_import_exercises(
                connection, csv_path
            )
            exercise_changes = self.database_subprocess.get_exercise_changes(connection)
            create_count = sum(
                1
                for exercise_change in exercise_changes
                if exercise_change.diff_type == "create"
            )
            update_count = sum(
                1
                for exercise_change in exercise_changes
                if exercise_change.diff_type == "update"
            )
            no_diff_count = sum(
                1
                for exercise_change in exercise_changes
                if exercise_change.diff_type == "no_different"
            )
            self.logger.info(
                "Detected %s exercise changes: create=%s update=%s unchanged=%s",
                len(exercise_changes),
                create_count,
                update_count,
                no_diff_count,
            )
            synced_exercises = self.code_review_subprocess.import_exercise(
                exercise_changes,
                sync_unchanged=True,
            )
            changed_exercises = [
                exercise
                for exercise in synced_exercises
                if exercise.diff_type != "no_different"
            ]
            self.code_review_ai_subprocess.import_exercises(changed_exercises)
            self.patch_code_review_ai_relations(changed_exercises)
            self.database_subprocess.upsert_latest_exercises(
                connection, changed_exercises
            )
            self.logger.info(
                "Finished import exercises batch with %s changed exercises persisted",
                len(changed_exercises),
            )

    def patch_code_review_ai_relations(
        self,
        exercises: Iterable[LeetCodeProblemChange],
    ) -> None:
        self.code_review_ai_subprocess.patch_exercise_relations_batch(exercises)

    def _filter_exercises_with_full_payload(
        self,
        exercises: Iterable[LeetCodeProblem],
        *,
        tag_slug: str,
    ) -> list[LeetCodeProblem]:
        complete_exercises: list[LeetCodeProblem] = []
        skipped_slugs: list[str] = []
        for exercise in exercises:
            if exercise.has_full_payload():
                complete_exercises.append(exercise)
                continue
            skipped_slugs.append(exercise.question_slug)

        if skipped_slugs:
            self.logger.warning(
                "Skipping %s LeetCode exercises without full payload for tag=%s slugs=%s",
                len(skipped_slugs),
                tag_slug,
                ", ".join(skipped_slugs),
            )

        return complete_exercises
