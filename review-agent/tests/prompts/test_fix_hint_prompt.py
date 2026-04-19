import unittest

try:
    from app.prompts.review.fix_hint import build_fix_hint_messages
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    build_fix_hint_messages = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@unittest.skipIf(
    build_fix_hint_messages is None,
    f"missing runtime dependency: {_IMPORT_ERROR}",
)
class FixHintPromptTests(unittest.TestCase):
    def test_fix_hint_prompt_mentions_cause_type_strategy_and_action_rule(self):
        messages = build_fix_hint_messages(
            issue={
                "issue": "The code never handles negative input.",
                "evidence": "tc-1",
                "code_snippet": "",
                "anchor_snippet": "if (x > 0) {",
                "cause_type": "missing_branch",
                "why_test_failed": "For input -2, the current code skips the positive branch and never prints the required negative case.",
                "missing_behavior": "Add a branch for negative values before the final output.",
                "history_status": "current_only",
                "fix_suggestion": "",
                "location": None,
            },
            assignment="Write a program that prints whether a number is positive or negative.",
            current_code="if (x > 0) {\n    cout << \"positive\";\n}",
            testcase_context="Input: -2\nExpected output: negative\nActual output:",
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("provided diagnosis", system_prompt)
        self.assertIn("Hint strategy by cause type:", user_prompt)
        self.assertIn("missing_logic or missing_branch", user_prompt)
        self.assertIn("Give one actionable next step", user_prompt)
        self.assertIn("Do not rewrite the whole program.", user_prompt)
        self.assertIn("ANCHOR SNIPPET:", user_prompt)


if __name__ == "__main__":
    unittest.main()
