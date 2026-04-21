import unittest

try:
    from app.agents.review_link_agent import ReviewLinkAgent
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    ReviewLinkAgent = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from app.models.logic_issue import create_logic_issue


class _ExplodingClient:
    class _Chat:
        class _Completions:
            @staticmethod
            def create(**kwargs):
                raise AssertionError(
                    "ReviewLinkAgent should not call the model when history is empty"
                )

        completions = _Completions()

    chat = _Chat()


@unittest.skipIf(
    ReviewLinkAgent is None,
    f"missing runtime dependency: {_IMPORT_ERROR}",
)
class ReviewLinkAgentTests(unittest.TestCase):
    def test_review_link_skips_when_history_is_empty(self):
        agent = ReviewLinkAgent(
            client=_ExplodingClient(),
            model_name="test-model",
        )
        state = {
            "code": "int main() { return 0; }",
            "history": [],
            "logic_issues": {
                "tc_1": create_logic_issue(
                    issue="The negative case is still not handled.",
                    evidence="tc_1",
                    code_snippet="if (x > 0) { cout << \"positive\"; }",
                )
            },
            "review_links": [
                {
                    "issue_evidence": "tc_1",
                    "previous_submission_id": "11111111-1111-1111-1111-111111111111",
                    "previous_code_snippets": ["stale"],
                    "comparison_mode": "persistent",
                    "what_improved": "stale",
                    "what_still_needs_work": "stale",
                    "relation_summary": "stale",
                }
            ],
        }

        updated_state = agent.analyze(state)

        self.assertEqual(updated_state["review_links"], [])

    def test_review_link_uses_first_earlier_failed_submission(self):
        agent = ReviewLinkAgent(
            client=_ExplodingClient(),
            model_name="test-model",
        )
        previous_submission = agent.find_first_failed_history_match(
            {
                "history": [
                    {
                        "submission_id": "11111111-1111-1111-1111-111111111111",
                        "code": "first failed code",
                        "failed_test_case_ids": ["tc_1"],
                        "passed_test_case_ids": [],
                    },
                    {
                        "submission_id": "22222222-2222-2222-2222-222222222222",
                        "code": "older failed code",
                        "failed_test_case_ids": ["tc_1"],
                        "passed_test_case_ids": [],
                    },
                ]
            },
            "tc_1",
        )

        self.assertEqual(
            previous_submission,
            {
                "submission_id": "11111111-1111-1111-1111-111111111111",
                "code": "first failed code",
            },
        )


if __name__ == "__main__":
    unittest.main()
