import logging
from typing import Dict

from openai import OpenAI

from app.models.review_state import LogicIssue, ReviewState
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class FixHintAgent:
    """Generates fix suggestions for each relevant concept in CS1 submissions with assignment context."""

    def __init__(self, client: OpenAI, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate_messages(
        self,
        issue: LogicIssue,
        assignment: str,
        current_code: str,
        testcase_context: str,
        previous_code: str | None = None,
        progress_summary: str = "",
    ) -> list[Dict[str, str]]:
        """Generate structured messages (system + user) for the model."""
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful CS1 tutoring assistant. "
                "Your goal is to help students understand and fix their code issues "
                "by focusing on conceptual understanding. "
                "Do not reveal the full code solution — instead, guide the student with reasoning and hints."
            ),
        }

        user_message = {
            "role": "user",
            "content": f"""
                ASSIGNMENT DESCRIPTION:
                {assignment}

                CURRENT STUDENT CODE:
                {current_code}

                CODE SNIPPET (from student's submission):
                {issue.get('code_snippet', '')}

                PROBLEM SUMMARY:
                {issue.get('issue', '')}

                FAILING TESTCASE DETAILS:
                {testcase_context}

                RELATED CS1 CONCEPTS (relevant only):
                {issue.get('relevant_concept', [])}

                EVIDENCE: Test case ID {issue.get('evidence')}

                HISTORY STATUS:
                {issue.get('history_status', 'unknown')}

                FIRST PREVIOUS SUBMISSION THAT FAILED THIS SAME TEST CASE:
                {previous_code if previous_code else "None"}

                SUBMISSION PROGRESS SUMMARY:
                {progress_summary}

                TASK:
                Based on the above information, generate a JSON object with a clear fix hint
                that explains what might be wrong conceptually and what steps the student
                should take to fix it.

                If the previous submission failed this same test case, also explain briefly:
                1. what the student improved from the previous code
                2. what still needs to be fixed now

                Output must be valid JSON:
                {{
                    "fix_suggestion": "your suggestion here"
                }}
                            """,
        }

        return [system_message, user_message]

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
        previous_code: str | None,
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

        if previous_code:
            suggestion_parts.append(
                "Compared with the previous submission, you did make a change, but the same testcase still fails. "
                "That means the fix was partial or aimed at one special value instead of the full rule the problem requires."
            )

        return "\n".join(suggestion_parts)

    def get_first_matching_history_code(
        self, state: ReviewState, testcase_id: str
    ) -> str | None:
        """Return the first previous submission code that failed the same testcase."""
        for submission in state.get("history", []):
            failed_test_case_ids = submission.get("failed_test_case_ids", [])
            if testcase_id in failed_test_case_ids:
                return submission.get("code", "")
        return None

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
        progress_summary = (
            f"Persistent failed testcases: {new_state.get('persistent_failed_test_case_ids', [])}\n"
            f"Fixed testcases from the first history entry: {new_state.get('fixed_test_case_ids', [])}\n"
            f"Newly failing testcases relative to the first history entry: {new_state.get('regressed_test_case_ids', [])}"
        )

        for issue_id, issue in logic_issues.items():
            logger.debug(
                "FixHintAgent generating hint for issue %s with concepts=%s",
                issue_id,
                issue.get("relevant_concept", []) or issue.get("other_concept", []),
            )
            previous_code = self.get_first_matching_history_code(
                new_state, issue.get("evidence", "")
            )
            testcase_context = self.get_testcase_context(
                new_state, issue.get("evidence", "")
            )
            messages = self.generate_messages(
                issue,
                assignment,
                current_code,
                testcase_context,
                previous_code,
                progress_summary,
            )

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.4,
                    max_tokens=512,
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
                    or self.build_fallback_fix_suggestion(
                        issue, testcase_context, previous_code
                    )
                )
                logger.debug(
                    "FixHintAgent stored fix suggestion for issue %s",
                    issue_id,
                )
                logic_issues[issue_id] = issue

            except Exception as e:
                logger.exception("FixHintAgent failed for issue %s", issue_id)
                issue["fix_suggestion"] = self.build_fallback_fix_suggestion(
                    issue, testcase_context, previous_code
                )
                logic_issues[issue_id] = issue

        new_state["logic_issues"] = logic_issues
        logger.debug(
            "FixHintAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
