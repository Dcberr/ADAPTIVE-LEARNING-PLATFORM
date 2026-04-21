import unittest

from app.utils.review_output_tools import parse_review_json_with_repair


class _FakeResponseMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeChoice:
    def __init__(self, content: str):
        self.message = _FakeResponseMessage(content)


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


class _RepairingClient:
    def __init__(self, repaired_text: str):
        self.repaired_text = repaired_text
        self.calls = 0

        class _Completions:
            def __init__(inner_self, outer):
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.calls += 1
                return _FakeResponse(inner_self.outer.repaired_text)

        class _Chat:
            def __init__(inner_self, outer):
                inner_self.completions = _Completions(outer)

        self.chat = _Chat(self)


class ReviewOutputToolsTests(unittest.TestCase):
    def test_parse_review_json_with_repair_uses_repair_when_shape_is_wrong(self):
        client = _RepairingClient('{"fix_suggestion":"Trace the branch first."}')

        parsed = parse_review_json_with_repair(
            client=client,
            model_name="test-model",
            raw_response="The fix is to check the branch.",
            expected_shape={"fix_suggestion": str},
        )

        self.assertEqual(client.calls, 1)
        self.assertEqual(parsed["fix_suggestion"], "Trace the branch first.")

    def test_parse_review_json_with_repair_skips_repair_when_shape_is_valid(self):
        client = _RepairingClient('{"unused":"value"}')

        parsed = parse_review_json_with_repair(
            client=client,
            model_name="test-model",
            raw_response='{"scorecard": {}}',
            expected_shape={"scorecard": dict},
        )

        self.assertEqual(client.calls, 0)
        self.assertEqual(parsed["scorecard"], {})


if __name__ == "__main__":
    unittest.main()
