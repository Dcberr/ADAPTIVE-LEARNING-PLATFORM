import unittest

try:
    from app.prompts.review.scoring import build_scoring_messages
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    build_scoring_messages = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@unittest.skipIf(
    build_scoring_messages is None,
    f"missing runtime dependency: {_IMPORT_ERROR}",
)
class ScoringPromptTests(unittest.TestCase):
    def test_scoring_prompt_mentions_rubric_evidence_mapping_and_anti_halo_rules(self):
        messages = build_scoring_messages(
            {
                "code": "if (x > 0) { cout << \"positive\"; } else { cout << \"negative\"; }",
                "history": [
                    {
                        "code": "cout << \"positive\";",
                        "failed_test_case_ids": ["tc-1"],
                        "passed_test_case_ids": ["tc-2"],
                    }
                ],
                "overview": "The student handles the positive case but still misses zero.",
                "logic_issues": {
                    "tc-1": {
                        "issue": "Zero is not handled.",
                        "evidence": "tc-1",
                        "code_snippet": "",
                        "anchor_snippet": "if (x > 0) {",
                        "cause_type": "missing_branch",
                        "why_test_failed": "For input 0, the code falls into the wrong branch.",
                        "missing_behavior": "Add a zero branch.",
                        "history_status": "persistent",
                        "fix_suggestion": "Check the zero case before the final fallback.",
                        "location": None,
                    }
                },
                "improvement_notes": [],
                "persistent_failed_test_case_ids": ["tc-1"],
                "fixed_test_case_ids": ["tc-2"],
                "regressed_test_case_ids": [],
            }
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("score learning signals, not to punish", system_prompt)
        self.assertIn("Do not let one major bug drag every dimension down.", user_prompt)
        self.assertIn("Evidence mapping by index:", user_prompt)
        self.assertIn(
            "A failing submission can still show partial understanding",
            user_prompt,
        )
        self.assertIn("Self-Correction Path: use newest-first history", user_prompt)
        self.assertIn("Return exactly one valid JSON object", system_prompt)


if __name__ == "__main__":
    unittest.main()
