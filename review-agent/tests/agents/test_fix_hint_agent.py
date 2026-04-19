import asyncio
import unittest

try:
    from app.agents.fix_hint_agent import FixHintAgent
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    FixHintAgent = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from app.models.logic_issue import create_logic_issue


class _FakeResponseMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeChoice:
    def __init__(self, content: str):
        self.message = _FakeResponseMessage(content)


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


class _RecordingClient:
    def __init__(self):
        self.calls = []

        class _Completions:
            def __init__(inner_self, outer):
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.calls.append(kwargs)
                return _FakeResponse(
                    '{"fix_suggestion":"Trace the branch for this testcase and adjust the missing rule."}'
                )

        class _Chat:
            def __init__(inner_self, outer):
                inner_self.completions = _Completions(outer)

        self.chat = _Chat(self)


@unittest.skipIf(
    FixHintAgent is None,
    f"missing runtime dependency: {_IMPORT_ERROR}",
)
class FixHintAgentTests(unittest.TestCase):
    def test_fix_hint_agent_async_updates_multiple_issues(self):
        client = _RecordingClient()
        agent = FixHintAgent(
            client=client,
            model_name="test-model",
            max_concurrency=2,
        )
        state = {
            "assignment_requirements": "Print whether the number is negative, zero, or positive.",
            "code": "if (x > 0) { cout << \"positive\"; } else { cout << \"negative\"; }",
            "sandbox_results": [
                {
                    "id": "tc-1",
                    "input": "0",
                    "expected": "zero",
                    "actual": "negative",
                },
                {
                    "id": "tc-2",
                    "input": "8",
                    "expected": "positive even",
                    "actual": "positive",
                },
            ],
            "logic_issues": {
                "tc-1": create_logic_issue(
                    issue="Zero is not handled.",
                    evidence="tc-1",
                    anchor_snippet="if (x > 0) {",
                    cause_type="missing_branch",
                    why_test_failed="For input 0, the code goes to the fallback branch and prints negative.",
                    missing_behavior="Add a zero branch before the negative fallback.",
                ),
                "tc-2": create_logic_issue(
                    issue="Positive even values are labeled too broadly.",
                    evidence="tc-2",
                    code_snippet='cout << "positive";',
                    cause_type="incorrect_code",
                    why_test_failed="For input 8, the code does not distinguish even from odd positive values.",
                ),
            },
        }

        updated_state = asyncio.run(agent.analyze(state))

        self.assertEqual(len(client.calls), 2)
        self.assertEqual(
            updated_state["logic_issues"]["tc-1"]["fix_suggestion"],
            "Trace the branch for this testcase and adjust the missing rule.",
        )
        self.assertEqual(
            updated_state["logic_issues"]["tc-2"]["fix_suggestion"],
            "Trace the branch for this testcase and adjust the missing rule.",
        )


if __name__ == "__main__":
    unittest.main()
