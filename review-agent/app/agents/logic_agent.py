import logging
from typing import Any, Dict
from together import Together

from app.models.logic_issue import create_logic_issue
from app.models.review_state import (
    LogicIssue,
    ReviewState,
    SandBoxResult,
)
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class LogicAgent:
    """Analyzes sandbox outputs and produces logic_issues using Qwen Coder via Together AI."""

    def __init__(self, client: Together, model_name: str):
        self.client = client
        self.model_name = model_name
        self.batch_size = 5

    def chunk_test_cases(self, cases: list):
        """Yield successive batches of test cases."""
        for i in range(0, len(cases), self.batch_size):
            yield cases[i : i + self.batch_size]

    def generate_messages(self, code: str, failed_tests: list[SandBoxResult]) -> list:
        """
        Generate messages to instruct the model to detect errors from failing test cases
        and link each failure to the code snippet causing it.
        """

        system_msg = {
            "role": "system",
            "content": (
                "You are a CS1-level programming tutor. "
                "Your job is to analyze student code and failing test cases, "
                "and identify the specific code snippets causing each failure. "
                "You must respond in valid JSON only."
            ),
        }

        # Format the failing tests
        tests_str = "\n".join(
            [
                f"ID: {tc["id"]} | Input: {tc["input"]} | Expected: {tc["expected"]} | Actual: {tc["actual"]}"
                for tc in failed_tests
            ]
        )

        user_msg = {
            "role": "user",
            "content": f"""
                Student code:
                {code}

                Failing test cases:
                {tests_str}

                Instructions:
                1) For each failing test case, produce a JSON object containing:
                - "issue": a short explanation of why the test failed
                - "evidence": the 'id' of the failing test case
                - "code_snippet": the part of the student's code that likely caused this failure
                - "location": line/column start and end of the code snippet if known (otherwise null)
                2) Respond only in JSON format, matching this schema:
                {{
                    "logic_issues": [
                        {{
                            "issue": "short explanation",
                            "evidence": "test case id",
                            "code_snippet": "relevant code snippet",
                            "location": {{
                                "start_line": line_number,
                                "end_line": line_number,
                                "start_col": column_number (optional),
                                "end_col": column_number (optional)
                            }}  # optional
                        }}
                    ],
                }}
                Make your explanations concise and beginner-friendly.
                """,
        }

        return [system_msg, user_msg]

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        """Run logic analysis on a submission state and return updated state."""
        logger.debug("Starting LogicAgent (Together AI / Qwen Coder)")

        new_state: ReviewState = dict(state)
        cases = state.get("sandbox_results", [])
        all_issues: Dict[int, LogicIssue] = {}

        for batch in self.chunk_test_cases(cases):
            messages = self.generate_messages(state.get("code", ""), batch)

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.3,
                    max_output_tokens=2048,
                )

                model_text = response.choices[0].message.content
                parsed = safe_parse_json_response(model_text)
                for issue_data in parsed.get("logic_issues") or []:
                    issue = create_logic_issue(
                        issue=issue_data.get("issue", ""),
                        evidence=int(issue_data.get("evidence", -1)),
                        code_snippet=issue_data.get("code_snippet", ""),
                        location=issue_data.get("location"),
                    )
                    all_issues[issue["evidence"]] = issue

            except Exception as e:
                logger.error(f"LogicAgent batch error: {e}")

        new_state["logic_issues"] = all_issues

        logger.debug(f"LogicAgent output state: {new_state}")
        return new_state
