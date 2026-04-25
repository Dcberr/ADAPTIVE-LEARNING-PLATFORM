from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ExerciseImportRecord:
    question_slug: str
    title: str
    content: str
    difficulty: str
    topic_tag_slugs: list[str]
    similar_question_slugs: list[str]

    def to_record(self) -> dict[str, str]:
        record = asdict(self)
        record["topic_tag_slugs"] = json.dumps(self.topic_tag_slugs, ensure_ascii=False)
        record["similar_question_slugs"] = json.dumps(
            self.similar_question_slugs, ensure_ascii=False
        )
        return record

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "ExerciseImportRecord":
        return cls(
            question_slug=row["question_slug"],
            title=row["title"],
            content=row["content"],
            difficulty=row["difficulty"],
            topic_tag_slugs=json.loads(row["topic_tag_slugs"]),
            similar_question_slugs=json.loads(row["similar_question_slugs"]),
        )
