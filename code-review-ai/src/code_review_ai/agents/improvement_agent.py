from ast import List
import logging
from typing import Any, Dict
from openai import OpenAI

from code_review_ai.prompts.review.improvement import build_improvement_messages
from code_review_ai.models.review_state import ReviewState
from code_review_ai.utils.code_context import build_improvement_code_context
from code_review_ai.utils.debug_logging import summarize_state, truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.review_output_tools import parse_review_json_with_repair

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
        return build_improvement_messages(
            build_improvement_code_context(code=code)
        )

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

            response = create_chat_completion_with_retry(
                self.client,
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
            parsed = parse_review_json_with_repair(
                client=self.client,
                model_name=self.model_name,
                raw_response=model_text,
                expected_shape={"improvement_notes": list},
            )

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
