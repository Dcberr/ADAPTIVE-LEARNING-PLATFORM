from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

import psycopg
from psycopg.rows import dict_row

from import_exercise_batch.model import ExerciseImportRecord
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class ExerciseDatabaseSubProcess(BaseSubProcess):
    tmp_table_name = "tmp_import_exercises"
    latest_table_name = "latest_import_exercises"
    tmp_table_schema_sql = """
    CREATE TABLE tmp_import_exercises (
        question_slug TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        topic_tag_slugs TEXT NOT NULL,
        similar_question_slugs TEXT NOT NULL
    );
    """
    latest_table_schema_sql = """
    CREATE TABLE latest_import_exercises (
        exercise_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        question_slug TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        topic_tag_slugs TEXT NOT NULL,
        similar_question_slugs TEXT NOT NULL
    );
    """

    def __init__(self, postgres_dsn: str) -> None:
        self.postgres_dsn = postgres_dsn

    @contextmanager
    def get_connection(self) -> Iterator[psycopg.Connection[Any]]:
        connection = psycopg.connect(self.postgres_dsn, row_factory=dict_row)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def truncate_tmp_import_exercises(self, connection: psycopg.Connection[Any]) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {self.tmp_table_name}")

    def insert_tmp_import_exercises(
        self, connection: psycopg.Connection[Any], exercises: Iterable[ExerciseImportRecord]
    ) -> None:
        with connection.cursor() as cursor:
            cursor.executemany(
                f"""
                INSERT INTO {self.tmp_table_name} (
                    question_slug,
                    title,
                    content,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                VALUES (
                    %(question_slug)s,
                    %(title)s,
                    %(content)s,
                    %(difficulty)s,
                    %(topic_tag_slugs)s,
                    %(similar_question_slugs)s
                )
                """,
                [exercise.to_record() for exercise in exercises],
            )

    def load_csv_to_tmp_import_exercises(
        self, connection: psycopg.Connection[Any], csv_path: Path
    ) -> None:
        with connection.cursor() as cursor:
            with cursor.copy(
                f"""
                COPY {self.tmp_table_name} (
                    question_slug,
                    title,
                    content,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
            ) as copy:
                with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
                    while chunk := csv_file.read(1024 * 1024):
                        copy.write(chunk)

    def get_changed_exercises(
        self, connection: psycopg.Connection[Any]
    ) -> list[ExerciseImportRecord]:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    tmp.question_slug,
                    tmp.title,
                    tmp.content,
                    tmp.difficulty,
                    tmp.topic_tag_slugs,
                    tmp.similar_question_slugs
                FROM {self.tmp_table_name} AS tmp
                LEFT JOIN {self.latest_table_name} AS latest
                    ON latest.question_slug = tmp.question_slug
                WHERE latest.question_slug IS NULL
                   OR latest.title != tmp.title
                   OR latest.content != tmp.content
                   OR latest.difficulty != tmp.difficulty
                   OR latest.topic_tag_slugs != tmp.topic_tag_slugs
                   OR latest.similar_question_slugs != tmp.similar_question_slugs
                ORDER BY tmp.title
                """
            )
            rows = cursor.fetchall()
        return [ExerciseImportRecord.from_row(row) for row in rows]

    def upsert_latest_exercises(
        self, connection: psycopg.Connection[Any], exercises: Iterable[ExerciseImportRecord]
    ) -> None:
        with connection.cursor() as cursor:
            cursor.executemany(
                f"""
                INSERT INTO {self.latest_table_name} (
                    question_slug,
                    title,
                    content,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                VALUES (
                    %(question_slug)s,
                    %(title)s,
                    %(content)s,
                    %(difficulty)s,
                    %(topic_tag_slugs)s,
                    %(similar_question_slugs)s
                )
                ON CONFLICT(question_slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    difficulty = EXCLUDED.difficulty,
                    topic_tag_slugs = EXCLUDED.topic_tag_slugs,
                    similar_question_slugs = EXCLUDED.similar_question_slugs
                """,
                [exercise.to_record() for exercise in exercises],
            )
