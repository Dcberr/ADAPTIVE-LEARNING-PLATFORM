from __future__ import annotations

import json
import time
from html import unescape
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from import_exercise_batch.config import LeetCodeSettings
from import_exercise_batch.model import ExerciseImportRecord
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class LeetCodeFetchSubProcess(BaseSubProcess):
    problemset_query = """
    query problemsetQuestionList(
      $categorySlug: String,
      $limit: Int,
      $skip: Int,
      $filters: QuestionListFilterInput
    ) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          titleSlug
          title
          content
          similarQuestions
          difficulty
          topicTags {
            slug
          }
        }
      }
    }
    """

    def __init__(self, settings: LeetCodeSettings) -> None:
        self.settings = settings

    def get_exercises_by_tag(self, tag: str, limit: int) -> list[ExerciseImportRecord]:
        payload = {
            "query": self.problemset_query,
            "variables": {
                "categorySlug": "",
                "skip": 0,
                "limit": limit,
                "filters": {
                    "tags": [tag],
                },
            },
        }
        response_data = self._post_with_retry(payload)
        questions = (
            response_data.get("data", {})
            .get("problemsetQuestionList", {})
            .get("questions", [])
        )
        return [
            ExerciseImportRecord(
                question_slug=question["titleSlug"].strip(),
                title=question["title"].strip(),
                content=self._normalize_content(question.get("content")),
                difficulty=question["difficulty"].strip(),
                topic_tag_slugs=self._extract_topic_tag_slugs(question.get("topicTags")),
                similar_question_slugs=self._extract_similar_question_slugs(
                    question.get("similarQuestions")
                ),
            )
            for question in questions
            if question.get("titleSlug")
            and question.get("title")
            and question.get("difficulty")
        ]

    def resolve_limit(self, limit: int) -> int:
        return self.settings.limit if limit < 0 else limit

    def _post_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            self.settings.graphql_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "import-exercise-batch/0.1.0",
            },
            method="POST",
        )

        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                with urlopen(request, timeout=self.settings.request_timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    if parsed.get("errors"):
                        raise RuntimeError(
                            f"LeetCode GraphQL returned errors: {parsed['errors']}"
                        )
                    return parsed
            except (
                HTTPError,
                URLError,
                TimeoutError,
                json.JSONDecodeError,
                RuntimeError,
            ) as error:
                last_error = error
                if attempt == self.settings.max_retries:
                    break
                time.sleep(self.settings.backoff_seconds * attempt)

        raise RuntimeError("Unable to fetch LeetCode exercises after retries") from last_error

    @staticmethod
    def _normalize_content(content: str | None) -> str:
        if not content:
            return ""
        return unescape(content).strip()

    @staticmethod
    def _extract_topic_tag_slugs(topic_tags: Any) -> list[str]:
        if not isinstance(topic_tags, list):
            return []
        return [
            topic_tag["slug"].strip()
            for topic_tag in topic_tags
            if isinstance(topic_tag, dict) and topic_tag.get("slug")
        ]

    @staticmethod
    def _extract_similar_question_slugs(similar_questions: Any) -> list[str]:
        if not similar_questions:
            return []
        if not isinstance(similar_questions, str):
            return []

        try:
            parsed = json.loads(similar_questions)
        except json.JSONDecodeError:
            return []

        if not isinstance(parsed, list):
            return []

        return [
            item["titleSlug"].strip()
            for item in parsed
            if isinstance(item, dict) and item.get("titleSlug")
        ]
