from __future__ import annotations

from openai import OpenAI


class FireworksEmbeddingClient:
    def __init__(self, *, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def embed(self, *, model_name: str, inputs: list[str]) -> list[list[float]]:
        if not inputs:
            return []
        if not self.api_key.strip():
            raise RuntimeError(
                "FIREWORKS_API_KEY is not configured for exercise embedding generation."
            )

        try:
            response = self.client.embeddings.create(
                model=model_name,
                input=inputs,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Fireworks embedding request failed: {exc}"
            ) from exc

        embeddings: list[list[float]] = []
        for item in response.data:
            embedding = getattr(item, "embedding", None)
            if not isinstance(embedding, list):
                raise RuntimeError(
                    "Fireworks embedding response item did not contain an embedding list."
                )
            embeddings.append([float(value) for value in embedding])
        return embeddings
