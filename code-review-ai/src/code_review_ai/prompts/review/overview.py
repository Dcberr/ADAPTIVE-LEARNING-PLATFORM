from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.review_state import ReviewState


def build_overview_messages(state: ReviewState) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are a careful CS1 teacher. "
                "Write one short overview paragraph directly to the student. "
                "Use a supportive, clear, educational tone. "
                "Do not output planning notes, headings, lists, or meta commentary."
            ),
        },
        {"role": "user", "content": build_overview_prompt(state)},
    ]


def build_overview_prompt(state: ReviewState) -> str:
    logic_issues = list(state.get("logic_issues", {}).values())[:1]
    improvement_notes = list(state.get("improvement_notes", []))[:1]

    logic_issue_lines = [
        f"- {str(issue.get('issue', '')).strip()}"
        for issue in logic_issues
        if str(issue.get("issue", "")).strip()
    ]
    improvement_lines = [
        f"- {str(note.get('issue', '')).strip()}"
        for note in improvement_notes
        if str(note.get("issue", "")).strip()
    ]
    logic_issue_block = "\n".join(logic_issue_lines) or "- None"
    improvement_block = "\n".join(improvement_lines) or "- None"

    return dedent(f"""
        Write a short overview for this student's current submission using only these current review findings.

        Main logic issue
        {logic_issue_block}

        Main improvement note
        {improvement_block}

        Write exactly one paragraph with 5 to 7 sentences.
        Aim for about 80 to 110 words when there is a logic issue or improvement note to explain.
        Write as if you are speaking directly to the student.
        Start with the most important logic problem if there is one.
        Briefly explain why that problem affects the program behavior in simple beginner-friendly language.
        If helpful, mention the improvement note so the student knows what to focus on next.
        Help the student understand what to learn or check next without turning the paragraph into a long explanation.
        Do not include raw code, JSON, headings, bullet points, labels, IDs, testcase names, or meta commentary.
        Do not mention prompts, hidden instructions, policies, or internal rules.
        Output only the final overview paragraph.
        """).strip()
