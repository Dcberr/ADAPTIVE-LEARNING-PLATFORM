from ast import List
import logging

from app.api.review_code_schema import ReviewItem
from app.models.review_state import ReviewState
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

    def format_history(self, state: ReviewState) -> str:
        """Format prior submission attempts for the overview prompt."""
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

    def format_progress_summary(self, state: ReviewState) -> str:
        """Format history-based progress signals for the overview prompt."""
        previous_failed = state.get("previous_failed_test_case_ids", [])
        persistent_failed = state.get("persistent_failed_test_case_ids", [])
        fixed_testcases = state.get("fixed_test_case_ids", [])
        regressed_testcases = state.get("regressed_test_case_ids", [])

        return (
            f"First history failed testcase IDs: {previous_failed}\n"
            f"Persistent failed testcase IDs: {persistent_failed}\n"
            f"Fixed testcase IDs since the first history entry: {fixed_testcases}\n"
            f"Newly failing testcase IDs since the first history entry: {regressed_testcases}"
        )

    def generate_prompt(self, state: ReviewState) -> str:
        """
        Teacher-style prompt: produce a concise, student-friendly overview of
        all errors and warnings in the submission.
        """
        history_text = self.format_history(state)
        progress_summary = self.format_progress_summary(state)
        return f"""
You are a CS1 teacher reviewing a student's code submission. Summarize the review concisely
and in beginner-friendly language. Base your overview on both the current submission and the
submission history. Focus on helping the student understand:

1. Functional errors (logic issues)
2. Style/quality warnings (improvement notes)
3. What improved from earlier submissions, if there is meaningful progress
4. How to improve their code step by step

Current student code:
{state['code']}

Submission history:
{history_text}

History-based progress summary:
{progress_summary}

Logic issues (Errors):
{list(state.get('logic_issues', {}).values())}

Review links to earlier attempts for the same testcase:
{state.get('review_links', [])}

Improvement notes (Warnings):
{state.get('improvement_notes', [])}

Instructions:
- Generate a clear overview paragraph that a CS1 student can easily understand.
- Highlight the most important errors first, then warnings.
- If history is available, briefly mention meaningful improvement from previous submissions.
- Mention whether the student fixed earlier failures, still has persistent failures, or introduced newly failing cases when that is supported by the data.
- Keep it concise and actionable.
- Output ONLY the overview text.
"""

    def analyze(self, state: ReviewState) -> ReviewState:
        """Merge logic issues and improvement notes into review_items and generate overview."""

        logger.debug("Starting OverviewAgent with state summary: %s", summarize_state(state))
        new_state: ReviewState = dict(state)
        review_items: List[ReviewItem] = []
        review_links = list(new_state.get("review_links", []))

        # Merge logic issues as Errors
        for issue in new_state.get("logic_issues", {}).values():
            matched_review_link = next(
                (
                    link
                    for link in review_links
                    if link.get("current_issue") == issue.get("issue", "")
                    and link.get("current_code_snippet")
                    == issue.get("code_snippet", "")
                ),
                None,
            )
            review_items.append(
                {
                    "type": "Error",
                    "location": issue["location"],
                    "code_snippet": issue.get("code_snippet", ""),
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
            prompt = self.generate_prompt(new_state)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful CS1 teacher."},
                    {"role": "user", "content": prompt},
                ],
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
