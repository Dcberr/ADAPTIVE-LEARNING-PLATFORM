import logging
from dataclasses import dataclass
from fastapi import Depends, Request
from openai import OpenAI
from app.agents.logic_agent import LogicAgent
from app.agents.fix_hint_agent import FixHintAgent
from app.agents.improvement_agent import ImprovementAgent
from app.agents.overview_agent import OverviewAgent
from app.agents.review_link_agent import ReviewLinkAgent
from app.agents.scoring_agent import ScoringAgent
from app.config import (
    DEFAULT_FIREWORKS_MODEL,
    DEFAULT_KNOWLEDGE_GRAPH_FIREWORKS_MODEL,
    DEFAULT_REVIEW_FIREWORKS_MODEL,
    Settings,
    get_settings,
)
from app.services.review_code_service import ReviewCodeService


logger = logging.getLogger(__name__)
FIREWORKS_MODEL_REQUIREMENTS = {
    "default": {
        "env": "FIREWORKS_MODEL",
        "default": DEFAULT_FIREWORKS_MODEL,
        "label": "default",
    },
    "review": {
        "env": "REVIEW_FIREWORKS_MODEL",
        "default": DEFAULT_REVIEW_FIREWORKS_MODEL,
        "label": "review",
    },
    "knowledge_graph": {
        "env": "KNOWLEDGE_GRAPH_FIREWORKS_MODEL",
        "default": DEFAULT_KNOWLEDGE_GRAPH_FIREWORKS_MODEL,
        "label": "knowledge graph",
    },
}


@dataclass(frozen=True)
class FireworksRequestConfig:
    model_name: str
    temperature: float
    max_tokens: int


FIREWORKS_REQUEST_PROFILES = {
    "default": {
        "default": {"temperature": 0.2, "max_tokens": 1400},
    },
    "review": {
        "logic": {"temperature": 0.2, "max_tokens": 1800},
        "fix_hint": {"temperature": 0.3, "max_tokens": 700},
        "improvement": {"temperature": 0.2, "max_tokens": 1200},
        "review_link": {"temperature": 0.15, "max_tokens": 900},
        "overview": {"temperature": 0.35, "max_tokens": 700},
        "scoring": {"temperature": 0.1, "max_tokens": 1600},
        "default": {"temperature": 0.2, "max_tokens": 1200},
    },
    "knowledge_graph": {
        "prerequisite_weight": {"temperature": 0.0, "max_tokens": 900},
        "exercise_weight": {"temperature": 0.0, "max_tokens": 1200},
        "default": {"temperature": 0.1, "max_tokens": 900},
    },
}


def get_fireworks_client(request: Request) -> OpenAI:
    client = getattr(request.app.state, "fireworks_client", None)
    if client is None:
        raise RuntimeError("Fireworks client is not initialized on application startup.")
    return client


def get_settings_dependency() -> Settings:
    return get_settings()


def get_fireworks_model_name(
    requirement: str = "default",
    settings: Settings | None = None,
) -> str:
    config = FIREWORKS_MODEL_REQUIREMENTS.get(requirement)
    if config is None:
        raise ValueError(f"Unknown Fireworks model requirement: {requirement}")

    default_model = config["default"]
    label = config["label"]
    resolved_settings = settings or get_settings()
    model_name = resolved_settings.get_fireworks_model_name(requirement)
    if model_name != default_model:
        logger.info(
            "Using %s Fireworks model from settings: %s",
            label,
            model_name,
        )
    else:
        logger.info("Using default %s Fireworks model: %s", label, model_name)
    return model_name


def get_fireworks_request_config(
    requirement: str = "default",
    profile: str = "default",
    settings: Settings | None = None,
) -> FireworksRequestConfig:
    requirement_profiles = FIREWORKS_REQUEST_PROFILES.get(requirement)
    if requirement_profiles is None:
        raise ValueError(f"Unknown Fireworks request requirement: {requirement}")

    profile_config = requirement_profiles.get(profile) or requirement_profiles["default"]
    return FireworksRequestConfig(
        model_name=get_fireworks_model_name(requirement, settings=settings),
        temperature=profile_config["temperature"],
        max_tokens=profile_config["max_tokens"],
    )


def get_logic_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> LogicAgent:
    config = get_fireworks_request_config("review", "logic", settings=settings)
    return LogicAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_fix_hint_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> FixHintAgent:
    config = get_fireworks_request_config("review", "fix_hint", settings=settings)
    return FixHintAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_improvement_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> ImprovementAgent:
    config = get_fireworks_request_config("review", "improvement", settings=settings)
    return ImprovementAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_review_link_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> ReviewLinkAgent:
    config = get_fireworks_request_config("review", "review_link", settings=settings)
    return ReviewLinkAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_overview_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> OverviewAgent:
    config = get_fireworks_request_config("review", "overview", settings=settings)
    return OverviewAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_scoring_agent(
    client=Depends(get_fireworks_client),
    settings: Settings = Depends(get_settings_dependency),
) -> ScoringAgent:
    config = get_fireworks_request_config("review", "scoring", settings=settings)
    return ScoringAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


# -----------------------------
# Dependency for ReviewCodeService
# -----------------------------
def get_review_service(
    logic_agent: LogicAgent = Depends(get_logic_agent),
    fix_hint_agent: FixHintAgent = Depends(get_fix_hint_agent),
    improvement_agent: ImprovementAgent = Depends(get_improvement_agent),
    review_link_agent: ReviewLinkAgent = Depends(get_review_link_agent),
    overview_agent: OverviewAgent = Depends(get_overview_agent),
    scoring_agent: ScoringAgent = Depends(get_scoring_agent),
) -> ReviewCodeService:
    return ReviewCodeService(
        logic_agent=logic_agent,
        fix_hint_agent=fix_hint_agent,
        improvement_agent=improvement_agent,
        review_link_agent=review_link_agent,
        overview_agent=overview_agent,
        scoring_agent=scoring_agent,
    )
