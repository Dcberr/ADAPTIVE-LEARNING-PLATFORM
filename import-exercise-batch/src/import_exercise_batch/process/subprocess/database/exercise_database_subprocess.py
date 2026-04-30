from __future__ import annotations

from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Any, Iterable, Iterator

import psycopg
from psycopg.rows import DictRow, dict_row

from import_exercise_batch.model import LeetCodeProblem, LeetCodeProblemChange
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class ExerciseDatabaseSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)

    tmp_table_name = "tmp_import_exercises"
    latest_table_name = "latest_import_exercises"
    tmp_table_schema_sql = """
    CREATE TABLE tmp_import_exercises (
        question_slug TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        sample_test_case TEXT NOT NULL,
        code_snippet TEXT NOT NULL,
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
        sample_test_case TEXT NOT NULL,
        code_snippet TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        topic_tag_slugs TEXT NOT NULL,
        similar_question_slugs TEXT NOT NULL
    );
    """

    def __init__(self, postgres_dsn: str) -> None:
        self.postgres_dsn = postgres_dsn

    @contextmanager
    def get_connection(self) -> Iterator[psycopg.Connection[DictRow]]:
        connection = psycopg.Connection[DictRow].connect(
            self.postgres_dsn,
            row_factory=dict_row,
        )
        try:
            yield connection
            connection.commit()
        except Exception:
            try:
                if not connection.closed:
                    connection.rollback()
            except psycopg.Error:
                self.logger.warning(
                    "Skipping rollback because the database connection is already lost",
                    exc_info=True,
                )
            raise
        finally:
            try:
                if not connection.closed:
                    connection.close()
            except psycopg.Error:
                self.logger.warning(
                    "Failed to close database connection cleanly",
                    exc_info=True,
                )

    def truncate_tmp_import_exercises(
        self, connection: psycopg.Connection[DictRow]
    ) -> None:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE tmp_import_exercises")
        self.logger.info("Truncated temporary table %s", self.tmp_table_name)

    def insert_tmp_import_exercises(
        self,
        connection: psycopg.Connection[DictRow],
        exercises: Iterable[LeetCodeProblem],
    ) -> None:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO tmp_import_exercises (
                    question_slug,
                    title,
                    content,
                    sample_test_case,
                    code_snippet,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                VALUES (
                    COALESCE(%(question_slug)s, ''),
                    COALESCE(%(title)s, ''),
                    COALESCE(%(content)s, ''),
                    COALESCE(%(sample_test_case)s, ''),
                    COALESCE(%(code_snippet)s, ''),
                    COALESCE(%(difficulty)s, ''),
                    COALESCE(%(topic_tag_slugs)s, '[]'),
                    COALESCE(%(similar_question_slugs)s, '[]')
                )
                """,
                [exercise.to_record() for exercise in exercises],
            )

    def load_csv_to_tmp_import_exercises(
        self, connection: psycopg.Connection[DictRow], csv_path: Path
    ) -> None:
        with connection.cursor() as cursor:
            with cursor.copy(
                """
                COPY tmp_import_exercises (
                    question_slug,
                    title,
                    content,
                    sample_test_case,
                    code_snippet,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                FROM STDIN WITH (
                    FORMAT CSV,
                    HEADER TRUE,
                    FORCE_NOT_NULL (
                        question_slug,
                        title,
                        content,
                        sample_test_case,
                        code_snippet,
                        difficulty,
                        topic_tag_slugs,
                        similar_question_slugs
                    )
                )
                """
            ) as copy:
                with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
                    while chunk := csv_file.read(1024 * 1024):
                        copy.write(chunk)
        self.logger.info(
            "Loaded CSV into temporary table %s from %s",
            self.tmp_table_name,
            csv_path,
        )

    def get_changed_exercises(
        self, connection: psycopg.Connection[DictRow]
    ) -> list[LeetCodeProblem]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH tmp_filtered AS (
                    SELECT
                        tmp.question_slug,
                        tmp.title,
                        tmp.content,
                        tmp.sample_test_case,
                        tmp.code_snippet,
                        tmp.difficulty,
                        tmp.topic_tag_slugs,
                        COALESCE(
                            (
                                SELECT COALESCE(
                                    jsonb_agg(slug)
                                    FILTER (
                                        WHERE EXISTS (
                                            SELECT 1
                                            FROM tmp_import_exercises AS existing
                                            WHERE existing.question_slug = slug
                                        )
                                    ),
                                    '[]'::jsonb
                                )
                                FROM jsonb_array_elements_text(
                                    tmp.similar_question_slugs::jsonb
                                ) AS similar(slug)
                            ),
                            '[]'::jsonb
                        )::text AS similar_question_slugs
                    FROM tmp_import_exercises AS tmp
                ),
                latest_filtered AS (
                    SELECT
                        latest.question_slug,
                        latest.title,
                        latest.content,
                        latest.sample_test_case,
                        latest.code_snippet,
                        latest.difficulty,
                        latest.topic_tag_slugs,
                        COALESCE(
                            (
                                SELECT COALESCE(
                                    jsonb_agg(slug)
                                    FILTER (
                                        WHERE EXISTS (
                                            SELECT 1
                                            FROM tmp_import_exercises AS existing
                                            WHERE existing.question_slug = slug
                                        )
                                    ),
                                    '[]'::jsonb
                                )
                                FROM jsonb_array_elements_text(
                                    latest.similar_question_slugs::jsonb
                                ) AS similar(slug)
                            ),
                            '[]'::jsonb
                        )::text AS similar_question_slugs
                    FROM latest_import_exercises AS latest
                )
                SELECT
                    tmp.question_slug,
                    tmp.title,
                    tmp.content,
                    tmp.sample_test_case,
                    tmp.code_snippet,
                    tmp.difficulty,
                    tmp.topic_tag_slugs,
                    tmp.similar_question_slugs
                FROM tmp_filtered AS tmp
                LEFT JOIN latest_filtered AS latest
                    ON latest.question_slug = tmp.question_slug
                WHERE latest.question_slug IS NULL
                   OR latest.title != tmp.title
                   OR latest.content != tmp.content
                   OR latest.sample_test_case != tmp.sample_test_case
                   OR latest.code_snippet != tmp.code_snippet
                   OR latest.difficulty != tmp.difficulty
                   OR latest.topic_tag_slugs != tmp.topic_tag_slugs
                   OR latest.similar_question_slugs != tmp.similar_question_slugs
                ORDER BY tmp.title
                """
            )
            rows = cursor.fetchall()
        return [LeetCodeProblem.from_row(row) for row in rows]

    def get_exercise_changes(
        self, connection: psycopg.Connection[DictRow]
    ) -> list[LeetCodeProblemChange]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH tmp_filtered AS (
                    SELECT
                        tmp.question_slug,
                        tmp.title,
                        tmp.content,
                        tmp.sample_test_case,
                        tmp.code_snippet,
                        tmp.difficulty,
                        tmp.topic_tag_slugs,
                        COALESCE(
                            (
                                SELECT COALESCE(
                                    jsonb_agg(sim.slug),
                                    '[]'::jsonb
                                )
                                FROM jsonb_array_elements_text(
                                    tmp.similar_question_slugs::jsonb
                                ) AS sim(slug)
                                WHERE EXISTS (
                                    SELECT 1
                                    FROM tmp_import_exercises AS existing
                                    WHERE existing.question_slug = sim.slug
                                )
                            ),
                            '[]'::jsonb
                        )::text AS similar_question_slugs
                    FROM tmp_import_exercises AS tmp
                ),
                latest_filtered AS (
                    SELECT
                        latest.exercise_id,
                        latest.question_slug,
                        latest.title,
                        latest.content,
                        latest.sample_test_case,
                        latest.code_snippet,
                        latest.difficulty,
                        latest.topic_tag_slugs,
                        COALESCE(
                            (
                                SELECT COALESCE(
                                    jsonb_agg(sim.slug),
                                    '[]'::jsonb
                                )
                                FROM jsonb_array_elements_text(
                                    latest.similar_question_slugs::jsonb
                                ) AS sim(slug)
                                WHERE EXISTS (
                                    SELECT 1
                                    FROM tmp_import_exercises AS existing
                                    WHERE existing.question_slug = sim.slug
                                )
                            ),
                            '[]'::jsonb
                        )::text AS similar_question_slugs
                    FROM latest_import_exercises AS latest
                )
                SELECT
                    latest.exercise_id,
                    tmp.question_slug,
                    tmp.title,
                    tmp.content,
                    tmp.sample_test_case,
                    tmp.code_snippet,
                    tmp.difficulty,
                    tmp.topic_tag_slugs,
                    tmp.similar_question_slugs,
                    COALESCE(latest.sample_test_case, '') AS latest_sample_test_case,
                    COALESCE(latest.code_snippet, '') AS latest_code_snippet,
                    COALESCE(latest.topic_tag_slugs, '[]') AS latest_topic_tag_slugs,
                    COALESCE(
                        latest.similar_question_slugs,
                        '[]'
                    ) AS latest_similar_question_slugs,
                    CASE
                        WHEN latest.question_slug IS NULL THEN 'create'
                        WHEN latest.title = tmp.title
                         AND latest.content = tmp.content
                         AND latest.sample_test_case = tmp.sample_test_case
                         AND latest.code_snippet = tmp.code_snippet
                         AND latest.difficulty = tmp.difficulty
                         AND latest.topic_tag_slugs = tmp.topic_tag_slugs
                         AND latest.similar_question_slugs = tmp.similar_question_slugs
                        THEN 'no_different'
                        ELSE 'update'
                    END AS diff_type,
                    (
                        latest.question_slug IS NOT NULL
                        AND (
                            latest.title != tmp.title
                            OR latest.content != tmp.content
                            OR latest.sample_test_case != tmp.sample_test_case
                            OR latest.code_snippet != tmp.code_snippet
                            OR latest.difficulty != tmp.difficulty
                        )
                    ) AS is_change_content,
                    (
                        latest.question_slug IS NOT NULL
                        AND latest.topic_tag_slugs != tmp.topic_tag_slugs
                    ) AS is_change_topic,
                    (
                        latest.question_slug IS NOT NULL
                        AND latest.similar_question_slugs != tmp.similar_question_slugs
                    ) AS is_change_similar_question
                FROM tmp_filtered AS tmp
                LEFT JOIN latest_filtered AS latest
                    ON latest.question_slug = tmp.question_slug
                ORDER BY tmp.title
                """
            )
            rows = cursor.fetchall()
        self.logger.info("Fetched %s exercise change rows from database", len(rows))
        return [LeetCodeProblemChange.from_row(row) for row in rows]

    def upsert_latest_exercises(
        self,
        connection: psycopg.Connection[DictRow],
        exercises: Iterable[LeetCodeProblemChange],
    ) -> None:
        records = [exercise.to_record() for exercise in exercises]
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO latest_import_exercises (
                    exercise_id,
                    question_slug,
                    title,
                    content,
                    sample_test_case,
                    code_snippet,
                    difficulty,
                    topic_tag_slugs,
                    similar_question_slugs
                )
                VALUES (
                    %(exercise_id)s,
                    %(question_slug)s,
                    %(title)s,
                    %(content)s,
                    %(sample_test_case)s,
                    %(code_snippet)s,
                    %(difficulty)s,
                    %(topic_tag_slugs)s,
                    %(similar_question_slugs)s
                )
                ON CONFLICT(question_slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    sample_test_case = EXCLUDED.sample_test_case,
                    code_snippet = EXCLUDED.code_snippet,
                    difficulty = EXCLUDED.difficulty,
                    topic_tag_slugs = EXCLUDED.topic_tag_slugs,
                    similar_question_slugs = EXCLUDED.similar_question_slugs
                """,
                records,
            )
        self.logger.info(
            "Upserted %s exercises into %s",
            len(records),
            self.latest_table_name,
        )
