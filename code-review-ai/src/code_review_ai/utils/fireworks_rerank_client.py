from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import error, request


logger = logging.getLogger(__name__)


class FireworksRerankError(RuntimeError):
    """Raised when the Fireworks rerank endpoint fails."""


def rerank_documents_with_retry(
    *,
    api_key: str,
    base_url: str,
    model_name: str,
    query: str,
    documents: list[str],
    top_n: int | None = None,
    return_documents: bool = False,
    task: str | None = None,
    max_retries: int = 3,
    initial_delay_seconds: float = 1.0,
    max_delay_seconds: float = 8.0,
) -> dict[str, Any]:
    if not documents:
        return {"object": "list", "model": model_name, "data": [], "usage": {}}

    payload: dict[str, Any] = {
        "model": model_name,
        "query": query,
        "documents": documents,
        "return_documents": return_documents,
    }
    if top_n is not None:
        payload["top_n"] = top_n
    if task:
        payload["task"] = task

    endpoint = f"{base_url.rstrip('/')}/rerank"
    body = json.dumps(payload).encode("utf-8")

    for attempt in range(max_retries + 1):
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body)
        except error.HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                if attempt >= max_retries:
                    raise FireworksRerankError(
                        f"rerank request failed with status {exc.code}"
                    ) from exc
                delay_seconds = _retry_delay(
                    attempt=attempt,
                    initial_delay_seconds=initial_delay_seconds,
                    max_delay_seconds=max_delay_seconds,
                    retry_after=exc.headers.get("Retry-After"),
                )
                logger.warning(
                    "Fireworks rerank request failed with status %s on attempt %s/%s; retrying in %.2fs",
                    exc.code,
                    attempt + 1,
                    max_retries + 1,
                    delay_seconds,
                )
                time.sleep(delay_seconds)
                continue
            raise FireworksRerankError(
                f"rerank request failed with status {exc.code}"
            ) from exc
        except error.URLError as exc:
            if attempt >= max_retries:
                raise FireworksRerankError("rerank request failed") from exc
            delay_seconds = _retry_delay(
                attempt=attempt,
                initial_delay_seconds=initial_delay_seconds,
                max_delay_seconds=max_delay_seconds,
                retry_after=None,
            )
            logger.warning(
                "Fireworks rerank request failed on attempt %s/%s; retrying in %.2fs",
                attempt + 1,
                max_retries + 1,
                delay_seconds,
            )
            time.sleep(delay_seconds)

    raise FireworksRerankError("rerank request failed")


def _retry_delay(
    *,
    attempt: int,
    initial_delay_seconds: float,
    max_delay_seconds: float,
    retry_after: str | None,
) -> float:
    if retry_after:
        try:
            return max(0.0, min(float(retry_after), max_delay_seconds))
        except (TypeError, ValueError):
            pass
    return min(initial_delay_seconds * (2**attempt), max_delay_seconds)
