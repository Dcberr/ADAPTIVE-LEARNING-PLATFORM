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
                    "current_issue": "stale",
                    "current_code_snippet": "stale",
                    "previous_submission_indexes": [1],
                    "comparison_mode": "persistent",
                    "previous_code_snippet": "stale",
                    "what_improved": "stale",
                    "what_still_needs_work": "stale",
                    "relation_summary": "stale",
                }
            ],
        }

        updated_state = agent.analyze(state)

        self.assertEqual(updated_state["review_links"], [])


if __name__ == "__main__":
    unittest.main()
