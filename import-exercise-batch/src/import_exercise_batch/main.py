from __future__ import annotations

from import_exercise_batch.config import ImportExercisesSettings
from import_exercise_batch.process import ImportExercisesMainProcess


def main() -> None:
    ImportExercisesMainProcess(ImportExercisesSettings.from_env()).run()


if __name__ == "__main__":
    main()
