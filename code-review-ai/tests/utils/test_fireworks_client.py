import unittest
from unittest.mock import MagicMock, patch

from openai import RateLimitError

from code_review_ai.utils.fireworks_client import (
    FireworksRateLimitExceededError,
    create_chat_completion_with_retry,
)


class FireworksClientRetryTests(unittest.TestCase):
    def test_retries_after_rate_limit_then_succeeds(self):
        client = MagicMock()
        response = MagicMock()
        rate_limit_error = RateLimitError(
            "rate limited",
            response=MagicMock(headers={}),
            body={},
        )
        client.chat.completions.create.side_effect = [rate_limit_error, response]

        with patch("code_review_ai.utils.fireworks_client.time.sleep") as sleep:
            result = create_chat_completion_with_retry(
                client,
                model="fireworks/test-model",
                messages=[],
                temperature=0.0,
                max_tokens=10,
            )

        self.assertIs(result, response)
        self.assertEqual(client.chat.completions.create.call_count, 2)
        sleep.assert_called_once()

    def test_raises_custom_error_when_rate_limit_retries_are_exhausted(self):
        client = MagicMock()
        rate_limit_error = RateLimitError(
            "rate limited",
            response=MagicMock(headers={}),
            body={},
        )
        client.chat.completions.create.side_effect = rate_limit_error

        with patch("code_review_ai.utils.fireworks_client.time.sleep"):
            with self.assertRaises(FireworksRateLimitExceededError):
                create_chat_completion_with_retry(
                    client,
                    max_retries=1,
                    model="fireworks/test-model",
                    messages=[],
                    temperature=0.0,
                    max_tokens=10,
                )


if __name__ == "__main__":
    unittest.main()
