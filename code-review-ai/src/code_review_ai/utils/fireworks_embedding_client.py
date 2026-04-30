from __future__ import annotations

import json
from urllib import error, request


class FireworksEmbeddingClient:
    def __init__(self, *, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def embed(self, *, model_name: str, inputs: list[str]) -> list[list[float]]:
        if not inputs:
            return []
        if not self.api_key.strip():
            raise RuntimeError(
                "FIREWORKS_API_KEY is not configured for exercise embedding generation."
            )

        payload = json.dumps(
            {
                "model": model_name,
                "input": inputs,
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/embeddings",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Fireworks embedding request failed with status {exc.code}: {body}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Fireworks embedding request failed: {exc.reason}"
            ) from exc

        parsed = json.loads(raw_body)
        data = parsed.get("data")
        if not isinstance(data, list):
            raise RuntimeError(
                "Fireworks embedding response did not contain a data list."
            )

        embeddings: list[list[float]] = []
        for item in data:
            embedding = item.get("embedding")
            if not isinstance(embedding, list):
                raise RuntimeError(
                    "Fireworks embedding response item did not contain an embedding list."
                )
            embeddings.append([float(value) for value in embedding])
        return embeddings
