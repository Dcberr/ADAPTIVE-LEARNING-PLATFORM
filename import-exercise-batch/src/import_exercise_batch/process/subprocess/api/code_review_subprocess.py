from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable, Iterable
from dataclasses import replace
from typing import TypeVar
from uuid import uuid4

import urllib3
from code_review_api_client import (
    ApiClient,
    ApiResponseListProblemResponse,
    Configuration,
    LeetCodeImportRequest,
    ProblemApi,
    ProblemResponse,
    TestcaseDto,
)
from code_review_api_client.exceptions import ApiException
from import_exercise_batch.model import LeetCodeProblemChange
from import_exercise_batch.process.subprocess.base import BaseSubProcess


class CodeReviewSubProcess(BaseSubProcess):
    logger = logging.getLogger(__name__)
    constraints_separator = "<p><strong>Constraints:</strong></p>"
    _ChunkItem = TypeVar("_ChunkItem")
    _ReturnValue = TypeVar("_ReturnValue")

    def __init__(
        self,
        base_url: str,
        max_retries: int,
        backoff_seconds: float,
        batch_import_chunk_size: int,
    ) -> None:
        self.base_url = base_url
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.batch_import_chunk_size = batch_import_chunk_size

    def import_exercise(
        self,
        exercises: Iterable[LeetCodeProblemChange],
    ) -> list[LeetCodeProblemChange]:
        processed_exercises: list[LeetCodeProblemChange] = []
        processed_count = 0
        for exercise in exercises:
            if exercise.diff_type == "create":
                exercise = self._assign_temp_exercise_id(exercise)
                self.logger.info(
                    "Creating exercise slug=%s title=%s exercise_id=%s",
                    exercise.question_slug,
                    exercise.title,
                    exercise.exercise_id,
                )
            elif exercise.diff_type == "update":
                self.logger.info(
                    "Updating exercise slug=%s title=%s exercise_id=%s",
                    exercise.question_slug,
                    exercise.title,
                    exercise.exercise_id,
                )
            else:
                self.logger.info(
                    "Skipping unchanged exercise slug=%s title=%s",
                    exercise.question_slug,
                    exercise.title,
                )
                continue

            processed_exercises.append(exercise)
            processed_count += 1

        if not self.base_url:
            self.logger.warning(
                "Skipping code review API batch import because CODE_REVIEW_API_BASE_URL is empty"
            )
            return processed_exercises

        if not processed_exercises:
            self.logger.info("No changed exercises to import to code review API")
            return processed_exercises

        configuration = Configuration(host=self.base_url)
        total_chunks = (
            len(processed_exercises) + self.batch_import_chunk_size - 1
        ) // self.batch_import_chunk_size
        success_count = 0
        self.logger.info(
            "Running code review API LeetCode batch import with %s chunks for %s exercises",
            total_chunks,
            len(processed_exercises),
        )
        for chunk_index, chunk in enumerate(
            self._chunked(processed_exercises, self.batch_import_chunk_size),
            start=1,
        ):
            chunk_start = (chunk_index - 1) * self.batch_import_chunk_size + 1
            chunk_end = chunk_start + len(chunk) - 1
            request = [
                self._build_leet_code_import_request(exercise) for exercise in chunk
            ]
            self.logger.info(
                "Calling code review API LeetCode batch import chunk=%s/%s records=%s range=%s-%s",
                chunk_index,
                total_chunks,
                len(chunk),
                chunk_start,
                chunk_end,
            )
            import_response = self._call_with_retry(
                action_name="batch import leetcode problems",
                target_identifier=f"chunk={chunk_index}/{total_chunks}",
                call=lambda request=request: self._call_import_leet_code_problems(
                    configuration,
                    request,
                ),
            )
            processed_exercises[chunk_start - 1 : chunk_end] = (
                self._merge_import_results(
                    chunk,
                    import_response.data or [],
                )
            )
            success_count += len(chunk)
            self.logger.info(
                "Code review API LeetCode batch import chunk succeeded chunk=%s/%s success_records=%s success_total=%s/%s",
                chunk_index,
                total_chunks,
                len(chunk),
                success_count,
                len(processed_exercises),
            )
        self.logger.info(
            "Processed %s changed exercises for code review API", processed_count
        )
        return processed_exercises

    def _build_leet_code_import_request(
        self,
        exercise: LeetCodeProblemChange,
    ) -> LeetCodeImportRequest:
        description, constraints = self._split_description_and_constraints(
            exercise.content
        )
        return LeetCodeImportRequest(
            externalId=exercise.question_slug,
            title=exercise.title,
            description=description,
            difficulty=exercise.difficulty,
            constraints=constraints,
            starterCodes={"cpp": exercise.code_snippet},
            testcases=self._parse_testcases(exercise.sample_test_case, exercise.content),
            similarQuestionIds=[],
            tags=exercise.topic_tag_slugs,
        )

    @staticmethod
    def _assign_temp_exercise_id(
        exercise: LeetCodeProblemChange,
    ) -> LeetCodeProblemChange:
        if exercise.exercise_id is not None:
            return exercise
        return replace(exercise, exercise_id=str(uuid4()))

    def _split_description_and_constraints(
        self, content: str
    ) -> tuple[str, str | None]:
        description, separator, constraints = content.partition(
            self.constraints_separator
        )
        normalized_description = description.strip("\n")
        if not separator:
            return normalized_description, None
        normalized_constraints = constraints.strip("\n")
        return normalized_description, normalized_constraints or None

    def _parse_testcases(self, sample_test_case: str, content: str) -> list[TestcaseDto]:
        parsed_from_content = self._parse_testcases_from_content(content)
        if parsed_from_content:
            return parsed_from_content

        parsed_from_sample = self._parse_testcases_from_sample(sample_test_case)
        if parsed_from_sample:
            self.logger.warning(
                "Using fallback testcase parsing from sample_test_case; output quality may be limited"
            )
        else:
            self.logger.warning(
                "No testcase could be extracted from content/sample_test_case"
            )
        return parsed_from_sample

    @classmethod
    def _parse_testcases_from_content(cls, content: str) -> list[TestcaseDto]:
        if not content:
            return []

        pre_blocks = re.findall(r"<pre>(.*?)</pre>", content, flags=re.IGNORECASE | re.DOTALL)
        testcases: list[TestcaseDto] = []

        for pre_block in pre_blocks:
            plain_block = cls._strip_html_tags(pre_block)
            parsed_pair = cls._extract_input_output_pair(plain_block)
            if parsed_pair is None:
                continue

            raw_input, raw_output = parsed_pair
            normalized_input = cls._normalize_input_arguments(raw_input)
            normalized_output = raw_output.strip()
            if not normalized_input or not normalized_output:
                continue

            testcases.append(
                TestcaseDto(
                    input=normalized_input,
                    expectedOutput=normalized_output,
                    isHidden=True,
                    explanation="",
                )
            )

        return cls._deduplicate_testcases(testcases)

    @staticmethod
    def _parse_testcases_from_sample(sample_test_case: str) -> list[TestcaseDto]:
        if not sample_test_case:
            return []

        lines = [line.strip() for line in sample_test_case.splitlines() if line.strip()]
        testcases: list[TestcaseDto] = []
        for index in range(0, len(lines) - 1, 2):
            testcases.append(
                TestcaseDto(
                    input=lines[index],
                    expectedOutput=lines[index + 1],
                    isHidden=True,
                    explanation="",
                )
            )
        return testcases

    @staticmethod
    def _strip_html_tags(value: str) -> str:
        without_tags = re.sub(r"<[^>]+>", "", value)
        return re.sub(r"\s+", " ", without_tags).strip()

    @classmethod
    def _extract_input_output_pair(cls, value: str) -> tuple[str, str] | None:
        input_match = re.search(
            r"Input\s*:\s*(.+?)(?=\s*Output\s*:|$)",
            value,
            flags=re.IGNORECASE | re.DOTALL,
        )
        output_match = re.search(
            r"Output\s*:\s*(.+?)(?=\s*Explanation\s*:|$)",
            value,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not input_match or not output_match:
            return None

        return input_match.group(1).strip(), output_match.group(1).strip()

    @classmethod
    def _normalize_input_arguments(cls, raw_input: str) -> str:
        compact_input = " ".join(raw_input.split())
        if "=" not in compact_input:
            return compact_input

        parts = cls._split_top_level_csv(compact_input)
        argument_values: list[str] = []
        for part in parts:
            if "=" not in part:
                continue
            _, value = part.split("=", 1)
            normalized_value = value.strip()
            if normalized_value:
                argument_values.append(normalized_value)

        if not argument_values:
            return compact_input
        return "\n".join(argument_values)

    @staticmethod
    def _split_top_level_csv(value: str) -> list[str]:
        parts: list[str] = []
        current: list[str] = []
        bracket_depth = 0
        brace_depth = 0
        paren_depth = 0
        in_single_quote = False
        in_double_quote = False

        for char in value:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif not in_single_quote and not in_double_quote:
                if char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth = max(0, bracket_depth - 1)
                elif char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth = max(0, brace_depth - 1)
                elif char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth = max(0, paren_depth - 1)
                elif (
                    char == ','
                    and bracket_depth == 0
                    and brace_depth == 0
                    and paren_depth == 0
                ):
                    part = "".join(current).strip()
                    if part:
                        parts.append(part)
                    current = []
                    continue
            current.append(char)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)
        return parts

    @staticmethod
    def _deduplicate_testcases(testcases: list[TestcaseDto]) -> list[TestcaseDto]:
        deduplicated: list[TestcaseDto] = []
        seen: set[tuple[str, str]] = set()
        for testcase in testcases:
            key = (testcase.input, testcase.expected_output)
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(testcase)
        return deduplicated

    @staticmethod
    def _chunked(
        items: list[_ChunkItem],
        chunk_size: int,
    ) -> Iterable[list[_ChunkItem]]:
        for index in range(0, len(items), chunk_size):
            yield items[index : index + chunk_size]

    def _call_with_retry(
        self,
        action_name: str,
        target_identifier: str,
        call: Callable[[], _ReturnValue],
    ) -> _ReturnValue:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return call()
                if attempt > 1:
                    self.logger.info(
                        "Code review API %s succeeded on retry attempt=%s target=%s",
                        action_name,
                        attempt,
                        target_identifier,
                    )
                return
            except Exception as error:
                last_error = error
                should_retry = self._should_retry_error(error)
                self.logger.warning(
                    "Code review API %s failed on attempt=%s target=%s retry=%s error=%s",
                    action_name,
                    attempt,
                    target_identifier,
                    should_retry and attempt < self.max_retries,
                    error,
                )
                if not should_retry or attempt == self.max_retries:
                    raise
                time.sleep(self.backoff_seconds * attempt)

        if last_error is not None:
            raise last_error
        raise RuntimeError(
            f"Code review API {action_name} failed without returning or raising target={target_identifier}"
        )

    def _merge_import_results(
        self,
        exercises: list[LeetCodeProblemChange],
        imported_problems: list[ProblemResponse],
    ) -> list[LeetCodeProblemChange]:
        imported_ids_by_slug: dict[str, str] = {}
        for problem in imported_problems:
            if problem.external_id is None or problem.id is None:
                raise ValueError(
                    "Code review API import response must include externalId and id for every problem"
                )
            imported_ids_by_slug[problem.external_id] = str(problem.id)

        missing_slugs = [
            exercise.question_slug
            for exercise in exercises
            if exercise.question_slug not in imported_ids_by_slug
        ]
        if missing_slugs:
            raise ValueError(
                "Code review API import response missing problems for slugs: "
                + ", ".join(missing_slugs)
            )

        return [
            replace(
                exercise,
                exercise_id=imported_ids_by_slug[exercise.question_slug],
            )
            for exercise in exercises
        ]

    @staticmethod
    def _should_retry_error(error: Exception) -> bool:
        if isinstance(error, ApiException):
            status = error.status
            return status is None or status in {408, 429} or 500 <= status <= 599
        return isinstance(error, urllib3.exceptions.HTTPError | OSError | TimeoutError)

    @staticmethod
    def _call_import_leet_code_problems(
        configuration: Configuration,
        request: list[LeetCodeImportRequest],
    ) -> ApiResponseListProblemResponse:
        with ApiClient(configuration) as api_client:
            api = ProblemApi(api_client)
            return api.import_leet_code_problems(leet_code_import_request=request)
