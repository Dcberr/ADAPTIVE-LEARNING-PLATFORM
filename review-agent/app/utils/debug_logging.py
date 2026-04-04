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
    concept_issues = state.get("concept_issues") or []
    review_items = state.get("review_items") or []
    sandbox_results = state.get("sandbox_results") or []

    return {
        "sandbox_results": len(sandbox_results),
        "logic_issues": len(logic_issues),
        "concept_issues": len(concept_issues),
        "improvement_notes": len(improvement_notes),
        "review_items": len(review_items),
        "overview_present": bool(state.get("overview")),
        "expected_concepts": len(state.get("expected_concepts") or []),
        "code_preview": truncate_text(state.get("code", ""), limit=80),
    }
