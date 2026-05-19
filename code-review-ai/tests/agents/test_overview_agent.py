import unittest
from unittest.mock import MagicMock

from code_review_ai.agents.overview_agent import OverviewAgent


class OverviewAgentTests(unittest.TestCase):
    def test_uses_model_response_when_available(self):
        client = MagicMock()
        response = MagicMock()
        response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Strong progress overall. Focus next on the remaining logic bug."
                )
            )
        ]
        client.chat.completions.create.return_value = response

        agent = OverviewAgent(client=client, model_name="fireworks/test-model")
        result = agent.analyze(
            {
                "code": "print('hello')",
                "logic_issues": {
                    "tc1": {
                        "issue": "The loop stops too early",
                        "evidence": "tc1",
                        "code_snippet": "",
                        "anchor_snippet": "",
                        "cause_type": "",
                        "why_test_failed": "",
                        "missing_behavior": "",
                        "location": None,
                        "history_status": "current_only",
                        "fix_suggestion": "",
                    }
                },
                "improvement_notes": [],
                "review_links": [],
            }
        )

        self.assertEqual(
            result["overview"],
            "Strong progress overall. Focus next on the remaining logic bug.",
        )

    def test_falls_back_to_local_summary_when_model_call_fails(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = RuntimeError("model unavailable")

        agent = OverviewAgent(client=client, model_name="fireworks/test-model")
        result = agent.analyze(
            {
                "code": "print('hello')",
                "logic_issues": {
                    "tc1": {
                        "issue": "The program does not handle negative input correctly",
                        "evidence": "tc1",
                        "code_snippet": "",
                        "anchor_snippet": "",
                        "cause_type": "",
                        "why_test_failed": "",
                        "missing_behavior": "",
                        "location": None,
                        "history_status": "current_only",
                        "fix_suggestion": "",
                    }
                },
                "improvement_notes": [
                    {
                        "issue": "Variable names are still too vague",
                        "code_snippet": "",
                        "fix_suggestion": "Rename temporary variables to describe their role.",
                        "location": None,
                    }
                ],
                "review_links": [],
            }
        )

        self.assertIn("main logic problem", result["overview"])
        self.assertIn("negative input", result["overview"])
        self.assertNotEqual(
            result["overview"],
            "Unable to generate overview at this time.",
        )

    def test_falls_back_to_local_summary_when_model_returns_blank_content(self):
        client = MagicMock()
        response = MagicMock()
        response.choices = [MagicMock(message=MagicMock(content="   "))]
        client.chat.completions.create.return_value = response

        agent = OverviewAgent(client=client, model_name="fireworks/test-model")
        result = agent.analyze(
            {
                "code": "print('hello')",
                "logic_issues": {
                    "tc1": {
                        "issue": "The condition misses the zero case",
                        "evidence": "tc1",
                        "code_snippet": "",
                        "anchor_snippet": "",
                        "cause_type": "",
                        "why_test_failed": "",
                        "missing_behavior": "",
                        "location": None,
                        "history_status": "current_only",
                        "fix_suggestion": "",
                    }
                },
                "improvement_notes": [],
                "review_links": [],
            }
        )

        self.assertIn("main logic problem", result["overview"])
        self.assertIn("zero case", result["overview"])

    def test_falls_back_when_model_returns_meta_analysis_instead_of_teacher_overview(self):
        client = MagicMock()
        response = MagicMock()
        response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        "The user wants me to write a short, student-facing overview paragraph. "
                        "Key constraints: start with the most important logic problem. "
                        "The prompt says to keep the tone educational."
                    )
                )
            )
        ]
        client.chat.completions.create.return_value = response

        agent = OverviewAgent(client=client, model_name="fireworks/test-model")
        result = agent.analyze(
            {
                "code": "print('hello')",
                "logic_issues": {
                    "tc1": {
                        "issue": "The code misses the branch for zero input",
                        "evidence": "tc1",
                        "code_snippet": "",
                        "anchor_snippet": "",
                        "cause_type": "",
                        "why_test_failed": "",
                        "missing_behavior": "",
                        "location": None,
                        "history_status": "current_only",
                        "fix_suggestion": "",
                    }
                },
                "improvement_notes": [],
                "review_links": [],
            }
        )

        self.assertIn("main logic problem", result["overview"])
        self.assertIn("zero input", result["overview"])


if __name__ == "__main__":
    unittest.main()
