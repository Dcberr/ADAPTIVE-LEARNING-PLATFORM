from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        dotenv_path = Path(__file__).resolve().parents[2] / ".env"
        if not dotenv_path.is_file():
            return False

        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in {'"', "'"}
            ):
                value = value[1:-1]
            os.environ.setdefault(key, value)
        return True


load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    postgres_dsn: str
    import_csv_path: Path

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        return cls(
            postgres_dsn=os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/import_exercises",
            ),
            import_csv_path=Path(
                os.getenv("IMPORT_EXERCISES_CSV_PATH", "data/import_exercises.csv")
            ),
        )


@dataclass(frozen=True)
class LeetCodeSettings:
    graphql_url: str
    session: str
    csrf_token: str
    request_timeout_seconds: int
    max_retries: int
    backoff_seconds: float
    limit: int

    @classmethod
    def from_env(cls) -> "LeetCodeSettings":
        return cls(
            graphql_url=os.getenv("LEETCODE_GRAPHQL_URL", "https://leetcode.com/graphql"),
            session=os.getenv("LEETCODE_SESSION", ""),
            csrf_token=os.getenv("CSRFTOKEN", ""),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            backoff_seconds=float(os.getenv("BACKOFF_SECONDS", "1.5")),
            limit=int(os.getenv("LEETCODE_FETCH_LIMIT", "100")),
        )


@dataclass(frozen=True)
class CodeReviewApiSettings:
    base_url: str

    @classmethod
    def from_env(cls) -> "CodeReviewApiSettings":
        return cls(base_url=os.getenv("CODE_REVIEW_API_BASE_URL", ""))


@dataclass(frozen=True)
class ReviewAgentApiSettings:
    base_url: str
    max_workers: int

    @classmethod
    def from_env(cls) -> "ReviewAgentApiSettings":
        return cls(
            base_url=os.getenv("REVIEW_AGENT_API_BASE_URL", ""),
            max_workers=max(1, int(os.getenv("REVIEW_AGENT_API_MAX_WORKERS", "8"))),
        )


@dataclass(frozen=True)
class TagConfig:
    name: str
    slug: str
    enable: bool
    limit: int
    prerequisite_slugs: list[str]


def load_tags_config() -> list[TagConfig]:
    project_root = Path(__file__).resolve().parents[2]
    local_config_path = project_root / "config" / "tags_config.json"
    if local_config_path.is_file():
        content = local_config_path.read_text(encoding="utf-8")
    else:
        resource = files("import_exercise_batch.resources").joinpath("tags_config.json")
        content = resource.read_text(encoding="utf-8")

    tags = json.loads(content)
    return [TagConfig(**tag) for tag in tags]


@dataclass(frozen=True)
class ImportExercisesSettings:
    database: DatabaseSettings
    leetcode: LeetCodeSettings
    code_review_api: CodeReviewApiSettings
    review_agent_api: ReviewAgentApiSettings
    tags: list[TagConfig]

    @classmethod
    def from_env(cls) -> "ImportExercisesSettings":
        return cls(
            database=DatabaseSettings.from_env(),
            leetcode=LeetCodeSettings.from_env(),
            code_review_api=CodeReviewApiSettings.from_env(),
            review_agent_api=ReviewAgentApiSettings.from_env(),
            tags=load_tags_config(),
        )


@dataclass(frozen=True)
class ImportTopicsSettings:
    review_agent_api: ReviewAgentApiSettings
    tags: list[TagConfig]

    @classmethod
    def from_env(cls) -> "ImportTopicsSettings":
        return cls(
            review_agent_api=ReviewAgentApiSettings.from_env(),
            tags=load_tags_config(),
        )
