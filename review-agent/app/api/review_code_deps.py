import logging
from fastapi import Depends, Request
from openai import OpenAI

from app.agents.fix_hint_agent import FixHintAgent
from app.agents.improvement_agent import ImprovementAgent
from app.agents.logic_agent import LogicAgent
from app.agents.overview_agent import OverviewAgent
from app.agents.review_link_agent import ReviewLinkAgent
from app.agents.scoring_agent import ScoringAgent
from app.config import EnvConfig, FireworksStageConfig, get_env_config
from app.services.review_code_service import ReviewCodeService


logger = logging.getLogger(__name__)


def get_fireworks_client(request: Request) -> OpenAI:
    client = getattr(request.app.state, "fireworks_client", None)
    if client is None:
        raise RuntimeError("Fireworks client is not initialized on application startup.")
    return client


def get_settings_dependency() -> EnvConfig:
    return get_env_config()


def get_stage_model_config(
    feature: str,
    stage: str = "default",
    settings: EnvConfig | None = None,
) -> FireworksStageConfig:
    resolved_settings = settings or get_env_config()
    config = resolved_settings.get_stage_config(feature, stage)
    logger.info(
        "Using Fireworks config for %s.%s: model=%s temperature=%s max_tokens=%s",
        feature,
        stage,
        config.model_name,
        config.temperature,
        config.max_tokens,
    )
    return config


def get_logic_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> LogicAgent:
    config = get_stage_model_config("review", "logic", settings=settings)
    return LogicAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_fix_hint_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> FixHintAgent:
    config = get_stage_model_config("review", "fix_hint", settings=settings)
    return FixHintAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_improvement_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> ImprovementAgent:
    config = get_stage_model_config("review", "improvement", settings=settings)
    return ImprovementAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_review_link_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> ReviewLinkAgent:
    config = get_stage_model_config("review", "review_link", settings=settings)
    return ReviewLinkAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_overview_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> OverviewAgent:
    config = get_stage_model_config("review", "overview", settings=settings)
    return OverviewAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_scoring_agent(
    client=Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> ScoringAgent:
    config = get_stage_model_config("review", "scoring", settings=settings)
    return ScoringAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


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
