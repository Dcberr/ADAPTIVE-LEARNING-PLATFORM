from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from import_exercise_batch.model import ExerciseImportRecord
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class ExerciseCsvSubProcess(BaseSubProcess):
    fieldnames = [
        "question_slug",
        "title",
        "content",
        "difficulty",
        "topic_tag_slugs",
        "similar_question_slugs",
    ]

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def write(self, exercises: Iterable[ExerciseImportRecord]) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            for exercise in exercises:
                writer.writerow(
                    {
                        "question_slug": exercise.question_slug,
                        "title": exercise.title,
                        "content": exercise.content,
                        "difficulty": exercise.difficulty,
                        "topic_tag_slugs": json.dumps(
                            exercise.topic_tag_slugs, ensure_ascii=False
                        ),
                        "similar_question_slugs": json.dumps(
                            exercise.similar_question_slugs, ensure_ascii=False
                        ),
                    }
                )
        return self.output_path
