import logging
from typing import Dict

from openai import OpenAI

from app.models.review_link import ReviewLink, create_review_link
from app.models.review_state import LogicIssue, ReviewState
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
            if testcase_id in submission.get("failed_test_case_ids", []):
                matches.append(
                    {
                        "submission_index": index,
                        "code": submission.get("code", ""),
                    }
                )
        return matches

    def format_history_matches(self, history_matches: list[dict[str, str | int]]) -> str:
        return "\n\n".join(
            [
                (
                    f"Previous submission index: {match['submission_index']}\n"
                    f"Code:\n{match['code']}"
                )
                for match in history_matches
            ]
        )

    def generate_messages(
        self,
        current_code: str,
        batch_candidates: list[dict],
    ) -> list[dict[str, str]]:
        issues_text = "\n\n".join(
            [
                f"""Issue ref: {index}
Current issue summary: {candidate['current_issue']}
Current code snippet identified by the logic agent:
{candidate['current_code_snippet']}

Matching previous submissions for the same testcase:
{self.format_history_matches(candidate['history_matches'])}
"""
                for index, candidate in enumerate(batch_candidates)
            ]
        )
        return [
            {
                "role": "system",
                "content": (
                    "You are a CS1 progress-analysis agent. "
                    "Compare each current issue with previous submissions that failed the same testcase. "
                    "Use the current issue description and code snippet as anchors, then inspect the previous code "
                    "to identify what improved and what still needs work for each issue. "
                    "Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": f"""
Current student code:
{current_code}

Issues to compare:
{issues_text}

Task:
Compare each current issue with the previous submissions that failed the same testcase.
Focus on how the student's code changed around the relevant logic.

Return JSON in exactly this shape:
{{
  "review_links": [
    {{
      "issue_ref": 0,
      "previous_code_snippet": "snippet from a previous submission that best matches the current issue",
      "what_improved": "brief statement of what improved compared with the past attempt(s)",
      "what_still_needs_work": "brief statement of what still needs to be fixed",
      "relation_summary": "one concise sentence explaining the link between past and current attempts"
    }}
  ]
}}

Guidelines:
- Ground the comparison in the current issue and current code snippet.
- If improvement is minimal, say so clearly.
- Keep the language student-friendly.
- Return JSON only.
                """,
            },
        ]

    def build_fallback_review_link(
        self,
        issue: LogicIssue,
        history_matches: list[dict[str, str | int]],
    ) -> ReviewLink:
        current_snippet = issue.get("code_snippet", "").strip()
        previous_code = str(history_matches[-1]["code"]) if history_matches else ""
        previous_snippet = previous_code.strip()
        if len(previous_snippet) > 240:
            previous_snippet = f"{previous_snippet[:237]}..."

        what_improved = (
            "There is a visible code change since the earlier attempt, which suggests the student is iterating."
            if previous_code.strip()
            and previous_code.strip() != current_snippet.strip()
            else "The current attempt shows little clear progress around this testcase."
        )
        what_still_needs_work = (
            "The same testcase is still linked to a logic problem, so the underlying rule is not fully handled yet."
        )

        return create_review_link(
            current_issue=issue.get("issue", ""),
            current_code_snippet=current_snippet,
            previous_submission_indexes=[
                int(match["submission_index"]) for match in history_matches
            ],
            previous_code_snippet=previous_snippet,
            what_improved=what_improved,
            what_still_needs_work=what_still_needs_work,
            relation_summary=(
                "This issue matches a testcase that also failed in an earlier submission, "
                "so the student has revised the code but not fully resolved the same underlying problem."
            ),
        )

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
                    "current_code_snippet": issue.get("code_snippet", ""),
                    "history_matches": history_matches,
                }
            )

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
