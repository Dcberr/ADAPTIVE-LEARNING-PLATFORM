from __future__ import annotations

from collections import deque
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
          sampleTestCase
          similarQuestions
          difficulty
          codeSnippets {
            langSlug
            code
          }
          topicTags {
            slug
          }
        }
      }
    }
    """

    question_detail_query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        titleSlug
        title
        content
        sampleTestCase
        similarQuestions
        difficulty
        codeSnippets {
          langSlug
          code
        }
        topicTags {
          slug
        }
      }
    }
    """

    def __init__(self, settings: LeetCodeSettings) -> None:
        self.settings = settings

    def get_exercises_by_tag(self, tag: str, limit: int) -> list[LeetCodeProblem]:
        self.logger.info("Fetching LeetCode exercises for tag=%s limit=%s", tag, limit)
        if limit == -1:
            seed_exercises = self._get_all_exercises_by_tag(tag)
        else:
            response_data = self._post_with_retry(self._build_payload(tag=tag, limit=limit, skip=0))
            seed_exercises = self._parse_problemset_exercises(response_data)
        exercises = self._expand_similar_exercises(seed_exercises, target_tag=tag)
        self.logger.info(
            "Fetched %s LeetCode exercises for tag=%s after BFS expansion from %s seed exercises",
            len(exercises),
            tag,
            len(seed_exercises),
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

            page_exercises = self._parse_problemset_exercises(response_data)
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

    def _build_question_detail_payload(self, title_slug: str) -> dict[str, Any]:
        return {
            "query": self.question_detail_query,
            "variables": {
                "titleSlug": title_slug,
            },
        }

    def _parse_problemset_exercises(self, response_data: dict[str, Any]) -> list[LeetCodeProblem]:
        questions = (
            response_data.get("data", {})
            .get("problemsetQuestionList", {})
            .get("questions", [])
        )
        exercises: list[LeetCodeProblem] = []
        for question in questions:
            exercise = self._parse_question(question)
            if exercise is not None:
                exercises.append(exercise)
        return exercises

    def _parse_question_detail(self, response_data: dict[str, Any]) -> LeetCodeProblem | None:
        question = response_data.get("data", {}).get("question")
        if not isinstance(question, dict):
            return None
        return self._parse_question(question)

    def _parse_question(self, question: dict[str, Any]) -> LeetCodeProblem | None:
        if (
            not question.get("titleSlug")
            or not question.get("title")
            or not question.get("difficulty")
        ):
            return None
        return LeetCodeProblem(
            question_slug=question["titleSlug"].strip(),
            title=question["title"].strip(),
            content=self._normalize_content(question.get("content")),
            sample_test_case=self._normalize_text(question.get("sampleTestCase")),
            code_snippet=self._extract_cpp_code_snippet(question.get("codeSnippets")),
            difficulty=question["difficulty"].strip(),
            topic_tag_slugs=self._extract_topic_tag_slugs(question.get("topicTags")),
            similar_question_slugs=self._extract_similar_question_slugs(
                question.get("similarQuestions")
            ),
        )

    def _expand_similar_exercises(
        self,
        seed_exercises: list[LeetCodeProblem],
        target_tag: str,
    ) -> list[LeetCodeProblem]:
        exercises_by_slug = {
            exercise.question_slug: exercise for exercise in seed_exercises
        }
        visited_slugs = set(exercises_by_slug)
        queued_slugs: set[str] = set()
        slugs_to_visit: deque[tuple[str, int]] = deque()
        max_depth = self.settings.similar_question_max_depth

        for exercise in seed_exercises:
            for similar_slug in exercise.similar_question_slugs:
                if similar_slug in visited_slugs or similar_slug in queued_slugs:
                    continue
                slugs_to_visit.append((similar_slug, 1))
                queued_slugs.add(similar_slug)

        while slugs_to_visit:
            similar_slug, depth = slugs_to_visit.popleft()
            if similar_slug in visited_slugs:
                continue
            visited_slugs.add(similar_slug)

            exercise = self._get_exercise_by_slug(similar_slug)
            if exercise is None:
                self.logger.info(
                    "Skipping similar question slug=%s because no exercise detail was returned",
                    similar_slug,
                )
                continue

            if depth < max_depth:
                for nested_similar_slug in exercise.similar_question_slugs:
                    if nested_similar_slug in visited_slugs or nested_similar_slug in queued_slugs:
                        continue
                    slugs_to_visit.append((nested_similar_slug, depth + 1))
                    queued_slugs.add(nested_similar_slug)

            if target_tag not in exercise.topic_tag_slugs:
                continue

            exercises_by_slug.setdefault(exercise.question_slug, exercise)

        return list(exercises_by_slug.values())

    def _get_exercise_by_slug(self, title_slug: str) -> LeetCodeProblem | None:
        response_data = self._post_with_retry(self._build_question_detail_payload(title_slug))
        return self._parse_question_detail(response_data)

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
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        return value.strip()

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

    @staticmethod
    def _extract_cpp_code_snippet(code_snippets: Any) -> str:
        if not isinstance(code_snippets, list):
            return ""
        for code_snippet in code_snippets:
            if not isinstance(code_snippet, dict):
                continue
            if code_snippet.get("langSlug") != "cpp":
                continue
            code = code_snippet.get("code")
            if isinstance(code, str):
                return code.strip()
        return ""
