from __future__ import annotations

from textwrap import dedent

from app.models.review_state import ReviewState


def build_scoring_messages(state: ReviewState) -> list[dict[str, str]]:
    progress_summary = (
        f"Persistent failed testcase IDs: {state.get('persistent_failed_test_case_ids', [])}\n"
        f"Fixed testcase IDs since previous submission: {state.get('fixed_test_case_ids', [])}\n"
        f"Newly failing testcase IDs since previous submission: {state.get('regressed_test_case_ids', [])}"
    )
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You are an educational assessment agent for CS1 submissions.

                Your job is to score learning signals, not to punish the student for every failing testcase.
                Judge each dimension independently using concrete evidence from the current submission first,
                then use recent history only as a supporting signal.

                Return exactly one valid JSON object and nothing else.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                CURRENT STUDENT CODE:
                {state.get('code', '')}

                SUBMISSION HISTORY:
                {_format_history(state)}

                REVIEW OVERVIEW:
                {state.get('overview', '')}

                LOGIC ISSUES:
                {list(state.get('logic_issues', {}).values())}

                IMPROVEMENT NOTES:
                {state.get('improvement_notes', [])}

                HISTORY-BASED PROGRESS SUMMARY:
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

                Core scoring rules:
                - Score from observable evidence, not from vague impressions.
                - Use the current submission as the primary evidence source.
                - Use history as a secondary signal, especially for Self-Correction Path.
                - Do not let one major bug drag every dimension down.
                - A failing submission can still show partial understanding in variables, control flow, or debugging behavior.
                - Since this is CS1, avoid over-penalizing beginner code for style alone.
                - Use extreme scores only when evidence is strong.

                Score scale:
                - 1 = very weak evidence of the skill
                - 2 = limited and inconsistent evidence
                - 3 = mixed or moderate evidence
                - 4 = clear but not fully consistent evidence
                - 5 = strong and consistent evidence

                Evidence mapping by index:
                - Problem-Solving Creativity: look for whether the student is attempting a real solution strategy or only shallow hard-coded behavior.
                - Logic Traceability: use how understandable and traceable the reasoning path is through the code and logic issues.
                - Generalization Score: use evidence about whether the code handles more than the easiest cases.
                - Construct Appropriateness: use whether the chosen conditions, loops, variables, and basic constructs fit the task.
                - Self-Correction Path: use newest-first history, fixed testcases, persistent failures, and regressions.
                - Variable Understanding: use how values are stored, updated, and interpreted in the code and logic issues.
                - Control Flow Understanding: use conditions, branching, loop behavior, and missing-branch errors.
                - Input/Output Awareness: use parsing, formatting, exact-output mismatches, and expected-vs-actual behavior.
                - Edge Case Awareness: use zero/negative/boundary/special-case handling and related failures.
                - Debugging Readiness: use whether the student's current attempt and recent changes suggest systematic correction or random changes.

                Output rules:
                - For each index, return:
                  - score: integer 1 to 5
                  - label: short phrase
                  - explanation: concise evidence-based explanation
                - Keep explanations short and specific.
                - Do not mention hidden test cases.
                - Do not return markdown or extra prose.

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

                Return JSON only.
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
                f"Previous submission {index} (newest first order):\n"
                f"Failed testcase IDs: {submission.get('failed_test_case_ids', [])}\n"
                f"Passed testcase IDs: {submission.get('passed_test_case_ids', [])}\n"
                f"Code:\n{submission.get('code', '')}"
            )
            for index, submission in enumerate(history, start=1)
        ]
    )
