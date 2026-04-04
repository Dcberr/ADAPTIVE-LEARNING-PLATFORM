from ast import List
import logging

from app.api.review_code_schema import ReviewItem
from app.models.review_state import ReviewState
from app.utils.debug_logging import summarize_state, truncate_text

logger = logging.getLogger(__name__)


class OverviewAgent:
    """Aggregates logic issues and improvement notes into a unified review and generates overview."""

    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def generate_prompt(self, state: ReviewState) -> str:
        """
        Teacher-style prompt: produce a concise, student-friendly overview of
        all errors and warnings in the submission.
        """
        return f"""
You are a CS1 teacher reviewing a student's code submission. Summarize the review concisely
and in beginner-friendly language. Focus on helping the student understand:

1. Functional errors (logic issues)
2. Style/quality warnings (improvement notes)
3. How to improve their code step by step

Student code:
{state['code']}

Logic issues (Errors):
{list(state.get('logic_issues', {}).values())}

Improvement notes (Warnings):
{state.get('improvement_notes', [])}

Instructions:
- Generate a clear overview paragraph that a CS1 student can easily understand.
- Highlight the most important errors first, then warnings.
- Keep it concise and actionable.
- Output ONLY the overview text.
"""

    def analyze(self, state: ReviewState) -> ReviewState:
        """Merge logic issues and improvement notes into review_items and generate overview."""

        logger.debug("Starting OverviewAgent with state summary: %s", summarize_state(state))
        new_state: ReviewState = dict(state)
        review_items: List[ReviewItem] = []

        # Merge logic issues as Errors
        for issue in new_state.get("logic_issues", {}).values():
            review_items.append(
                {
                    "type": "Error",
                    "location": issue["location"],
                    "code_snippet": issue.get("code_snippet", ""),
                    "fix_suggestion": issue.get("fix_suggestion", ""),
                    "issue": issue.get("issue", ""),
                    "relevant_concept": issue.get("relevant_concept", []),
                }
            )

        # Merge improvement notes as Warnings
        for note in new_state.get("improvement_notes", []):
            review_items.append(
                {
                    "type": "Warning",
                    "location": note.get("location", {"start_line": 1, "end_line": 1}),
                    "code_snippet": note.get("code_snippet", ""),
                    "fix_suggestion": note.get("fix_suggestion", ""),
                    "issue": note.get("issue", ""),
                    "relevant_concept": [],
                }
            )

        new_state["review_items"] = review_items
        logger.debug("OverviewAgent prepared %s review items", len(review_items))

        # Generate teacher-style overview using prompt
        try:
            prompt = self.generate_prompt(new_state)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful CS1 teacher."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            overview_text = response.choices[0].message.content.strip()
            new_state["overview"] = overview_text
            logger.debug(
                "OverviewAgent generated overview preview: %s",
                truncate_text(overview_text),
            )
        except Exception as e:
            logger.exception("OverviewAgent failed")
            new_state["overview"] = "Unable to generate overview at this time."

        logger.debug(
            "OverviewAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state
