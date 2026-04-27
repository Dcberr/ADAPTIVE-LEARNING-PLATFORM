from __future__ import annotations

from typing import Any, Mapping


def truncate_text(value: Any, limit: int = 160) -> str:
    """Return a compact single-line preview for debug logging."""
    if value is None:
        return ""

    text = str(value).replace("\n", "\\n").strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def summarize_state(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact summary of the current workflow state."""
    logic_issues = state.get("logic_issues") or {}
    improvement_notes = state.get("improvement_notes") or []
    review_items = state.get("review_items") or []
    review_links = state.get("review_links") or []
    scorecard = state.get("scorecard") or []
    sandbox_results = state.get("sandbox_results") or []
    persistent_failed_test_case_ids = state.get("persistent_failed_test_case_ids") or []
    fixed_test_case_ids = state.get("fixed_test_case_ids") or []
    regressed_test_case_ids = state.get("regressed_test_case_ids") or []

    return {
        "sandbox_results": len(sandbox_results),
        "logic_issues": len(logic_issues),
        "persistent_failed_testcases": len(persistent_failed_test_case_ids),
        "fixed_testcases": len(fixed_test_case_ids),
        "regressed_testcases": len(regressed_test_case_ids),
        "improvement_notes": len(improvement_notes),
        "review_items": len(review_items),
        "review_links": len(review_links),
        "scorecard": len(scorecard),
        "overview_present": bool(state.get("overview")),
        "code_preview": truncate_text(state.get("code", ""), limit=80),
    }
