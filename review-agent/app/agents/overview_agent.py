from ast import List
import logging

from app.api.review_code_schema import ReviewItem
from app.models.review_state import ReviewState
from app.prompts.review.overview import build_overview_messages
from app.utils.debug_logging import summarize_state, truncate_text

logger = logging.getLogger(__name__)


class OverviewAgent:
    """Aggregates logic issues and improvement notes into a unified review and generates overview."""

    def __init__(
        self,
        client,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def analyze(self, state: ReviewState) -> ReviewState:
        """Merge logic issues and improvement notes into review_items and generate overview."""

        logger.debug("Starting OverviewAgent with state summary: %s", summarize_state(state))
        new_state: ReviewState = dict(state)
        review_items: List[ReviewItem] = []
        review_links = list(new_state.get("review_links", []))

        # Merge logic issues as Errors
        for issue in new_state.get("logic_issues", {}).values():
            display_snippet = issue.get("code_snippet", "") or issue.get(
                "anchor_snippet", ""
            )
            matched_review_link = next(
                (
                    link
                    for link in review_links
                    if link.get("current_issue") == issue.get("issue", "")
                    and link.get("current_code_snippet")
                    == display_snippet
                ),
                None,
            )
            review_items.append(
                {
                    "type": "Error",
                    "location": issue["location"],
                    "code_snippet": display_snippet,
                    "fix_suggestion": issue.get("fix_suggestion", ""),
                    "issue": issue.get("issue", ""),
                    "review_link": matched_review_link,
                    "history_status": issue.get("history_status", ""),
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
                    "review_link": None,
                }
            )

        new_state["review_items"] = review_items
        logger.debug("OverviewAgent prepared %s review items", len(review_items))

        # Generate teacher-style overview using prompt
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=build_overview_messages(new_state),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
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
