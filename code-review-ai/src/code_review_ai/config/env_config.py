from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from code_review_ai.config.model_config import (
    FireworksFeatureConfig,
    FireworksStageConfig,
    KnowledgeGraphModelConfig,
    RecommendationModelConfig,
    ReviewModelConfig,
)

DEFAULT_FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"


class EnvConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    uvicorn_reload: bool = False
    log_level: str = "INFO"
    exercise_embedding_model: str = "fireworks/qwen3-embedding-8b"

    fireworks_api_key: str
    fireworks_base_url: str = DEFAULT_FIREWORKS_BASE_URL

    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "exercise-recommendations"
    qdrant_timeout_seconds: float = 5.0

    fireworks_stage_configs: FireworksFeatureConfig

    def get_stage_config(
        self, feature: str, stage: str = "default"
    ) -> FireworksStageConfig:
        feature_map = self.fireworks_stage_configs.get_feature_map(feature)
        return feature_map.get(stage) or feature_map["default"]

    @property
    def neo4j_is_configured(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_username and self.neo4j_password)

    @property
    def qdrant_is_configured(self) -> bool:
        return bool(self.qdrant_url and self.qdrant_collection_name)


@lru_cache(maxsize=1)
def get_env_config() -> EnvConfig:
    env_values = {
        **_read_dotenv(".env"),
        **os.environ,
    }
    return build_env_config(env_values)


def build_env_config(env_values: dict[str, object] | None = None) -> EnvConfig:
    resolved_values = env_values or {}
    return EnvConfig(
        host=str(resolved_values.get("HOST", "0.0.0.0")),
        port=int(resolved_values.get("PORT", 8000)),
        uvicorn_reload=str(resolved_values.get("UVICORN_RELOAD", "false")).lower()
        == "true",
        log_level=str(resolved_values.get("LOG_LEVEL", "INFO")).upper(),
        exercise_embedding_model=str(
            resolved_values.get(
                "EXERCISE_EMBEDDING_MODEL", "fireworks/qwen3-embedding-8b"
            )
        ),
        fireworks_api_key=str(resolved_values.get("FIREWORKS_API_KEY", "")),
        fireworks_base_url=str(
            resolved_values.get("FIREWORKS_BASE_URL", DEFAULT_FIREWORKS_BASE_URL)
        ),
        neo4j_uri=_optional_env(resolved_values, "NEO4J_URI"),
        neo4j_username=_optional_env(resolved_values, "NEO4J_USERNAME"),
        neo4j_password=_optional_env(resolved_values, "NEO4J_PASSWORD"),
        qdrant_url=_optional_env(resolved_values, "QDRANT_URL"),
        qdrant_api_key=_optional_env(resolved_values, "QDRANT_API_KEY"),
        qdrant_collection_name=str(
            resolved_values.get("QDRANT_COLLECTION_NAME", "exercise-recommendations")
        ),
        qdrant_timeout_seconds=_optional_float(
            resolved_values, "QDRANT_TIMEOUT_SECONDS", 5.0
        ),
        fireworks_stage_configs=_build_stage_configs(resolved_values),
    )


def get_settings() -> EnvConfig:
    return get_env_config()


def clear_env_config_cache() -> None:
    get_env_config.cache_clear()


def _build_stage_configs(env_values: dict[str, object]) -> FireworksFeatureConfig:
    defaults = FireworksFeatureConfig()
    feature_maps = {
        "review": defaults.review.as_stage_map(),
        "knowledge_graph": defaults.knowledge_graph.as_stage_map(),
        "recommendation": defaults.recommendation.as_stage_map(),
    }
    feature_configs: dict[str, dict[str, FireworksStageConfig]] = {}

    for feature, stage_defaults in feature_maps.items():
        feature_prefix = feature.upper()
        feature_default = stage_defaults["default"]
        feature_default_model = str(
            env_values.get(f"{feature_prefix}_MODEL", feature_default.model_name)
        )
        stage_configs: dict[str, FireworksStageConfig] = {}
        for stage, stage_default in stage_defaults.items():
            stage_prefix = f"{feature_prefix}_{stage.upper()}"
            model_name = str(
                env_values.get(
                    f"{stage_prefix}_MODEL",
                    env_values.get(
                        f"{feature_prefix}_{stage.upper()}_FIREWORKS_MODEL",
                        feature_default_model,
                    ),
                )
            )
            stage_configs[stage] = FireworksStageConfig(
                model_name=model_name or feature_default.model_name,
                temperature=_optional_float(
                    env_values, f"{stage_prefix}_TEMPERATURE", stage_default.temperature
                ),
                max_tokens=_optional_int(
                    env_values, f"{stage_prefix}_MAX_TOKENS", stage_default.max_tokens
                ),
            )
        feature_configs[feature] = stage_configs

    return FireworksFeatureConfig(
        review=_build_review_model_config(feature_configs["review"]),
        knowledge_graph=_build_knowledge_graph_model_config(
            feature_configs["knowledge_graph"]
        ),
        recommendation=_build_recommendation_model_config(
            feature_configs["recommendation"]
        ),
    )


def _build_review_model_config(stage_configs: dict[str, FireworksStageConfig]):
    return ReviewModelConfig(
        logic=stage_configs["logic"],
        fix_hint=stage_configs["fix_hint"],
        improvement=stage_configs["improvement"],
        review_link=stage_configs["review_link"],
        overview=stage_configs["overview"],
        scoring=stage_configs["scoring"],
        default=stage_configs["default"],
    )


def _build_knowledge_graph_model_config(stage_configs: dict[str, FireworksStageConfig]):
    return KnowledgeGraphModelConfig(
        prerequisite_weight=stage_configs["prerequisite_weight"],
        exercise_weight=stage_configs["exercise_weight"],
        default=stage_configs["default"],
    )


def _build_recommendation_model_config(stage_configs: dict[str, FireworksStageConfig]):
    return RecommendationModelConfig(
        rerank_context_builder=stage_configs["rerank_context_builder"],
        reranker=stage_configs["reranker"],
        explanation_builder=stage_configs["explanation_builder"],
        default=stage_configs["default"],
    )


def _optional_env(env_values: dict[str, object], key: str) -> str | None:
    value = env_values.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_float(env_values: dict[str, object], key: str, fallback: float) -> float:
    value = env_values.get(key)
    if value is None:
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _optional_int(env_values: dict[str, object], key: str, fallback: int) -> int:
    value = env_values.get(key)
    if value is None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _read_dotenv(path: str) -> dict[str, str]:
    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values
