from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from import_exercise_batch.process.subprocess.database import (
    ExerciseDatabaseSubProcess,
)


class _FakeCursor:
    def __init__(self) -> None:
        self.executemany_calls: list[tuple[str, list[dict[str, str]]]] = []

    def __enter__(self) -> "_FakeCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def executemany(
        self,
        query: str,
        params_seq,
    ) -> None:
        self.executemany_calls.append((query, list(params_seq)))


class _FakeConnection:
    def __init__(self, cursor: _FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self) -> _FakeCursor:
        return self._cursor


class ExerciseDatabaseSubProcessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.subprocess = ExerciseDatabaseSubProcess(
            "postgresql://postgres:postgres@localhost:5432/import_exercises"
        )

    def _write_csv(self, rows: list[dict[str, str]]) -> Path:
        fieldnames = [
            "question_slug",
            "title",
            "content",
            "sample_test_case",
            "code_snippet",
            "difficulty",
            "topic_tag_slugs",
            "similar_question_slugs",
        ]
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        csv_path = Path(temp_dir.name) / "import_exercises.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return csv_path

    def test_iter_csv_records_normalizes_blank_values(self) -> None:
        csv_path = self._write_csv(
            [
                {
                    "question_slug": "two-sum",
                    "title": "Two Sum",
                    "content": "Problem content",
                    "sample_test_case": "",
                    "code_snippet": "class Solution {}",
                    "difficulty": "EASY",
                    "topic_tag_slugs": "",
                    "similar_question_slugs": "",
                }
            ]
        )

        records = list(self.subprocess._iter_csv_records(csv_path))

        self.assertEqual(
            [
                {
                    "question_slug": "two-sum",
                    "title": "Two Sum",
                    "content": "Problem content",
                    "sample_test_case": "",
                    "code_snippet": "class Solution {}",
                    "difficulty": "EASY",
                    "topic_tag_slugs": "[]",
                    "similar_question_slugs": "[]",
                }
            ],
            records,
        )

    def test_load_csv_to_tmp_import_exercises_uses_insert_records(self) -> None:
        csv_path = self._write_csv(
            [
                {
                    "question_slug": "two-sum",
                    "title": "Two Sum",
                    "content": "Problem content",
                    "sample_test_case": "1\\n2",
                    "code_snippet": "class Solution {}",
                    "difficulty": "EASY",
                    "topic_tag_slugs": "[\"array\"]",
                    "similar_question_slugs": "[]",
                }
            ]
        )
        fake_cursor = _FakeCursor()
        fake_connection = _FakeConnection(fake_cursor)

        self.subprocess.load_csv_to_tmp_import_exercises(fake_connection, csv_path)

        self.assertEqual(1, len(fake_cursor.executemany_calls))
        query, rows = fake_cursor.executemany_calls[0]
        self.assertIn("INSERT INTO tmp_import_exercises", query)
        self.assertEqual(
            [
                {
                    "question_slug": "two-sum",
                    "title": "Two Sum",
                    "content": "Problem content",
                    "sample_test_case": "1\\n2",
                    "code_snippet": "class Solution {}",
                    "difficulty": "EASY",
                    "topic_tag_slugs": "[\"array\"]",
                    "similar_question_slugs": "[]",
                }
            ],
            rows,
        )


if __name__ == "__main__":
    unittest.main()
