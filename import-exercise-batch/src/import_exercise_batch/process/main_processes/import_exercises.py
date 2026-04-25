from __future__ import annotations

from import_exercise_batch.config import ImportExercisesSettings
from import_exercise_batch.process.main_processes.base import BaseMainProcess
from import_exercise_batch.process.subprocess.api import (
    CodeReviewSubProcess,
    ReviewAgentSubProcess,
)
from import_exercise_batch.process.subprocess.csv import ExerciseCsvSubProcess
from import_exercise_batch.process.subprocess.database import ExerciseDatabaseSubProcess
from import_exercise_batch.process.subprocess.leetcode import LeetCodeFetchSubProcess


class ImportExercisesMainProcess(BaseMainProcess):
    def __init__(self, settings: ImportExercisesSettings) -> None:
        self.settings = settings
        self.database_subprocess = ExerciseDatabaseSubProcess(settings.database.postgres_dsn)
        self.csv_subprocess = ExerciseCsvSubProcess(settings.database.import_csv_path)
        self.leetcode_subprocess = LeetCodeFetchSubProcess(settings.leetcode)
        self.code_review_subprocess = CodeReviewSubProcess(settings.code_review_api.base_url)
        self.review_agent_subprocess = ReviewAgentSubProcess(settings.review_agent_api.base_url)

    def run(self) -> None:
        with self.database_subprocess.get_connection() as connection:
            self.database_subprocess.truncate_tmp_import_exercises(connection)

            exercises = []
            for tag in self.settings.tags:
                if not tag.enable:
                    continue
                exercises.extend(
                    self.leetcode_subprocess.get_exercises_by_tag(
                        tag=tag.slug,
                        limit=self.leetcode_subprocess.resolve_limit(tag.limit),
                    )
                )

            csv_path = self.csv_subprocess.write(exercises)
            self.database_subprocess.load_csv_to_tmp_import_exercises(connection, csv_path)

            changed_exercises = self.database_subprocess.get_changed_exercises(connection)
            self.code_review_subprocess.import_exercise(changed_exercises)
            self.review_agent_subprocess.import_knowledge_graph_exercise(changed_exercises)
            self.database_subprocess.upsert_latest_exercises(connection, changed_exercises)
