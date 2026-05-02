from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FireworksStageConfig:
    model_name: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class ReviewModelConfig:
    logic: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/kimi-k2p5",
            temperature=0.1,
            max_tokens=2200,
        )
    )
    fix_hint: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.25,
            max_tokens=900,
        )
    )
    improvement: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/kimi-k2p5",
            temperature=0.15,
            max_tokens=1200,
        )
    )
    review_link: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.1,
            max_tokens=1000,
        )
    )
    overview: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.3,
            max_tokens=950,
        )
    )
    scoring: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.05,
            max_tokens=1800,
        )
    )
    default: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.2,
            max_tokens=1200,
        )
    )

    def as_stage_map(self) -> dict[str, FireworksStageConfig]:
        return {
            "logic": self.logic,
            "fix_hint": self.fix_hint,
            "improvement": self.improvement,
            "review_link": self.review_link,
            "overview": self.overview,
            "scoring": self.scoring,
            "default": self.default,
        }


@dataclass(frozen=True)
class KnowledgeGraphModelConfig:
    prerequisite_weight: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/qwen3-8b",
            temperature=0.0,
            max_tokens=400,
        )
    )
    exercise_weight: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/qwen3-8b",
            temperature=0.0,
            max_tokens=700,
        )
    )
    default: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/qwen3-8b",
            temperature=0.1,
            max_tokens=400,
        )
    )

    def as_stage_map(self) -> dict[str, FireworksStageConfig]:
        return {
            "prerequisite_weight": self.prerequisite_weight,
            "exercise_weight": self.exercise_weight,
            "default": self.default,
        }


@dataclass(frozen=True)
class RecommendationModelConfig:
    rerank_context_builder: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.1,
            max_tokens=1200,
        )
    )
    reranker: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="accounts/fireworks/models/qwen3-reranker-8b",
            temperature=0.0,
            max_tokens=0,
        )
    )
    roadmap_builder: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.2,
            max_tokens=1800,
        )
    )
    default: FireworksStageConfig = field(
        default_factory=lambda: FireworksStageConfig(
            model_name="fireworks/deepseek-v3p2",
            temperature=0.2,
            max_tokens=1400,
        )
    )

    def as_stage_map(self) -> dict[str, FireworksStageConfig]:
        return {
            "rerank_context_builder": self.rerank_context_builder,
            "reranker": self.reranker,
            "roadmap_builder": self.roadmap_builder,
            "default": self.default,
        }


@dataclass(frozen=True)
class FireworksFeatureConfig:
    review: ReviewModelConfig = field(default_factory=ReviewModelConfig)
    knowledge_graph: KnowledgeGraphModelConfig = field(
        default_factory=KnowledgeGraphModelConfig
    )
    recommendation: RecommendationModelConfig = field(
        default_factory=RecommendationModelConfig
    )

    def get_feature_map(self, feature: str) -> dict[str, FireworksStageConfig]:
        feature_config = getattr(self, feature, None)
        if feature_config is None:
            raise ValueError(f"Unknown feature model config: {feature}")
        return feature_config.as_stage_map()
