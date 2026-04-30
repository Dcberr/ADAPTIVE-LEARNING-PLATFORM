import logging

from openai import OpenAI

from code_review_ai.models.review_link import ReviewLink, create_review_link
from code_review_ai.models.review_state import LogicIssue, ReviewState
from code_review_ai.prompts.review.review_link import build_review_link_messages
from code_review_ai.utils.code_diff import build_changed_line_summary
from code_review_ai.utils.debug_logging import summarize_state, truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.history_matcher import find_first_failed_history_match
from code_review_ai.utils.review_output_tools import parse_review_json_with_repair
from code_review_ai.utils.snippet_tools import extract_related_snippets

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
        previous_submission: dict[str, str],
    ) -> ReviewLink:
        previous_code = previous_submission.get("code", "")
        current_snippet = (
            issue.get("code_snippet", "").strip()
            or issue.get("anchor_snippet", "").strip()
        )
        comparison_mode = self._determine_comparison_mode(issue, previous_submission)
        previous_code_snippets = self._build_previous_code_snippets(issue, previous_code)
        changed_summary = build_changed_line_summary(
            previous_code=previous_code,
            current_code=issue.get("current_code_for_diff", "") or "",
        )

        what_improved = (
            "Recent code changes suggest the student is iterating on the same problem: "
            + "; ".join(changed_summary[:3])
            if changed_summary
            else "There is little clear improvement between this issue and the earlier failed submission."
        )
        what_still_needs_work = (
            "The same testcase failed before, so the underlying rule behind this issue still needs a clearer fix."
        )
        relation_summary = (
            "This issue is linked to the first earlier submission where the same testcase also failed."
        )

        return create_review_link(
            issue_evidence=issue.get("evidence", ""),
            previous_submission_id=previous_submission.get("submission_id", ""),
            previous_code_snippets=previous_code_snippets,
            comparison_mode=comparison_mode,
            what_improved=what_improved,
            what_still_needs_work=what_still_needs_work,
            relation_summary=relation_summary,
        )

    def _determine_comparison_mode(
        self,
        issue: LogicIssue,
        previous_submission: dict[str, str] | None,
    ) -> str:
        if previous_submission:
            if issue.get("history_status") == "persistent":
                return "persistent"
            return "historical_match"
        if issue.get("history_status") == "regression":
            return "regression"
        return "current_only"

    def _build_previous_code_snippets(
        self,
        issue: LogicIssue,
        previous_code: str,
    ) -> list[str]:
        if not previous_code.strip():
            return []

        snippets: list[str] = []
        anchors = [
            str(issue.get("code_snippet", "")).strip(),
            str(issue.get("anchor_snippet", "")).strip(),
        ]
        snippets = extract_related_snippets(
            code=previous_code,
            anchors=anchors,
            max_snippets=2,
            context_lines=1,
        )
        if snippets:
            return snippets

        trimmed = previous_code.strip()
        if len(trimmed) > 240:
            trimmed = f"{trimmed[:237]}..."
        return [trimmed]

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
            previous_submission = find_first_failed_history_match(
                new_state.get("history", []), testcase_id
            )
            if not previous_submission:
                continue

            issue_for_review_link = dict(issue)
            issue_for_review_link["current_code_for_diff"] = current_code

            candidates.append(
                {
                    "issue": issue_for_review_link,
                    "testcase_id": testcase_id,
                    "comparison_mode": self._determine_comparison_mode(
                        issue_for_review_link, previous_submission
                    ),
                    "previous_submission": previous_submission,
                    "current_code_snippet": (
                        issue_for_review_link.get("code_snippet", "")
                        or issue_for_review_link.get("anchor_snippet", "")
                    ),
                    "changed_summary": build_changed_line_summary(
                        previous_code=previous_submission.get("code", ""),
                        current_code=current_code,
                    ),
                }
            )

        if not candidates:
            new_state["review_links"] = []
            logger.debug(
                "ReviewLinkAgent skipped because no matching failed testcase history was found"
            )
            return new_state

        for batch_index, batch_candidates in enumerate(
            self.chunk_candidates(candidates), start=1
        ):
            try:
                messages = self.generate_messages(current_code, batch_candidates)
                response = create_chat_completion_with_retry(
                    self.client,
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
                parsed = parse_review_json_with_repair(
                    client=self.client,
                    model_name=self.model_name,
                    raw_response=model_text,
                    expected_shape={"review_links": list},
                )
                parsed_links = parsed.get("review_links") or []

                for candidate, parsed_link in zip(batch_candidates, parsed_links):
                    if not isinstance(parsed_link, dict):
                        parsed_link = None
                    if parsed_link is None:
                        review_links.append(
                            self.build_fallback_review_link(
                                candidate["issue"],
                                candidate["previous_submission"],
                            )
                        )
                        continue

                    parsed_previous_code_snippets = parsed_link.get(
                        "previous_code_snippets", []
                    )
                    if not isinstance(parsed_previous_code_snippets, list):
                        parsed_previous_code_snippets = []

                    review_links.append(
                        create_review_link(
                            issue_evidence=candidate["issue"].get("evidence", ""),
                            previous_submission_id=candidate[
                                "previous_submission"
                            ].get("submission_id", ""),
                            previous_code_snippets=[
                                snippet.strip()
                                for snippet in parsed_previous_code_snippets
                                if str(snippet).strip()
                            ]
                            or self._build_previous_code_snippets(
                                candidate["issue"],
                                candidate["previous_submission"].get("code", ""),
                            ),
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

                if len(parsed_links) < len(batch_candidates):
                    for candidate in batch_candidates[len(parsed_links) :]:
                        review_links.append(
                            self.build_fallback_review_link(
                                candidate["issue"],
                                candidate["previous_submission"],
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
                            candidate["previous_submission"],
                        )
                    )

        new_state["review_links"] = review_links
        logger.debug(
            "ReviewLinkAgent completed with %s review links",
            len(review_links),
        )
        return new_state
