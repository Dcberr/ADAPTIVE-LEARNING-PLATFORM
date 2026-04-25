from __future__ import annotations

from collections.abc import Iterable

from import_exercise_batch.model import ExerciseImportRecord
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class CodeReviewSubProcess(BaseSubProcess):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def import_exercise(self, exercises: Iterable[ExerciseImportRecord]) -> None:
        """TODO: implement code review API batch flow."""
        _ = self.base_url
        _ = exercises
