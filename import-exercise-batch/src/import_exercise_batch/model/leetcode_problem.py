from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class LeetCodeProblem:
    question_slug: str
    title: str
    content: str
    sample_test_case: str
    code_snippet: str
    difficulty: str
    topic_tag_slugs: list[str]
    similar_question_slugs: list[str]

    def has_full_payload(self) -> bool:
        return bool(
            self.content.strip()
            and self.sample_test_case.strip()
            and self.code_snippet.strip()
        )

    def to_record(self) -> dict[str, str]:
        record = asdict(self)
        record["topic_tag_slugs"] = json.dumps(self.topic_tag_slugs, ensure_ascii=False)
        record["similar_question_slugs"] = json.dumps(
            self.similar_question_slugs, ensure_ascii=False
        )
        return record

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "LeetCodeProblem":
        return cls(
            question_slug=row["question_slug"],
            title=row["title"],
            content=row["content"],
            sample_test_case=row["sample_test_case"],
            code_snippet=row["code_snippet"],
            difficulty=row["difficulty"],
            topic_tag_slugs=json.loads(row["topic_tag_slugs"]),
            similar_question_slugs=json.loads(row["similar_question_slugs"]),
        )
