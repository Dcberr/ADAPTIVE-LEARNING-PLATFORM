import json
import unittest
from unittest.mock import patch

from code_review_ai.utils.fireworks_embedding_client import FireworksEmbeddingClient


class _FakeResponse:
    def __init__(self, body: str):
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class FireworksEmbeddingClientTests(unittest.TestCase):
    def test_embed_calls_fireworks_embeddings_endpoint(self):
        client = FireworksEmbeddingClient(
            api_key="test-key",
            base_url="https://api.fireworks.ai/inference/v1",
        )

        with patch(
            "code_review_ai.utils.fireworks_embedding_client.request.urlopen",
            return_value=_FakeResponse(
                json.dumps(
                    {
                        "data": [
                            {"embedding": [0.1, 0.2]},
                            {"embedding": [0.3, 0.4]},
                        ]
                    }
                )
            ),
        ) as urlopen:
            embeddings = client.embed(
                model_name="fireworks/qwen3-embedding-8b",
                inputs=["first", "second"],
            )

        self.assertEqual(embeddings, [[0.1, 0.2], [0.3, 0.4]])
        req = urlopen.call_args.args[0]
        self.assertEqual(
            req.full_url, "https://api.fireworks.ai/inference/v1/embeddings"
        )
        self.assertEqual(req.get_method(), "POST")

    def test_embed_requires_api_key(self):
        client = FireworksEmbeddingClient(api_key="", base_url="https://example.com")

        with self.assertRaises(RuntimeError) as context:
            client.embed(
                model_name="fireworks/qwen3-embedding-8b",
                inputs=["hello"],
            )

        self.assertIn("FIREWORKS_API_KEY", str(context.exception))


if __name__ == "__main__":
    unittest.main()
