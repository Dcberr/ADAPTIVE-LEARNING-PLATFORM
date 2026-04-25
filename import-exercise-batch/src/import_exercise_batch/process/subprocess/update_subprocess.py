from __future__ import annotations

from collections.abc import Iterable

from import_exercise_batch.model import Exercise
from import_exercise_batch.process.subprocess.base_subprocess import BaseSubProcess


class UpdateExerciseSubProcess(BaseSubProcess):
    def run(self, exercises: Iterable[Exercise]) -> None:
        for exercise in exercises:
            self.update_exercise(exercise)

    def update_exercise(self, exercise: Exercise) -> None:
        """TODO: call downstream API to update exercise data."""
        _ = exercise

