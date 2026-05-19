from __future__ import annotations

from dataclasses import dataclass, field

REVIEW_MODEL = "accounts/fireworks/models/glm-5p1"
REVIEW_OVERVIEW_MODEL = "accounts/fireworks/models/gpt-oss-120b"
RECOMMENDATION_MODEL = "accounts/fireworks/models/kimi-k2p6"
RERANKER_MODEL = "accounts/fireworks/models/qwen3-reranker-8b"


@dataclass(frozen=True)
class FireworksStageConfig:
    model_name: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class ReviewModelConfig:
    logic: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=REVIEW_MODEL,
            temperature=0.1,
            max_tokens=2200,
        )
    )
    fix_hint: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=REVIEW_MODEL,
            temperature=0.25,
            max_tokens=900,
        )
    )
    improvement: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=REVIEW_MODEL,
            temperature=0.15,
            max_tokens=1200,
        )
    )
    review_link: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=REVIEW_MODEL,
            temperature=0.1,
            max_tokens=1000,
        )
    )
    overview: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=REVIEW_OVERVIEW_MODEL,
            temperature=0.12,
            max_tokens=450,
        )
    )

    def as_stage_map(self) -> dict[str, FireworksStageConfig]:
        return {
            "logic": self.logic,
            "fix_hint": self.fix_hint,
            "improvement": self.improvement,
            "review_link": self.review_link,
            "overview": self.overview,
        }


@dataclass(frozen=True)
class RecommendationModelConfig:
    rerank_context_builder: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=RECOMMENDATION_MODEL,
            temperature=0.1,
            max_tokens=1200,
        )
    )
    reranker: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=RERANKER_MODEL,
            temperature=0.0,
            max_tokens=0,
        )
    )
    roadmap_builder: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name=RECOMMENDATION_MODEL,
            temperature=0.2,
            max_tokens=1800,
        )
    )

    def as_stage_map(self) -> dict[str, FireworksStageConfig]:
        return {
            "rerank_context_builder": self.rerank_context_builder,
            "reranker": self.reranker,
            "roadmap_builder": self.roadmap_builder,
        }


@dataclass(frozen=True)
class FireworksFeatureConfig:
    review: ReviewModelConfig = field(default_factory=ReviewModelConfig)
    recommendation: RecommendationModelConfig = field(
        default_factory=RecommendationModelConfig
    )

    def get_feature_map(self, feature: str) -> dict[str, FireworksStageConfig]:
        feature_config = getattr(self, feature, None)
        if feature_config is None:
            raise ValueError(f"Unknown feature model config: {feature}")
        return feature_config.as_stage_map()
