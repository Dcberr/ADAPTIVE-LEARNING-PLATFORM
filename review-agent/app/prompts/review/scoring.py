from __future__ import annotations

from textwrap import dedent

from app.models.review_state import ReviewState


def build_scoring_messages(state: ReviewState) -> list[dict[str, str]]:
    progress_summary = (
        f"Persistent failed testcase IDs: {state.get('persistent_failed_test_case_ids', [])}\n"
        f"Fixed testcase IDs since first history entry: {state.get('fixed_test_case_ids', [])}\n"
        f"Newly failing testcase IDs since first history entry: {state.get('regressed_test_case_ids', [])}"
    )
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are an educational assessment agent for CS1 submissions.

                Score learning signals based on the student's current code,
                submission history, and review findings.

                Return valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Current student code:
                {state.get('code', '')}

                Submission history:
                {_format_history(state)}

                Review overview:
                {state.get('overview', '')}

                Logic issues:
                {list(state.get('logic_issues', {}).values())}

                Improvement notes:
                {state.get('improvement_notes', [])}

                History-based progress summary:
                {progress_summary}

                Score these ten indices:
                1. Problem-Solving Creativity
                2. Logic Traceability
                3. Generalization Score
                4. Construct Appropriateness
                5. Self-Correction Path
                6. Variable Understanding
                7. Control Flow Understanding
                8. Input/Output Awareness
                9. Edge Case Awareness
                10. Debugging Readiness

                For each index:
                - assign a score from 1 to 5
                - provide a short label
                - provide a concise explanation grounded in the code/history/review

                Return JSON in exactly this shape:
                {{
                  "scorecard": {{
                    "problem_solving_creativity": {{
                      "score": 1,
                      "label": "Rote Memorization",
                      "explanation": "short grounded explanation"
                    }},
                    "logic_traceability": {{
                      "score": 1,
                      "label": "Chaotic",
                      "explanation": "short grounded explanation"
                    }},
                    "generalization_score": {{
                      "score": 1,
                      "label": "Hard-coded",
                      "explanation": "short grounded explanation"
                    }},
                    "construct_appropriateness": {{
                      "score": 1,
                      "label": "Poor Tool Choice",
                      "explanation": "short grounded explanation"
                    }},
                    "self_correction_path": {{
                      "score": 1,
                      "label": "Random Changes",
                      "explanation": "short grounded explanation"
                    }},
                    "variable_understanding": {{
                      "score": 1,
                      "label": "Treats Values as Fixed",
                      "explanation": "short grounded explanation"
                    }},
                    "control_flow_understanding": {{
                      "score": 1,
                      "label": "Confused Flow",
                      "explanation": "short grounded explanation"
                    }},
                    "input_output_awareness": {{
                      "score": 1,
                      "label": "I/O Mismatch",
                      "explanation": "short grounded explanation"
                    }},
                    "edge_case_awareness": {{
                      "score": 1,
                      "label": "Happy-Path Only",
                      "explanation": "short grounded explanation"
                    }},
                    "debugging_readiness": {{
                      "score": 1,
                      "label": "Needs Debugging Support",
                      "explanation": "short grounded explanation"
                    }}
                  }}
                }}

                Scoring guidance:
                - 1 means very weak evidence
                - 3 means mixed or moderate evidence
                - 5 means strong evidence
                - Ground every score in observable signals from the code or history.
                - For Self-Correction Path, use history heavily.
                - For beginner-focused indices, favor concrete evidence about variables, control flow, input/output handling, edge cases, and how the student responds to failed attempts.
                - Return JSON only.
                """
            ).strip(),
        },
    ]


def _format_history(state: ReviewState) -> str:
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
