from __future__ import annotations

from code_review_ai.models.review_state import ReviewState
from code_review_ai.utils.history_matcher import summarize_history_progress
from code_review_ai.utils.snippet_tools import compress_text


def build_scoring_context_summary(state: ReviewState) -> dict[str, str]:
    logic_issue_lines = []
    for issue in list(state.get("logic_issues", {}).values())[:6]:
        logic_issue_lines.append(
            "- "
            + compress_text(
                f"{issue.get('evidence', '')}: {issue.get('issue', '')} | "
                f"cause_type={issue.get('cause_type', '')} | "
                f"history_status={issue.get('history_status', '')}",
                max_chars=240,
            )
        )

    improvement_lines = [
        "- " + compress_text(str(note), max_chars=220)
        for note in list(state.get("improvement_notes", []))[:5]
    ]
    review_link_lines = [
        "- "
        + compress_text(
            f"{link.get('comparison_mode', '')}: {link.get('relation_summary', '')}",
            max_chars=220,
        )
        for link in list(state.get("review_links", []))[:5]
    ]

    return {
        "current_code": compress_text(state.get("code", ""), max_chars=1400),
        "history": _format_history_summary(state),
        "overview": compress_text(state.get("overview", ""), max_chars=500),
        "logic_issues": "\n".join(logic_issue_lines) if logic_issue_lines else "None.",
        "improvement_notes": "\n".join(improvement_lines)
        if improvement_lines
        else "None.",
        "review_links": "\n".join(review_link_lines) if review_link_lines else "None.",
        "progress_summary": summarize_history_progress(
            previous_failed_test_case_ids=state.get("previous_failed_test_case_ids", []),
            persistent_failed_test_case_ids=state.get(
                "persistent_failed_test_case_ids", []
            ),
            fixed_test_case_ids=state.get("fixed_test_case_ids", []),
            regressed_test_case_ids=state.get("regressed_test_case_ids", []),
        ),
    }


def _format_history_summary(state: ReviewState) -> str:
    history = state.get("history", [])
    if not history:
        return "No previous submissions."

    blocks = []
    for index, submission in enumerate(history[:3], start=1):
        blocks.append(
            "\n".join(
                [
                    f"Previous submission {index} (newest first order):",
                    f"Submission id: {submission.get('submission_id', '')}",
                    f"Failed testcase IDs: {submission.get('failed_test_case_ids', [])}",
                    f"Passed testcase IDs: {submission.get('passed_test_case_ids', [])}",
                    f"Code summary: {compress_text(submission.get('code', ''), max_chars=400)}",
                ]
            )
        )
    return "\n\n".join(blocks)
