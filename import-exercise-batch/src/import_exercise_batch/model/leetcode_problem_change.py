from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from import_exercise_batch.model.leetcode_problem import LeetCodeProblem


@dataclass(frozen=True)
class LeetCodeProblemChange:
    exercise_id: str | None
    question_slug: str
    title: str
    content: str
    sample_test_case: str
    code_snippet: str
    difficulty: str
    topic_tag_slugs: list[str]
    similar_question_slugs: list[str]
    latest_sample_test_case: str
    latest_code_snippet: str
    latest_topic_tag_slugs: list[str]
    latest_similar_question_slugs: list[str]
    diff_type: str
    is_change_content: bool
    is_change_topic: bool
    is_change_similar_question: bool

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "LeetCodeProblemChange":
        return cls(
            exercise_id=str(row["exercise_id"]) if row["exercise_id"] is not None else None,
            question_slug=row["question_slug"],
            title=row["title"],
            content=row["content"],
            sample_test_case=row["sample_test_case"],
            code_snippet=row["code_snippet"],
            difficulty=row["difficulty"],
            topic_tag_slugs=json.loads(row["topic_tag_slugs"]),
            similar_question_slugs=json.loads(row["similar_question_slugs"]),
            latest_sample_test_case=row["latest_sample_test_case"] or "",
            latest_code_snippet=row["latest_code_snippet"] or "",
            latest_topic_tag_slugs=json.loads(row["latest_topic_tag_slugs"] or "[]"),
            latest_similar_question_slugs=json.loads(
                row["latest_similar_question_slugs"] or "[]"
            ),
            diff_type=row["diff_type"],
            is_change_content=row["is_change_content"],
            is_change_topic=row["is_change_topic"],
            is_change_similar_question=row["is_change_similar_question"],
        )

    def to_problem(self) -> LeetCodeProblem:
        return LeetCodeProblem(
            question_slug=self.question_slug,
            title=self.title,
            content=self.content,
            sample_test_case=self.sample_test_case,
            code_snippet=self.code_snippet,
            difficulty=self.difficulty,
            topic_tag_slugs=self.topic_tag_slugs,
            similar_question_slugs=self.similar_question_slugs,
        )

    def to_record(self) -> dict[str, str | None]:
        record = asdict(self)
        record["topic_tag_slugs"] = json.dumps(self.topic_tag_slugs, ensure_ascii=False)
        record["similar_question_slugs"] = json.dumps(
            self.similar_question_slugs, ensure_ascii=False
        )
        return {
            "exercise_id": record["exercise_id"],
            "question_slug": record["question_slug"],
            "title": record["title"],
            "content": record["content"],
            "sample_test_case": record["sample_test_case"],
            "code_snippet": record["code_snippet"],
            "difficulty": record["difficulty"],
            "topic_tag_slugs": record["topic_tag_slugs"],
            "similar_question_slugs": record["similar_question_slugs"],
        }

    def added_topic_tag_slugs(self) -> list[str]:
        latest_topics = set(self.latest_topic_tag_slugs)
        return [slug for slug in self.topic_tag_slugs if slug not in latest_topics]

    def added_similar_question_slugs(self) -> list[str]:
        latest_similar_questions = set(self.latest_similar_question_slugs)
        return [
            slug
            for slug in self.similar_question_slugs
            if slug not in latest_similar_questions
        ]
