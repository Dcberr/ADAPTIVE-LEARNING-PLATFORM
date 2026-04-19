from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CodeChunk:
    label: str
    start_line: int
    end_line: int
    code: str


def build_logic_code_context(
    *,
    code: str,
    failed_tests: list[dict[str, Any]],
    max_chunks: int = 4,
) -> str:
    lines = code.splitlines()
    if not lines:
        return "No student code provided."

    if len(lines) <= 80:
        return f"Full C++ code with line numbers:\n{_with_line_numbers(code)}"

    chunks = _extract_tree_sitter_cpp_chunks(code) or _extract_cpp_keyword_chunks(code)
    ranked_chunks = _rank_chunks(chunks=chunks, failed_tests=failed_tests)
    selected = ranked_chunks[:max_chunks] or [CodeChunk("full_code", 1, len(lines), code)]

    return "\n\n".join(
        [
            (
                f"[{chunk.label} | lines {chunk.start_line}-{chunk.end_line}]\n"
                f"{_with_line_numbers(chunk.code, start_line=chunk.start_line)}"
            )
            for chunk in selected
        ]
    )


def build_improvement_code_context(
    *,
    code: str,
    max_chunks: int = 5,
) -> str:
    lines = code.splitlines()
    if not lines:
        return "No student code provided."

    if len(lines) <= 100:
        full_code = f"Full C++ code with line numbers:\n{_with_line_numbers(code)}"
    else:
        chunks = _extract_tree_sitter_cpp_chunks(code) or _extract_cpp_keyword_chunks(code)
        selected = _rank_improvement_chunks(chunks)[:max_chunks] or [
            CodeChunk("full_code", 1, len(lines), code)
        ]
        full_code = "\n\n".join(
            [
                (
                    f"[{chunk.label} | lines {chunk.start_line}-{chunk.end_line}]\n"
                    f"{_with_line_numbers(chunk.code, start_line=chunk.start_line)}"
                )
                for chunk in selected
            ]
        )

    hotspot_text = _format_improvement_hotspots(code)
    return f"{full_code}\n\nPotential code-quality hotspots:\n{hotspot_text}"


def _extract_tree_sitter_cpp_chunks(code: str) -> list[CodeChunk]:
    parser = _get_tree_sitter_cpp_parser()
    if parser is None:
        return []

    try:
        tree = parser.parse(code.encode("utf-8"))
        root = tree.root_node
    except Exception:
        return []

    interesting_types = {
        "function_definition",
        "if_statement",
        "for_statement",
        "while_statement",
        "switch_statement",
        "case_statement",
        "declaration",
        "expression_statement",
        "return_statement",
    }
    chunks: list[CodeChunk] = []
    seen_ranges: set[tuple[int, int]] = set()
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type in interesting_types:
            start_line = int(node.start_point[0]) + 1
            end_line = int(node.end_point[0]) + 1
            if (start_line, end_line) in seen_ranges:
                continue
            if end_line - start_line > 40:
                continue
            snippet = code[node.start_byte : node.end_byte].strip("\n")
            if snippet.strip():
                chunks.append(
                    CodeChunk(
                        label=node.type,
                        start_line=start_line,
                        end_line=end_line,
                        code=snippet,
                    )
                )
                seen_ranges.add((start_line, end_line))
        stack.extend(reversed(getattr(node, "children", [])))
    return chunks


def _extract_cpp_keyword_chunks(code: str) -> list[CodeChunk]:
    lines = code.splitlines()
    keywords = (
        "cin",
        "cout",
        "return",
        "if",
        "else",
        "for",
        "while",
        "switch",
        "case",
        "vector",
        "string",
    )
    chunks: list[CodeChunk] = []
    for index, line in enumerate(lines, start=1):
        if not any(keyword in line for keyword in keywords):
            continue
        start_line = max(1, index - 2)
        end_line = min(len(lines), index + 2)
        snippet = "\n".join(lines[start_line - 1 : end_line]).strip("\n")
        chunks.append(
            CodeChunk(
                label="cpp_window",
                start_line=start_line,
                end_line=end_line,
                code=snippet,
            )
        )
    return chunks


def _rank_chunks(
    *,
    chunks: list[CodeChunk],
    failed_tests: list[dict[str, Any]],
) -> list[CodeChunk]:
    if not chunks:
        return []

    combined_test_text = " ".join(
        [
            f"{case.get('input', '')} {case.get('expected', '')} {case.get('actual', '')}"
            for case in failed_tests
        ]
    ).lower()
    scored: list[tuple[int, int, CodeChunk]] = []
    for chunk in chunks:
        lower_code = chunk.code.lower()
        score = 0
        for keyword in (
            "cin",
            "cout",
            "return",
            "if",
            "else",
            "for",
            "while",
            "switch",
            "case",
        ):
            if keyword in lower_code:
                score += 2
        for token in ("+", "-", "*", "/", "%", "==", "!=", "<", ">", "int", "long", "double"):
            if token in lower_code:
                score += 1
        for test_token in combined_test_text.split():
            if len(test_token) >= 2 and test_token in lower_code:
                score += 1
        scored.append((score, -chunk.start_line, chunk))
    scored.sort(reverse=True)
    return [chunk for _, _, chunk in scored]


def _rank_improvement_chunks(chunks: list[CodeChunk]) -> list[CodeChunk]:
    if not chunks:
        return []

    scored: list[tuple[int, int, CodeChunk]] = []
    for chunk in chunks:
        lower_code = chunk.code.lower()
        score = 0
        if chunk.label == "function_definition":
            score += 5
        if chunk.label in {"for_statement", "while_statement", "if_statement", "switch_statement"}:
            score += 3
        if "cout" in lower_code or "cin" in lower_code:
            score += 2
        if lower_code.count("cout") > 1:
            score += 2
        if len(chunk.code.splitlines()) >= 8:
            score += 2
        if any(token in lower_code for token in ("int ", "double ", "string ", "vector<")):
            score += 1
        scored.append((score, -chunk.start_line, chunk))
    scored.sort(reverse=True)
    return [chunk for _, _, chunk in scored]


def _format_improvement_hotspots(code: str) -> str:
    lines = code.splitlines()
    hotspot_lines: list[str] = []

    if len(lines) > 25:
        hotspot_lines.append(
            f"- The submission is {len(lines)} lines long; check whether one long block should be split into smaller helper functions."
        )

    repeated_cout = sum(1 for line in lines if "cout" in line)
    if repeated_cout >= 3:
        hotspot_lines.append(
            "- There are several output statements; check whether output formatting could be simplified or grouped for readability."
        )

    repeated_cin = sum(1 for line in lines if "cin" in line)
    if repeated_cin >= 3:
        hotspot_lines.append(
            "- There are several input statements; check whether variable naming and input flow are easy for a CS1 student to follow."
        )

    if any("using namespace std" in line for line in lines):
        hotspot_lines.append(
            "- `using namespace std;` appears in the code; mention it only if the code also has other readability issues, since this is a beginner submission."
        )

    if any(line.count("if") + line.count("else") >= 2 for line in lines):
        hotspot_lines.append(
            "- There are nested or repeated branches; check whether the branching structure can be simplified or explained more clearly."
        )

    if any(_has_magic_number(line) for line in lines):
        hotspot_lines.append(
            "- Some literals may be acting like magic numbers; flag them only when naming or extraction would make the code meaningfully clearer."
        )

    return "\n".join(hotspot_lines) if hotspot_lines else "- No obvious code-quality hotspots detected from lightweight heuristics."


def _has_magic_number(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    for token in (" 0", " 1", " 2", " 10", "(0", "(1", "(2", "= 0", "= 1", "= 2", "= 10"):
        if token in f" {stripped}":
            return True
    return False


def _with_line_numbers(text: str, start_line: int = 1) -> str:
    lines = text.splitlines() or [text]
    return "\n".join(
        [
            f"{line_number:>4} | {line}"
            for line_number, line in enumerate(lines, start=start_line)
        ]
    )


def _get_tree_sitter_cpp_parser():
    try:
        from tree_sitter_languages import get_parser  # type: ignore

        return get_parser("cpp")
    except Exception:
        return None
