from __future__ import annotations

from import_exercise_batch.config import Settings
from import_exercise_batch.process.subprocess.database_subprocess import (
    DatabaseSubProcess,
)
from import_exercise_batch.process.subprocess.leetcode_subprocess import (
    LeetCodeFetchSubProcess,
)
from import_exercise_batch.process.subprocess.update_subprocess import (
    UpdateExerciseSubProcess,
)


class MainProcess:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database_subprocess = DatabaseSubProcess(settings.database_path)
        self.leetcode_subprocess = LeetCodeFetchSubProcess(settings)
        self.update_subprocess = UpdateExerciseSubProcess()

    def run(self) -> None:
        with self.database_subprocess.get_connection() as connection:
            self.database_subprocess.initialize_tables(connection)
            self.database_subprocess.truncate_tmp_import_exercises(connection)

            exercises = self.leetcode_subprocess.run()
            self.database_subprocess.insert_tmp_import_exercises(connection, exercises)

            changed_exercises = self.database_subprocess.get_changed_exercises(connection)
            self.update_subprocess.run(changed_exercises)
            self.database_subprocess.upsert_latest_exercises(connection, changed_exercises)

