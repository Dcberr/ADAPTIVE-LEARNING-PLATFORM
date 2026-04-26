from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import replace
from uuid import uuid4

from import_exercise_batch.model import LeetCodeProblemChange
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class CodeReviewSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def import_exercise(
        self,
        exercises: Iterable[LeetCodeProblemChange],
    ) -> list[LeetCodeProblemChange]:
        processed_exercises: list[LeetCodeProblemChange] = []
        processed_count = 0
        for exercise in exercises:
            if exercise.diff_type == "create":
                exercise = self._assign_temp_exercise_id(exercise)
                self.logger.info(
                    "Creating exercise slug=%s title=%s exercise_id=%s",
                    exercise.question_slug,
                    exercise.title,
                    exercise.exercise_id,
                )
                self.create_exercise(exercise)
            elif exercise.diff_type == "update":
                self.logger.info(
                    "Updating exercise slug=%s title=%s exercise_id=%s",
                    exercise.question_slug,
                    exercise.title,
                    exercise.exercise_id,
                )
                self.update_exercise(exercise)
            else:
                self.logger.info(
                    "Skipping unchanged exercise slug=%s title=%s",
                    exercise.question_slug,
                    exercise.title,
                )
                continue

            processed_exercises.append(exercise)
            processed_count += 1
            self.logger.info(
                "Code review API step completed for slug=%s diff_type=%s",
                exercise.question_slug,
                exercise.diff_type,
            )
        self.logger.info("Processed %s changed exercises for code review API", processed_count)
        return processed_exercises

    def create_exercise(self, exercise: LeetCodeProblemChange) -> None:
        """TODO: call code review API to create an exercise."""
        _ = self.base_url
        _ = exercise

    def update_exercise(self, exercise: LeetCodeProblemChange) -> None:
        """TODO: call code review API to update an exercise."""
        _ = self.base_url
        _ = exercise

    @staticmethod
    def _assign_temp_exercise_id(exercise: LeetCodeProblemChange) -> LeetCodeProblemChange:
        if exercise.exercise_id is not None:
            return exercise
        return replace(exercise, exercise_id=str(uuid4()))
