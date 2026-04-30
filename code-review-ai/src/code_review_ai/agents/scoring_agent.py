import logging
from typing import Any, Dict

from openai import OpenAI

from code_review_ai.models.review_state import ReviewState
from code_review_ai.prompts.review.scoring import build_scoring_messages
from code_review_ai.utils.debug_logging import summarize_state, truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.review_output_tools import parse_review_json_with_repair

logger = logging.getLogger(__name__)


class ScoringAgent:
    """Scores higher-level learning signals from code, history, and review output."""

    SCORECARD_TEMPLATE = {
        "problem_solving_creativity": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence in the current code and review data to judge the student's creativity in problem solving.",
        },
        "logic_traceability": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to explain how consistently the student's code reflects a traceable line of reasoning.",
        },
        "generalization_score": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to determine whether the student's solution generalizes beyond the observed cases.",
        },
        "construct_appropriateness": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to judge whether the student selected appropriate programming constructs for the task.",
        },
        "self_correction_path": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough history evidence to explain how effectively the student is correcting mistakes across attempts.",
        },
        "variable_understanding": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to assess the student's understanding of how variables should store and change values.",
        },
        "control_flow_understanding": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to assess the student's understanding of conditions, branching, or execution flow.",
        },
        "input_output_awareness": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to assess how well the student understands input handling and expected output behavior.",
        },
        "edge_case_awareness": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to determine whether the student anticipates edge cases or unusual inputs.",
        },
        "debugging_readiness": {
            "score": 1,
            "label": "Insufficient Evidence",
            "explanation": "There is not enough clear evidence to assess how prepared the student is to debug systematically.",
        },
    }

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.2,
        max_tokens: int = 1400,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @staticmethod
    def _normalize_score(raw_score: Any, default: int) -> int:
        try:
            return max(1, min(5, int(raw_score)))
        except (TypeError, ValueError):
            return default

    def generate_messages(self, state: ReviewState) -> list[Dict[str, str]]:
        return build_scoring_messages(state)

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        logger.debug(
            "Starting ScoringAgent with state summary: %s",
            summarize_state(state),
        )

        new_state: ReviewState = dict(state)

        try:
            messages = self.generate_messages(new_state)
            response = create_chat_completion_with_retry(
                self.client,
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            model_text = response.choices[0].message.content
            logger.debug(
                "ScoringAgent raw response preview: %s",
                truncate_text(model_text),
            )
            parsed = parse_review_json_with_repair(
                client=self.client,
                model_name=self.model_name,
                raw_response=model_text,
                expected_shape={"scorecard": dict},
            )
            scorecard = parsed.get("scorecard") or {}
            normalized_scorecard = {
                key: {
                    "score": self._normalize_score(
                        scorecard.get(key, {}).get("score", template["score"]),
                        template["score"],
                    ),
                    "label": (
                        str(scorecard.get(key, {}).get("label", "")).strip()
                        or template["label"]
                    ),
                    "explanation": (
                        str(scorecard.get(key, {}).get("explanation", "")).strip()
                        or template["explanation"]
                    ),
                }
                for key, template in self.SCORECARD_TEMPLATE.items()
            }
            new_state["scorecard"] = normalized_scorecard
            logger.debug(
                "ScoringAgent parsed fixed scorecard with %s metrics",
                len(new_state["scorecard"]),
            )
        except Exception:
            logger.exception("ScoringAgent failed")
            new_state["scorecard"] = self.SCORECARD_TEMPLATE.copy()

        logger.debug(
            "ScoringAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
