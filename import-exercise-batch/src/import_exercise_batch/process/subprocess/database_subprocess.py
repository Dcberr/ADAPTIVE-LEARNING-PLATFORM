from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from import_exercise_batch.model import Exercise
from import_exercise_batch.process.subprocess.base_subprocess import BaseSubProcess


class DatabaseSubProcess(BaseSubProcess):
    tmp_table_name = "tmp_import_exercises"
    latest_table_name = "latest_import_exercises"

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_tables(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.tmp_table_name} (
                title TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL
            )
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.latest_table_name} (
                title TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL
            )
            """
        )

    def truncate_tmp_import_exercises(self, connection: sqlite3.Connection) -> None:
        connection.execute(f"DELETE FROM {self.tmp_table_name}")

    def insert_tmp_import_exercises(
        self, connection: sqlite3.Connection, exercises: Iterable[Exercise]
    ) -> None:
        connection.executemany(
            f"""
            INSERT INTO {self.tmp_table_name} (title, description, difficulty)
            VALUES (:title, :description, :difficulty)
            """,
            [exercise.to_record() for exercise in exercises],
        )

    def get_changed_exercises(self, connection: sqlite3.Connection) -> list[Exercise]:
        rows = connection.execute(
            f"""
            SELECT
                tmp.title,
                tmp.description,
                tmp.difficulty
            FROM {self.tmp_table_name} AS tmp
            LEFT JOIN {self.latest_table_name} AS latest
                ON latest.title = tmp.title
            WHERE latest.title IS NULL
               OR latest.description != tmp.description
               OR latest.difficulty != tmp.difficulty
            ORDER BY tmp.title
            """
        ).fetchall()
        return [Exercise.from_row(row) for row in rows]

    def upsert_latest_exercises(
        self, connection: sqlite3.Connection, exercises: Iterable[Exercise]
    ) -> None:
        connection.executemany(
            f"""
            INSERT INTO {self.latest_table_name} (title, description, difficulty)
            VALUES (:title, :description, :difficulty)
            ON CONFLICT(title) DO UPDATE SET
                description = excluded.description,
                difficulty = excluded.difficulty
            """,
            [exercise.to_record() for exercise in exercises],
        )

