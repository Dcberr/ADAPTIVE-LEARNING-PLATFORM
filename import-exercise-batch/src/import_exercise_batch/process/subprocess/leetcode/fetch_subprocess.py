from __future__ import annotations

import json
import logging
import time
from html import unescape
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from import_exercise_batch.config import LeetCodeSettings
from import_exercise_batch.model import LeetCodeProblem
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class LeetCodeFetchSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)

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

    def get_exercises_by_tag(self, tag: str, limit: int) -> list[LeetCodeProblem]:
        self.logger.info("Fetching LeetCode exercises for tag=%s limit=%s", tag, limit)
        if limit == -1:
            exercises = self._get_all_exercises_by_tag(tag)
        else:
            response_data = self._post_with_retry(self._build_payload(tag=tag, limit=limit, skip=0))
            exercises = self._parse_exercises(response_data)
        self.logger.info(
            "Fetched %s LeetCode exercises for tag=%s",
            len(exercises),
            tag,
        )
        return exercises

    def resolve_limit(self, limit: int) -> int:
        return limit

    def _get_all_exercises_by_tag(self, tag: str) -> list[LeetCodeProblem]:
        exercises: list[LeetCodeProblem] = []
        skip = 0
        page_limit = self.settings.limit
        total: int | None = None

        while True:
            response_data = self._post_with_retry(
                self._build_payload(tag=tag, limit=page_limit, skip=skip)
            )
            page = response_data.get("data", {}).get("problemsetQuestionList", {})
            if total is None:
                total_value = page.get("total")
                total = total_value if isinstance(total_value, int) else None

            page_exercises = self._parse_exercises(response_data)
            exercises.extend(page_exercises)
            self.logger.info(
                "Fetched page for tag=%s skip=%s page_size=%s total_loaded=%s total=%s",
                tag,
                skip,
                len(page_exercises),
                len(exercises),
                total if total is not None else "unknown",
            )

            if not page_exercises:
                break
            skip += page_limit
            if total is not None and skip >= total:
                break
            if len(page_exercises) < page_limit:
                break

        return exercises

    def _build_payload(self, tag: str, limit: int, skip: int) -> dict[str, Any]:
        return {
            "query": self.problemset_query,
            "variables": {
                "categorySlug": "",
                "skip": skip,
                "limit": limit,
                "filters": {
                    "tags": [tag],
                },
            },
        }

    def _parse_exercises(self, response_data: dict[str, Any]) -> list[LeetCodeProblem]:
        questions = (
            response_data.get("data", {})
            .get("problemsetQuestionList", {})
            .get("questions", [])
        )
        return [
            LeetCodeProblem(
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

    def _post_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "import-exercise-batch/0.1.0",
        }
        cookies: list[str] = []
        if self.settings.session:
            cookies.append(f"LEETCODE_SESSION={self.settings.session}")
        if self.settings.csrf_token:
            headers["x-csrftoken"] = self.settings.csrf_token
            cookies.append(f"csrftoken={self.settings.csrf_token}")
        if cookies:
            headers["Cookie"] = "; ".join(cookies)

        request = Request(
            self.settings.graphql_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                self.logger.info(
                    "Calling LeetCode GraphQL attempt=%s url=%s",
                    attempt,
                    self.settings.graphql_url,
                )
                with urlopen(request, timeout=self.settings.request_timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    if parsed.get("errors"):
                        raise RuntimeError(
                            f"LeetCode GraphQL returned errors: {parsed['errors']}"
                        )
                    self.logger.info("LeetCode GraphQL call succeeded on attempt=%s", attempt)
                    return parsed
            except (
                HTTPError,
                URLError,
                TimeoutError,
                json.JSONDecodeError,
                RuntimeError,
            ) as error:
                last_error = error
                self.logger.warning(
                    "LeetCode GraphQL call failed on attempt=%s: %s",
                    attempt,
                    error,
                )
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
