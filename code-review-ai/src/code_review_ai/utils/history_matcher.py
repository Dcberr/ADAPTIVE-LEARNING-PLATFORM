from __future__ import annotations

from typing import Any


def find_first_failed_history_match(
    history: list[dict[str, Any]],
    testcase_id: str,
) -> dict[str, str] | None:
    for submission in history:
        if testcase_id in submission.get("failed_test_case_ids", []):
            return {
                "submission_id": str(submission.get("submission_id", "")).strip(),
                "code": str(submission.get("code", "")).strip(),
            }
    return None


def summarize_history_progress(
    *,
    previous_failed_test_case_ids: list[str],
    persistent_failed_test_case_ids: list[str],
    fixed_test_case_ids: list[str],
    regressed_test_case_ids: list[str],
) -> str:
    return "\n".join(
        [
            f"Latest previous failed testcase IDs: {previous_failed_test_case_ids}",
            f"Persistent failed testcase IDs: {persistent_failed_test_case_ids}",
            f"Fixed testcase IDs: {fixed_test_case_ids}",
            f"Regressed testcase IDs: {regressed_test_case_ids}",
        ]
    )
