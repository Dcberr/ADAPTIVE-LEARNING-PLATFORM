from __future__ import annotations


def extract_related_snippets(
    *,
    code: str,
    anchors: list[str],
    max_snippets: int = 2,
    context_lines: int = 1,
    max_chars: int = 240,
) -> list[str]:
    if not code.strip():
        return []

    lines = code.splitlines()
    snippets: list[str] = []
    for anchor in anchors:
        anchor = str(anchor).strip()
        if not anchor:
            continue
        for index, line in enumerate(lines):
            if anchor not in line and line.strip() != anchor:
                continue
            start = max(0, index - context_lines)
            end = min(len(lines), index + context_lines + 1)
            snippet = "\n".join(lines[start:end]).strip()
            if len(snippet) > max_chars:
                snippet = f"{snippet[: max_chars - 3]}..."
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= max_snippets:
                return snippets
    return snippets


def compress_text(value: str, max_chars: int = 600) -> str:
    text = str(value).strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."
