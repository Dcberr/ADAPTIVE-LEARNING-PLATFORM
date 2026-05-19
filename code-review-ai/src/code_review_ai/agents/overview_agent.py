from ast import List
import logging
from time import perf_counter
from typing import Any

from code_review_ai.api.review_code_schema import ReviewItem
from code_review_ai.models.review_state import ReviewState
from code_review_ai.prompts.review.overview import build_overview_messages
from code_review_ai.utils.debug_logging import summarize_state, truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry

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
                    if link.get("issue_evidence") == issue.get("evidence", "")
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
            messages = build_overview_messages(new_state)
            prompt_text = "\n\n".join(
                str(message.get("content", "")) for message in messages
            )
            logger.debug(
                "OverviewAgent request summary: model=%s logic_issues=%s improvement_notes=%s review_items=%s prompt_chars=%s prompt_lines=%s",
                self.model_name,
                len(new_state.get("logic_issues", {})),
                len(new_state.get("improvement_notes", [])),
                len(review_items),
                len(prompt_text),
                len(prompt_text.splitlines()),
            )
            request_started_at = perf_counter()
            response = create_chat_completion_with_retry(
                self.client,
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            request_elapsed_ms = (perf_counter() - request_started_at) * 1000
            overview_text = self._sanitize_overview_text(
                response.choices[0].message.content
            )
            if not overview_text:
                overview_text = self._build_fallback_overview(new_state)
            new_state["overview"] = overview_text
            logger.debug(
                "OverviewAgent response summary: model=%s duration_ms=%.2f overview_chars=%s preview=%s",
                self.model_name,
                request_elapsed_ms,
                len(overview_text),
                truncate_text(overview_text),
            )
        except Exception:
            logger.exception(
                "OverviewAgent failed for model=%s; using deterministic fallback",
                self.model_name,
            )
            new_state["overview"] = self._build_fallback_overview(new_state)

        logger.debug(
            "OverviewAgent completed with state summary: %s",
            summarize_state(new_state),
        )
        return new_state

    @staticmethod
    def _sanitize_overview_text(content: str | None) -> str:
        text = (content or "").strip()
        if not text:
            return ""

        lowered_text = text.lower()
        blocked_phrases = (
            "the user wants",
            "analyze the request",
            "analysis of the request",
            "key constraints",
            "the prompt says",
            "system prompt",
            "hidden instructions",
            "internal rules",
            "i should",
            "i need to",
            "let me",
            "role:",
            "tone:",
            "constraints:",
            "output:",
        )
        if any(phrase in lowered_text for phrase in blocked_phrases):
            return ""

        blocked_prefixes = (
            "you are ",
            "instructions:",
            "current review findings:",
            "logic issues:",
            "improvement notes:",
            "system prompt",
            "1.",
            "2.",
            "3.",
        )
        kept_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
            and not line.strip().lower().startswith(blocked_prefixes)
            and not line.strip().startswith("- ")
        ]
        cleaned = " ".join(kept_lines).strip()
        if not cleaned:
            cleaned = text

        return cleaned

    @staticmethod
    def _build_fallback_overview(state: ReviewState) -> str:
        logic_issues = list(state.get("logic_issues", {}).values())
        improvement_notes = list(state.get("improvement_notes", []))

        if logic_issues:
            main_issue = OverviewAgent._extract_summary_text(logic_issues[0])
            parts = [f"Your program still has a main logic problem: {main_issue}."]
            if improvement_notes:
                improvement = OverviewAgent._extract_summary_text(improvement_notes[0])
                parts.append(
                    f"After fixing that, also improve this part of the code: {improvement}."
                )
            return " ".join(parts)

        if improvement_notes:
            improvement = OverviewAgent._extract_summary_text(improvement_notes[0])
            return (
                f"Your solution is close, but there is still an important improvement to make: {improvement}."
            )

        return "No major issues were detected in this submission."

    @staticmethod
    def _extract_summary_text(item: Any) -> str:
        issue_text = str(item.get("issue", "")).strip() if isinstance(item, dict) else ""
        fix_text = (
            str(item.get("fix_suggestion", "")).strip() if isinstance(item, dict) else ""
        )
        text = issue_text or fix_text or "please review the current submission"
        return text.rstrip(".")
