from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
DEFAULT_FIREWORKS_MODEL = "fireworks/deepseek-v3p2"
DEFAULT_REVIEW_FIREWORKS_MODEL = "fireworks/kimi-k2p5"
DEFAULT_KNOWLEDGE_GRAPH_FIREWORKS_MODEL = "fireworks/kimi-k2p5"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    uvicorn_reload: bool = Field(default=False, alias="UVICORN_RELOAD")

    fireworks_api_key: str = Field(alias="FIREWORKS_API_KEY")
    fireworks_base_url: str = Field(
        default=DEFAULT_FIREWORKS_BASE_URL,
        alias="FIREWORKS_BASE_URL",
    )
    fireworks_model: str = Field(
        default=DEFAULT_FIREWORKS_MODEL,
        alias="FIREWORKS_MODEL",
    )
    review_fireworks_model: str = Field(
        default=DEFAULT_REVIEW_FIREWORKS_MODEL,
        alias="REVIEW_FIREWORKS_MODEL",
    )
    knowledge_graph_fireworks_model: str = Field(
        default=DEFAULT_KNOWLEDGE_GRAPH_FIREWORKS_MODEL,
        alias="KNOWLEDGE_GRAPH_FIREWORKS_MODEL",
    )

    neo4j_uri: str | None = Field(default=None, alias="NEO4J_URI")
    neo4j_username: str | None = Field(default=None, alias="NEO4J_USERNAME")
    neo4j_password: str | None = Field(default=None, alias="NEO4J_PASSWORD")

    def get_fireworks_model_name(self, requirement: str = "default") -> str:
        if requirement == "review":
            return self.review_fireworks_model or self.fireworks_model
        if requirement == "knowledge_graph":
            return self.knowledge_graph_fireworks_model or self.fireworks_model
        return self.fireworks_model

    @property
    def neo4j_is_configured(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_username and self.neo4j_password)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
