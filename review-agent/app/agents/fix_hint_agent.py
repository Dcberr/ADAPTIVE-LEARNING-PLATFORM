import logging
from typing import Dict

from openai import OpenAI

from app.models.review_state import LogicIssue, ReviewState
from app.prompts.review.fix_hint import build_fix_hint_messages
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class FixHintAgent:
    """Generates fix suggestions for each current logic issue in CS1 submissions."""

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.4,
        max_tokens: int = 512,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

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
        suggestion_parts = [
            f"Focus on testcase `{issue.get('evidence', '')}`.",
            testcase_context,
            (
                f"The current issue is: {issue.get('issue', '')} "
                "Trace the program line by line for this exact input and write down how each important variable changes."
            ),
            (
                "Compare the moment your code produces the current output with the expected behavior, "
                "then replace any special-case handling with logic that works for the general case."
            ),
        ]

        return "\n".join(suggestion_parts)

    def analyze(self, state: ReviewState) -> ReviewState:
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

        for issue_id, issue in logic_issues.items():
            logger.debug(
                "FixHintAgent generating hint for issue %s",
                issue_id,
            )
            testcase_context = self.get_testcase_context(
                new_state, issue.get("evidence", "")
            )
            messages = self.generate_messages(
                issue,
                assignment,
                current_code,
                testcase_context,
            )

            try:
                response = self.client.chat.completions.create(
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
                parsed = safe_parse_json_response(model_text)

                issue["fix_suggestion"] = (
                    parsed.get("fix_suggestion", "").strip()
                    or self.build_fallback_fix_suggestion(issue, testcase_context)
                )
                logger.debug(
                    "FixHintAgent stored fix suggestion for issue %s",
                    issue_id,
                )
                logic_issues[issue_id] = issue

            except Exception as e:
                logger.exception("FixHintAgent failed for issue %s", issue_id)
                issue["fix_suggestion"] = self.build_fallback_fix_suggestion(
                    issue, testcase_context
                )
                logic_issues[issue_id] = issue

        new_state["logic_issues"] = logic_issues
        logger.debug(
            "FixHintAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
