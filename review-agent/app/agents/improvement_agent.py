from ast import List
import logging
from typing import Any, Dict
from openai import OpenAI

from app.models.review_state import ReviewState
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ImprovementAgent:
    """Analyzes code style and quality using a chat model."""

    def __init__(self, client: OpenAI, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate_messages(self, code: str) -> List[Dict[str, str]]:
        """
        Build the conversation messages, separating system and user roles.
        The model acts as a CS1 code-style coach.
        """

        system_msg = {
            "role": "system",
            "content": (
                "You are a CS1-level programming style and quality tutor. "
                "Your job is to analyze student code and provide feedback on code style, "
                "readability, and structure — but not logic or syntax errors. "
                "All responses must be in valid JSON format."
            ),
        }

        user_msg = {
            "role": "user",
            "content": f"""
                Analyze the student's code below and identify *style and quality* issues that might
                affect readability, maintainability, or performance, but do NOT affect correctness.

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
                            "fix_suggestion": "specific and actionable improvement suggestion",
                            "issue": "explain why this part needs improvement in simple terms",

                        }}
                    ]
                }}

                Guidelines:
                - Explain each issue in a way that a CS1 student can understand.
                - Focus on naming, commenting, modularity, duplication, and structure.
                - Avoid logic or syntax explanations.
                - Keep the tone supportive and educational.
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
                temperature=0.3,
                max_tokens=2048,
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
