import logging
from typing import Any, Dict

from openai import OpenAI

from app.models.review_state import ReviewState
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

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

    def __init__(self, client: OpenAI, model_name: str):
        self.client = client
        self.model_name = model_name

    @staticmethod
    def _normalize_score(raw_score: Any, default: int) -> int:
        try:
            return max(1, min(5, int(raw_score)))
        except (TypeError, ValueError):
            return default

    def format_history(self, state: ReviewState) -> str:
        history = state.get("history", [])
        if not history:
            return "No previous submissions."

        return "\n\n".join(
            [
                (
                    f"Previous submission {index}:\n"
                    f"Failed testcase IDs: {submission.get('failed_test_case_ids', [])}\n"
                    f"Code:\n{submission.get('code', '')}"
                )
                for index, submission in enumerate(history, start=1)
            ]
        )

    def generate_messages(self, state: ReviewState) -> list[Dict[str, str]]:
        progress_summary = (
            f"Persistent failed testcase IDs: {state.get('persistent_failed_test_case_ids', [])}\n"
            f"Fixed testcase IDs since first history entry: {state.get('fixed_test_case_ids', [])}\n"
            f"Newly failing testcase IDs since first history entry: {state.get('regressed_test_case_ids', [])}"
        )

        system_msg = {
            "role": "system",
            "content": (
                "You are an educational assessment agent for CS1 submissions. "
                "Score learning signals based on the student's current code, "
                "submission history, and review findings. "
                "Return valid JSON only."
            ),
        }

        user_msg = {
            "role": "user",
            "content": f"""
Current student code:
{state.get('code', '')}

Submission history:
{self.format_history(state)}

Review overview:
{state.get('overview', '')}

Logic issues:
{list(state.get('logic_issues', {}).values())}

Improvement notes:
{state.get('improvement_notes', [])}

History-based progress summary:
{progress_summary}

Score these ten indices:
1. Problem-Solving Creativity
2. Logic Traceability
3. Generalization Score
4. Construct Appropriateness
5. Self-Correction Path
6. Variable Understanding
7. Control Flow Understanding
8. Input/Output Awareness
9. Edge Case Awareness
10. Debugging Readiness

For each index:
- assign a score from 1 to 5
- provide a short label
- provide a concise explanation grounded in the code/history/review

Return JSON in exactly this shape:
{{
  "scorecard": {{
    "problem_solving_creativity": {{
      "score": 1,
      "label": "Rote Memorization",
      "explanation": "short grounded explanation"
    }},
    "logic_traceability": {{
      "score": 1,
      "label": "Chaotic",
      "explanation": "short grounded explanation"
    }},
    "generalization_score": {{
      "score": 1,
      "label": "Hard-coded",
      "explanation": "short grounded explanation"
    }},
    "construct_appropriateness": {{
      "score": 1,
      "label": "Poor Tool Choice",
      "explanation": "short grounded explanation"
    }},
    "self_correction_path": {{
      "score": 1,
      "label": "Random Changes",
      "explanation": "short grounded explanation"
    }},
    "variable_understanding": {{
      "score": 1,
      "label": "Treats Values as Fixed",
      "explanation": "short grounded explanation"
    }},
    "control_flow_understanding": {{
      "score": 1,
      "label": "Confused Flow",
      "explanation": "short grounded explanation"
    }},
    "input_output_awareness": {{
      "score": 1,
      "label": "I/O Mismatch",
      "explanation": "short grounded explanation"
    }},
    "edge_case_awareness": {{
      "score": 1,
      "label": "Happy-Path Only",
      "explanation": "short grounded explanation"
    }},
    "debugging_readiness": {{
      "score": 1,
      "label": "Needs Debugging Support",
      "explanation": "short grounded explanation"
    }}
  }}
}}

Scoring guidance:
- 1 means very weak evidence
- 3 means mixed or moderate evidence
- 5 means strong evidence
- Ground every score in observable signals from the code or history.
- For Self-Correction Path, use history heavily.
- For beginner-focused indices, favor concrete evidence about variables, control flow, input/output handling, edge cases, and how the student responds to failed attempts.
- Return JSON only.
            """,
        }

        return [system_msg, user_msg]

    def analyze(self, state: ReviewState) -> Dict[str, Any]:
        logger.debug(
            "Starting ScoringAgent with state summary: %s",
            summarize_state(state),
        )

        new_state: ReviewState = dict(state)

        try:
            messages = self.generate_messages(new_state)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=1400,
            )

            model_text = response.choices[0].message.content
            logger.debug(
                "ScoringAgent raw response preview: %s",
                truncate_text(model_text),
            )
            parsed = safe_parse_json_response(model_text)
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
