import asyncio
import logging
from typing import Dict

from openai import OpenAI

from code_review_ai.models.review_state import LogicIssue, ReviewState
from code_review_ai.prompts.review.fix_hint import build_fix_hint_messages
from code_review_ai.utils.debug_logging import summarize_state, truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.review_output_tools import parse_review_json_with_repair

logger = logging.getLogger(__name__)


class FixHintAgent:
    """Generates fix suggestions for each current logic issue in CS1 submissions."""

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.4,
        max_tokens: int = 512,
        max_concurrency: int = 4,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_concurrency = max(1, max_concurrency)

    def generate_messages(
        self,
        issue: LogicIssue,
        assignment: str,
        current_code: str,
        testcase_context: str,
    ) -> list[Dict[str, str]]:
        return build_fix_hint_messages(
            issue=issue,
            assignment=assignment,
            current_code=current_code,
            testcase_context=testcase_context,
        )

    def get_testcase_context(self, state: ReviewState, testcase_id: str) -> str:
        """Return the failing testcase details for a given evidence id."""
        for testcase in state.get("sandbox_results", []):
            if testcase.get("id") == testcase_id:
                return (
                    f"Input: {testcase.get('input', '')}\n"
                    f"Expected output: {testcase.get('expected', '')}\n"
                    f"Actual output: {testcase.get('actual', '')}"
                )
        return "No testcase details available."

    def build_fallback_fix_suggestion(
        self,
        issue: LogicIssue,
        testcase_context: str,
    ) -> str:
        """Create a specific fallback hint when the model returns no structured JSON."""
        cause_type = issue.get("cause_type", "").strip()
        diagnosis_parts = [
            f"Focus on testcase `{issue.get('evidence', '')}`.",
            testcase_context,
            f"The current issue is: {issue.get('issue', '')}",
            (
                f"Why this testcase fails: {issue.get('why_test_failed', '')}"
                if issue.get("why_test_failed", "")
                else ""
            ),
            (
                f"Nearest related code: {issue.get('anchor_snippet', '')}"
                if issue.get("anchor_snippet", "")
                else ""
            ),
            (
                f"Missing behavior to add: {issue.get('missing_behavior', '')}"
                if issue.get("missing_behavior", "")
                else ""
            ),
        ]

        if cause_type == "incorrect_code":
            action = (
                "Start by tracing the current code snippet for this exact input and write down the key values before the program prints or returns the result. "
                "Then compare that moment with the expected behavior and adjust only the calculation or branch that produces the wrong output."
            )
        elif cause_type in {"missing_logic", "missing_branch"}:
            action = (
                "Start by checking which case is not handled yet for this input. "
                "Add one small branch or rule near the anchor snippet so this missing case is handled before the final output."
            )
        elif cause_type == "missing_validation":
            action = (
                "Start by checking what condition should be validated before the current logic continues. "
                "Add that validation first, then trace the testcase again to confirm the rest of the logic runs on valid input."
            )
        else:
            action = (
                "Trace the program line by line for this exact input, compare the current output with the expected behavior, "
                "and change the smallest part of the logic that causes the mismatch."
            )

        return "\n".join([part for part in diagnosis_parts if part] + [action])

    async def _process_issue(
        self,
        state: ReviewState,
        issue_id: str,
        issue: LogicIssue,
        assignment: str,
        current_code: str,
        semaphore: asyncio.Semaphore,
    ) -> tuple[str, LogicIssue]:
        testcase_context = self.get_testcase_context(
            state, issue.get("evidence", "")
        )
        messages = self.generate_messages(
            issue,
            assignment,
            current_code,
            testcase_context,
        )

        try:
            async with semaphore:
                response = await asyncio.to_thread(
                    create_chat_completion_with_retry,
                    self.client,
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

            model_text = response.choices[0].message.content
            logger.debug(
                "FixHintAgent raw response preview for issue %s: %s",
                issue_id,
                truncate_text(model_text),
            )
            parsed = parse_review_json_with_repair(
                client=self.client,
                model_name=self.model_name,
                raw_response=model_text,
                expected_shape={"fix_suggestion": str},
            )

            issue["fix_suggestion"] = (
                parsed.get("fix_suggestion", "").strip()
                or self.build_fallback_fix_suggestion(issue, testcase_context)
            )
            logger.debug(
                "FixHintAgent stored fix suggestion for issue %s",
                issue_id,
            )
        except Exception:
            logger.exception("FixHintAgent failed for issue %s", issue_id)
            issue["fix_suggestion"] = self.build_fallback_fix_suggestion(
                issue, testcase_context
            )

        return issue_id, issue

    async def analyze(self, state: ReviewState) -> ReviewState:
        """Generate fix suggestions for all relevant logic issues."""
        logger.debug(
            "Starting FixHintAgent with state summary: %s",
            summarize_state(state),
        )

        new_state: ReviewState = dict(state)
        logic_issues: Dict[str, LogicIssue] = new_state.get("logic_issues", {})
        assignment = new_state.get(
            "assignment_requirements", "No assignment description provided."
        )
        current_code = new_state.get("code", "")
        semaphore = asyncio.Semaphore(self.max_concurrency)

        if not logic_issues:
            logger.debug("FixHintAgent skipped because there are no logic issues")
            return new_state

        tasks = []

        for issue_id, issue in logic_issues.items():
            logger.debug(
                "FixHintAgent generating hint for issue %s",
                issue_id,
            )
            tasks.append(
                self._process_issue(
                    new_state,
                    issue_id,
                    issue,
                    assignment,
                    current_code,
                    semaphore,
                )
            )

        for issue_id, issue in await asyncio.gather(*tasks):
            logic_issues[issue_id] = issue

        new_state["logic_issues"] = logic_issues
        logger.debug(
            "FixHintAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
