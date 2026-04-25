from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    leetcode_graphql_url: str = os.getenv("LEETCODE_GRAPHQL_URL", "https://leetcode.com/graphql")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/import_exercises.db"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    backoff_seconds: float = float(os.getenv("BACKOFF_SECONDS", "1.5"))

