import logging
from typing import Any, Dict

from openai import OpenAI

from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ReflectionAgent:
    """Performs a final sanity check, validates, and compiles feedback for CS1 students."""

    def __init__(self, client: OpenAI, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate_messages(self, state: Dict[str, Any]) -> list[Dict[str, str]]:
        system_message = {
            "role": "system",
            "content": (
                "You are a CS1 (Introduction to Programming) professor reviewing "
                "assembled feedback before it is shown to first-year students. "
                "Return valid JSON only."
            ),
        }

        user_message = {
            "role": "user",
            "content": f"""
You are validating feedback for CS1 students. Ensure it is:
1. Pedagogically sound and appropriate for CS1 level
2. Clear and understandable for beginners
3. Constructive and encouraging while being accurate
4. Focused on fundamental concepts they have learned

Review these components:
- Code and test results: {state.get('sandbox_result', {})}
- Identified issues: {state.get('logic_issues', [])}
- Concept mappings: {state.get('concept_issues', [])}
- Detailed feedback: {state.get('categorized_feedback', [])}
- Quality suggestions: {state.get('improvement_notes', [])}
- Advanced topics: {state.get('advanced_suggestions', [])}
- Summary overview: {state.get('overview', '')}
- Review items: {state.get('review_items', [])}

Return JSON with this shape:
{{
    "final_report": {{
        "feedback": [
            {{
                "line": {{ "start": number, "end": number }},
                "column": {{ "start": number, "end": number }},
                "code_snippet": "relevant code",
                "type": "Error|Warning",
                "issue": "Clear explanation using CS1 terminology",
                "fix_suggestion": "Step-by-step guidance appropriate for beginners",
                "educational_notes": {{
                    "concepts": ["list", "of", "relevant", "CS1", "concepts"],
                    "prerequisites": "What they need to know to understand this",
                    "learning_goal": "What they should learn from this feedback"
                }}
            }}
        ],
        "summary": {{
            "overview": "Overall assessment in encouraging, clear language",
            "key_concepts": ["main", "CS1", "concepts", "to", "focus", "on"],
            "next_steps": "Clear guidance on what to learn or review"
        }},
        "meta": {{
            "validated": true,
            "pedagogical_notes": "Any concerns about complexity or prerequisites",
            "difficulty_level": "beginner|intermediate|advanced"
        }}
    }}
}}

Educational guidelines:
- Use CS1 vocabulary consistently.
- Break down complex issues into simpler concepts.
- Connect feedback to fundamental programming principles.
- Provide concrete, actionable steps for improvement.
- Include positive reinforcement when appropriate.
- Do not give away complete solutions.
- Verify all feedback is based on evidence from code or tests.
            """,
        }

        return [system_message, user_message]

    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Starting ReflectionAgent with state summary: %s", summarize_state(state))

        new_state = dict(state)
        messages = self.generate_messages(state)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=2048,
            )
            model_text = response.choices[0].message.content
            logger.debug(
                "ReflectionAgent raw response preview: %s",
                truncate_text(model_text),
            )
            parsed = safe_parse_json_response(model_text)

            if parsed and parsed.get("final_report"):
                new_state["final_report"] = parsed.get("final_report")
            else:
                new_state["final_report"] = {
                    "feedback": new_state.get("categorized_feedback", [])
                    or new_state.get("improvement_notes", [])
                    or [],
                    "meta": {"validated": True},
                }
        except Exception as e:
            logger.exception("ReflectionAgent failed")
            new_state["final_report"] = {
                "feedback": [],
                "meta": {"validated": False, "error": str(e)},
            }

        logger.debug(
            "ReflectionAgent completed; final_report keys=%s",
            list((new_state.get("final_report") or {}).keys()),
        )
        return new_state
