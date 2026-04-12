from ast import List
import logging
from typing import Any, Dict
from openai import OpenAI

from app.models.review_state import ReviewState
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ImprovementAgent:
    """Analyzes clean-code and refactoring opportunities using a chat model."""

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

    def generate_messages(self, code: str) -> List[Dict[str, str]]:
        """
        Build the conversation messages, separating system and user roles.
        The model acts as a CS1 code-style coach.
        """

        system_msg = {
            "role": "system",
            "content": (
                "You are a CS1-level programming tutor focused on clean code and beginner-friendly refactoring. "
                "Your job is to analyze student code and provide educational warning feedback about readability, "
                "naming, structure, duplication, and simple refactoring opportunities, but not logic or syntax errors. "
                "All responses must be in valid JSON format."
            ),
        }

        user_msg = {
            "role": "user",
            "content": f"""
                Analyze the student's code below and identify *clean code and refactoring* warnings for a CS1 student.
                These warnings should help the student write clearer, easier-to-follow code even if the program already passes all test cases.

                CODE:
                {code}

                Return valid JSON with this structure:
                {{
                    "improvement_notes": [
                        {{
                            "location": {{
                                "start_line": line_number,
                                "end_line": line_number,
                                "start_col": column_number (optional),
                                "end_col": column_number (optional)
                            }},
                            "code_snippet": "exact code lines related to the issue",
                            "fix_suggestion": "specific and actionable clean-code or refactoring suggestion",
                            "issue": "explain in simple CS1 terms why this code should be cleaned up or refactored",

                        }}
                    ]
                }}

                Guidelines:
                - Explain each warning in a way that a CS1 student can understand.
                - Focus on clean code topics such as naming, readability, duplication, simple function extraction, structure, and unused or noisy code.
                - Good warnings include things like: variable names are unclear, code is repetitive, one block should be extracted into a function, formatting makes the code harder to read, or structure can be simplified for learning clarity.
                - Do NOT talk about hidden test cases, edge cases, possible future bugs, or speculative failures.
                - Do NOT repeat logic or syntax errors that belong to other review items.
                - If the code is already correct, still give clean-code warnings when there are beginner-friendly refactoring opportunities.
                - Keep the tone supportive, practical, and educational.
                - Return an empty list only if the code is already very clean for a CS1 student.
                """,
        }

        return [system_msg, user_msg]

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        """Run style/quality analysis and update the review state."""
        logger.debug(
            "Starting ImprovementAgent with state summary: %s",
            summarize_state(state),
        )

        new_state: ReviewState = dict(state)
        code = state["code"]

        try:
            messages = self.generate_messages(code)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            model_text = response.choices[0].message.content
            logger.debug(
                "ImprovementAgent raw response preview: %s",
                truncate_text(model_text),
            )
            parsed = safe_parse_json_response(model_text)

            new_state["improvement_notes"] = parsed.get("improvement_notes", [])
            logger.debug(
                "ImprovementAgent parsed %s improvement notes",
                len(new_state["improvement_notes"]),
            )

        except Exception as e:
            logger.exception("ImprovementAgent failed")
            new_state["improvement_notes"] = []

        logger.debug(
            "ImprovementAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
