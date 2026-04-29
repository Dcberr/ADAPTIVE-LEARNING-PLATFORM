from __future__ import annotations

import logging
import time
from typing import Any

from openai import RateLimitError


logger = logging.getLogger(__name__)


class FireworksRateLimitExceededError(RuntimeError):
    """Raised when Fireworks rate limiting persists after all retries are exhausted."""


def create_chat_completion_with_retry(
    client: Any,
    *,
    max_retries: int = 3,
    initial_delay_seconds: float = 1.0,
    max_delay_seconds: float = 8.0,
    **kwargs: Any,
) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as exc:
            if attempt >= max_retries:
                raise FireworksRateLimitExceededError("rate limit exceed") from exc

            delay_seconds = _resolve_retry_delay_seconds(
                exc=exc,
                attempt=attempt,
                initial_delay_seconds=initial_delay_seconds,
                max_delay_seconds=max_delay_seconds,
            )
            logger.warning(
                "Fireworks rate limit hit for model=%s on attempt %s/%s; retrying in %.2fs",
                kwargs.get("model", ""),
                attempt + 1,
                max_retries + 1,
                delay_seconds,
            )
            time.sleep(delay_seconds)


def _resolve_retry_delay_seconds(
    *,
    exc: RateLimitError,
    attempt: int,
    initial_delay_seconds: float,
    max_delay_seconds: float,
) -> float:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or {}
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after is not None:
        try:
            return max(0.0, min(float(retry_after), max_delay_seconds))
        except (TypeError, ValueError):
            pass

    return min(initial_delay_seconds * (2**attempt), max_delay_seconds)
