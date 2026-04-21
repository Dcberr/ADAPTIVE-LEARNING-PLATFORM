import unittest

try:
    from app.prompts.review.logic import build_logic_messages
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    build_logic_messages = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@unittest.skipIf(
    build_logic_messages is None,
    f"missing runtime dependency: {_IMPORT_ERROR}",
)
class ReviewLogicPromptTests(unittest.TestCase):
    def test_logic_prompt_mentions_cpp_missing_logic_and_anchor_snippet_rules(self):
        messages = build_logic_messages(
            code_context='   1 | if (x > 0) {\n   2 |     cout << "positive";\n   3 | }',
            failed_tests=[
                {
                    "id": "tc-1",
                    "input": "-2",
                    "expected": "negative",
                    "actual": "",
                }
            ],
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("Analyze C++ student code context", system_prompt)
        self.assertIn("If the needed behavior is missing", system_prompt)
        self.assertIn('"cause_type": one of "incorrect_code", "missing_logic"', user_prompt)
        self.assertIn('"anchor_snippet": "nearest related code snippet or null"', user_prompt)
        self.assertIn('"missing_behavior": "short description or null"', user_prompt)
        self.assertIn('set "code_snippet" to null', user_prompt)
        self.assertIn("Do not include testcase ids, indexes, or any other identifier fields", user_prompt)
        self.assertNotIn('"evidence": "test case id"', user_prompt)
        self.assertNotIn("Submission history:", user_prompt)


if __name__ == "__main__":
    unittest.main()
