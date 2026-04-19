import logging
from typing import Dict

from openai import OpenAI

from app.models.review_link import ReviewLink, create_review_link
from app.models.review_state import LogicIssue, ReviewState
from app.prompts.review.review_link import build_review_link_messages
from app.utils.debug_logging import summarize_state, truncate_text
from app.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class ReviewLinkAgent:
    """Links current issues to earlier attempts for the same testcase."""

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        batch_size: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ):
        self.client = client
        self.model_name = model_name
        self.batch_size = batch_size
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chunk_candidates(self, candidates: list[dict]):
        for i in range(0, len(candidates), self.batch_size):
            yield candidates[i : i + self.batch_size]

    def find_matching_history(
        self, state: ReviewState, testcase_id: str
    ) -> list[dict[str, str | int]]:
        matches: list[dict[str, str | int]] = []
        for index, submission in enumerate(state.get("history", []), start=1):
            testcase_status = ""
            if testcase_id in submission.get("failed_test_case_ids", []):
                testcase_status = "failed"
            elif testcase_id in submission.get("passed_test_case_ids", []):
                testcase_status = "passed"
            if not testcase_status:
                continue
            matches.append(
                {
                    "submission_index": index,
                    "testcase_status": testcase_status,
                    "code": submission.get("code", ""),
                }
            )
        return matches

    def generate_messages(
        self,
        current_code: str,
        batch_candidates: list[dict],
    ) -> list[dict[str, str]]:
        return build_review_link_messages(
            current_code=current_code,
            batch_candidates=batch_candidates,
        )

    def build_fallback_review_link(
        self,
        issue: LogicIssue,
        history_matches: list[dict[str, str | int]],
    ) -> ReviewLink:
        current_snippet = (
            issue.get("code_snippet", "").strip()
            or issue.get("anchor_snippet", "").strip()
        )
        latest_match = history_matches[0] if history_matches else None
        previous_code = str(latest_match["code"]) if latest_match else ""
        previous_snippet = previous_code.strip()
        if len(previous_snippet) > 240:
            previous_snippet = f"{previous_snippet[:237]}..."

        comparison_mode = self._determine_comparison_mode(issue, history_matches)
        if comparison_mode == "regression":
            what_improved = "The student previously had this testcase working, but the latest code change broke that behavior."
            what_still_needs_work = (
                "Find the recent change that turned a previously passing case into a failing one and restore that rule without breaking the newer logic."
            )
            relation_summary = (
                "This testcase passed in a recent history entry but fails now, so the current submission introduced a regression."
            )
        elif comparison_mode == "persistent":
            what_improved = (
                "There is a visible code change since the earlier failed attempt, which suggests the student is iterating."
                if previous_code.strip()
                and previous_code.strip() != current_snippet.strip()
                else "The current attempt shows little clear progress around this testcase."
            )
            what_still_needs_work = (
                "The same testcase is still linked to a logic problem, so the underlying rule is not fully handled yet."
            )
            relation_summary = (
                "This testcase also failed in a recent history entry, so the student has revised the code but not fully resolved the same underlying problem."
            )
        else:
            what_improved = "There is not enough matching testcase history to describe a clear improvement trend."
            what_still_needs_work = (
                "Focus on fixing the current logic issue first, then compare the next attempt with this one."
            )
            relation_summary = (
                "This issue appears only in the current attempt or does not have enough earlier testcase history for a stronger comparison."
            )

        return create_review_link(
            current_issue=issue.get("issue", ""),
            current_code_snippet=current_snippet,
            previous_submission_indexes=[
                int(match["submission_index"]) for match in history_matches
            ],
            previous_code_snippet=previous_snippet,
            comparison_mode=comparison_mode,
            what_improved=what_improved,
            what_still_needs_work=what_still_needs_work,
            relation_summary=relation_summary,
        )

    def _determine_comparison_mode(
        self,
        issue: LogicIssue,
        history_matches: list[dict[str, str | int]],
    ) -> str:
        if issue.get("history_status") == "regression":
            return "regression"
        if history_matches and history_matches[0].get("testcase_status") == "failed":
            return "persistent"
        return "current_only"

    def analyze(self, state: ReviewState) -> ReviewState:
        logger.debug(
            "Starting ReviewLinkAgent with state summary: %s",
            summarize_state(state),
        )
        new_state: ReviewState = dict(state)
        review_links: list[ReviewLink] = []
        current_code = new_state.get("code", "")
        candidates: list[dict] = []

        for issue in new_state.get("logic_issues", {}).values():
            testcase_id = issue.get("evidence", "")
            history_matches = self.find_matching_history(new_state, testcase_id)
            if not history_matches:
                continue

            candidates.append(
                {
                    "issue": issue,
                    "testcase_id": testcase_id,
                    "current_issue": issue.get("issue", ""),
                    "current_code_snippet": (
                        issue.get("code_snippet", "")
                        or issue.get("anchor_snippet", "")
                    ),
                    "comparison_mode": self._determine_comparison_mode(
                        issue, history_matches
                    ),
                    "history_matches": history_matches,
                }
            )

        if not candidates:
            new_state["review_links"] = []
            logger.debug(
                "ReviewLinkAgent skipped because no matching testcase history was found"
            )
            return new_state

        for batch_index, batch_candidates in enumerate(
            self.chunk_candidates(candidates), start=1
        ):
            try:
                messages = self.generate_messages(current_code, batch_candidates)
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                model_text = response.choices[0].message.content
                logger.debug(
                    "ReviewLinkAgent batch %s raw response preview: %s",
                    batch_index,
                    truncate_text(model_text),
                )
                parsed = safe_parse_json_response(model_text)
                parsed_links = parsed.get("review_links") or []
                links_by_ref: Dict[int, dict] = {
                    item.get("issue_ref"): item
                    for item in parsed_links
                    if isinstance(item.get("issue_ref"), int)
                }

                for issue_ref, candidate in enumerate(batch_candidates):
                    parsed_link = links_by_ref.get(issue_ref)
                    if parsed_link is None:
                        review_links.append(
                            self.build_fallback_review_link(
                                candidate["issue"],
                                candidate["history_matches"],
                            )
                        )
                        continue

                    review_links.append(
                        create_review_link(
                            current_issue=candidate["current_issue"],
                            current_code_snippet=candidate["current_code_snippet"],
                            previous_submission_indexes=[
                                int(match["submission_index"])
                                for match in candidate["history_matches"]
                            ],
                            previous_code_snippet=str(
                                parsed_link.get("previous_code_snippet", "")
                            ).strip(),
                            comparison_mode=str(
                                parsed_link.get(
                                    "comparison_mode",
                                    candidate["comparison_mode"],
                                )
                            ).strip()
                            or candidate["comparison_mode"],
                            what_improved=str(
                                parsed_link.get("what_improved", "")
                            ).strip(),
                            what_still_needs_work=str(
                                parsed_link.get("what_still_needs_work", "")
                            ).strip(),
                            relation_summary=str(
                                parsed_link.get("relation_summary", "")
                            ).strip(),
                        )
                    )
            except Exception:
                logger.exception(
                    "ReviewLinkAgent batch %s failed",
                    batch_index,
                )
                for candidate in batch_candidates:
                    review_links.append(
                        self.build_fallback_review_link(
                            candidate["issue"],
                            candidate["history_matches"],
                        )
                    )

        new_state["review_links"] = review_links
        logger.debug(
            "ReviewLinkAgent completed with %s review links",
            len(review_links),
        )
        return new_state
