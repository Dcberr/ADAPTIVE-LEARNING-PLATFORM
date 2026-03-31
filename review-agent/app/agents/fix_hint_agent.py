import logging
from typing import Dict

from app.models.review_state import LogicIssue, ReviewState
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class FixHintAgent:
    """Generates fix suggestions for each relevant concept in CS1 submissions with assignment context."""

    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate_messages(
        self, issue: LogicIssue, assignment: str
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

                CODE SNIPPET (from student's submission):
                {issue.get('code_snippet', '')}

                PROBLEM SUMMARY:
                {issue.get('issue', '')}

                RELATED CS1 CONCEPTS (relevant only):
                {issue.get('relevant_concept', [])}

                EVIDENCE: Test case ID {issue.get('evidence')}

                TASK:
                Based on the above information, generate a JSON object with a clear fix hint
                that explains what might be wrong conceptually and what steps the student
                should take to fix it.

                Output must be valid JSON:
                {{
                    "fix_suggestion": "your suggestion here"
                }}
                            """,
        }

        return [system_message, user_message]

    def analyze(self, state: ReviewState) -> ReviewState:
        """Generate fix suggestions for all relevant logic issues."""
        logger.debug("Starting FixHintAgent with separated system/user messages")

        new_state: ReviewState = dict(state)
        logic_issues: Dict[int, LogicIssue] = new_state.get("logic_issues", {})
        assignment = new_state.get("assignment", "No assignment description provided.")

        for issue_id, issue in logic_issues.items():
            if not issue.get("relevant_concept"):
                continue  # Skip if no relevant concept

            messages = self.generate_messages(issue, assignment)

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.4,
                    max_output_tokens=512,
                )

                model_text = response.choices[0].message.content
                parsed = safe_parse_json_response(model_text)

                issue["fix_suggestion"] = (
                    parsed.get("fix_suggestion", "").strip()
                    or "No fix suggestion generated."
                )
                logic_issues[issue_id] = issue

            except Exception as e:
                logger.error(f"FixHintAgent error for issue {issue_id}: {e}")
                issue["fix_suggestion"] = "Error generating fix suggestion."
                logic_issues[issue_id] = issue

        new_state["logic_issues"] = logic_issues
        logger.debug(f"FixHintAgent output state: {new_state}")
        return new_state
