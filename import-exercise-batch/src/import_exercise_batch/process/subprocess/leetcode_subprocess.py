from __future__ import annotations

import json
import time
from html import unescape
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from import_exercise_batch.config import Settings
from import_exercise_batch.model import Exercise
from import_exercise_batch.process.subprocess.base_subprocess import BaseSubProcess


class LeetCodeFetchSubProcess(BaseSubProcess):
    problemset_query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
      ) {
        questions: data {
          title
          content
          difficulty
        }
      }
    }
    """

    def __init__(self, settings: Settings, limit: int = 100) -> None:
        self.settings = settings
        self.limit = limit

    def run(self) -> list[Exercise]:
        payload = {
            "query": self.problemset_query,
            "variables": {
                "categorySlug": "",
                "skip": 0,
                "limit": self.limit,
            },
        }
        response_data = self._post_with_retry(payload)
        questions = (
            response_data.get("data", {})
            .get("problemsetQuestionList", {})
            .get("questions", [])
        )
        return [
            Exercise(
                title=question["title"].strip(),
                description=self._normalize_description(question.get("content")),
                difficulty=question["difficulty"].strip(),
            )
            for question in questions
            if question.get("title") and question.get("difficulty")
        ]

    def _post_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            self.settings.leetcode_graphql_url,
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
    def _normalize_description(content: str | None) -> str:
        if not content:
            return ""
        return unescape(content).strip()

