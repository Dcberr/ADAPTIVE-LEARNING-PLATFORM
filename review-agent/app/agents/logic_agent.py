import logging
from typing import Any, Dict
from openai import OpenAI

from app.models.logic_issue import create_logic_issue
from app.models.review_state import (
    LogicIssue,
    ReviewState,
    SandBoxResult,
)
from app.prompts.review.logic import build_logic_messages
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class LogicAgent:
    """Analyzes sandbox outputs and produces logic issues with a chat model."""

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.batch_size = 5

    def chunk_test_cases(self, cases: list):
        """Yield successive batches of test cases."""
        for i in range(0, len(cases), self.batch_size):
            yield cases[i : i + self.batch_size]

    def _normalize_output(self, value: Any) -> str:
        """Normalize sandbox outputs before comparing expected vs actual."""
        if value is None:
            return ""
        return str(value).strip()

    def _is_meaningfully_failed(self, case: SandBoxResult) -> bool:
        """Keep only cases where expected and actual differ after normalization."""
        return self._normalize_output(case.get("expected")) != self._normalize_output(
            case.get("actual")
        )

    def generate_messages(
        self,
        code: str,
        failed_tests: list[SandBoxResult],
        history: list[dict[str, Any]],
    ) -> list:
        return build_logic_messages(code=code, failed_tests=failed_tests, history=history)

    def classify_history_status(self, state: ReviewState, testcase_id: str) -> str:
        """Classify a failing testcase relative to the first history entry."""
        if testcase_id in state.get("persistent_failed_test_case_ids", []):
            return "persistent"
        if testcase_id in state.get("regressed_test_case_ids", []):
            return "regression"
        return "current_only"

    def create_fallback_issue(
        self, state: ReviewState, failed_test: SandBoxResult
    ) -> LogicIssue:
        """Create a deterministic issue when model parsing fails or returns nothing."""
        input_value = failed_test.get("input", "")
        actual_output = failed_test.get("actual", "")
        expected_output = failed_test.get("expected", "")
        issue = create_logic_issue(
            issue=(
                "The program output does not match the expected result for this testcase. "
                f"For input '{input_value}', it returned '{actual_output}' but expected '{expected_output}'."
            ),
            evidence=failed_test["id"],
            code_snippet=state.get("code", ""),
            location=None,
        )
        issue["history_status"] = self.classify_history_status(
            state, failed_test["id"]
        )
        issue["fix_suggestion"] = (
            f"Start with the failing input '{input_value}' and trace the code line by line. "
            f"Write down the important variable values after each step, then note exactly where the program produces '{actual_output}' "
            f"instead of the expected '{expected_output}'. From there, replace any special-case or hard-coded behavior with logic that works for the general case."
        )
        return issue

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        """Run logic analysis on a submission state and return updated state."""
        logger.debug("Starting LogicAgent with state summary: %s", summarize_state(state))

        new_state: ReviewState = dict(state)
        raw_cases = state.get("sandbox_results", [])
        cases = [case for case in raw_cases if self._is_meaningfully_failed(case)]
        history = state.get("history", [])
        all_issues: Dict[str, LogicIssue] = {}

        if len(cases) != len(raw_cases):
            logger.debug(
                "LogicAgent filtered out %s sandbox results where expected matched actual",
                len(raw_cases) - len(cases),
            )

        for batch_index, batch in enumerate(self.chunk_test_cases(cases), start=1):
            logger.debug(
                "LogicAgent processing batch %s with test ids=%s",
                batch_index,
                [case["id"] for case in batch],
            )
            messages = self.generate_messages(state.get("code", ""), batch, history)

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

                model_text = response.choices[0].message.content
                logger.debug(
                    "LogicAgent batch %s raw response preview: %s",
                    batch_index,
                    truncate_text(model_text),
                )
                parsed = safe_parse_json_response(model_text)
                batch_issues = parsed.get("logic_issues") or []
                logger.debug(
                    "LogicAgent batch %s parsed %s issues",
                    batch_index,
                    len(batch_issues),
                )
                for issue_data in batch_issues:
                    evidence = str(issue_data.get("evidence", "")).strip()
                    if not evidence:
                        continue
                    issue = create_logic_issue(
                        issue=issue_data.get("issue", ""),
                        evidence=evidence,
                        code_snippet=issue_data.get("code_snippet", ""),
                        location=issue_data.get("location"),
                    )
                    issue["history_status"] = self.classify_history_status(
                        new_state, evidence
                    )
                    all_issues[issue["evidence"]] = issue

                if not batch_issues:
                    logger.debug(
                        "LogicAgent batch %s produced no parsed issues, using fallback issues",
                        batch_index,
                    )
                    for failed_test in batch:
                        fallback_issue = self.create_fallback_issue(
                            new_state, failed_test
                        )
                        all_issues[fallback_issue["evidence"]] = fallback_issue

            except Exception as e:
                logger.exception("LogicAgent batch %s failed", batch_index)
                for failed_test in batch:
                    fallback_issue = self.create_fallback_issue(new_state, failed_test)
                    all_issues[fallback_issue["evidence"]] = fallback_issue

        new_state["logic_issues"] = all_issues

        logger.debug(
            "LogicAgent completed with %s total logic issues",
            len(new_state["logic_issues"]),
        )
        return new_state
