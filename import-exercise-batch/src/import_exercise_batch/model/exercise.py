from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Exercise:
    title: str
    description: str
    difficulty: str

    def to_record(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Exercise":
        return cls(
            title=row["title"],
            description=row["description"],
            difficulty=row["difficulty"],
        )

