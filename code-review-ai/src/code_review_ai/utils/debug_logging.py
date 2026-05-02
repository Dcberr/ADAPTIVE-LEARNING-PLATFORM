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
        "overview_present": bool(state.get("overview")),
        "code_preview": truncate_text(state.get("code", ""), limit=80),
    }


def snapshot_review_state(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact but more detailed review-state snapshot for debug logs."""
    logic_issues = list((state.get("logic_issues") or {}).values())
    improvement_notes = list(state.get("improvement_notes") or [])
    review_items = list(state.get("review_items") or [])
    review_links = list(state.get("review_links") or [])
    return {
        "overview": truncate_text(state.get("overview", ""), limit=220),
        "logic_issue_summaries": [
            truncate_text(issue.get("issue", ""), limit=140) for issue in logic_issues[:3]
        ],
        "improvement_summaries": [
            truncate_text(note.get("issue", ""), limit=140) for note in improvement_notes[:3]
        ],
        "review_item_types": [item.get("type", "") for item in review_items[:5]],
        "review_link_summaries": [
            truncate_text(link.get("relation_summary", ""), limit=140)
            for link in review_links[:3]
        ],
    }
