from __future__ import annotations

from difflib import SequenceMatcher


def build_changed_line_summary(
    *,
    previous_code: str,
    current_code: str,
    max_changes: int = 6,
) -> list[str]:
    previous_lines = previous_code.splitlines()
    current_lines = current_code.splitlines()
    matcher = SequenceMatcher(a=previous_lines, b=current_lines)
    changes: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag in {"replace", "delete"}:
            for line in previous_lines[i1:i2]:
                stripped = line.strip()
                if stripped:
                    changes.append(f"- {stripped}")
                if len(changes) >= max_changes:
                    return changes
        if tag in {"replace", "insert"}:
            for line in current_lines[j1:j2]:
                stripped = line.strip()
                if stripped:
                    changes.append(f"+ {stripped}")
                if len(changes) >= max_changes:
                    return changes

    return changes
