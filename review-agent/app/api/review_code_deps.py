import os
import logging
from fastapi import Depends, Request
from openai import OpenAI
from app.agents.logic_agent import LogicAgent
from app.agents.concept_mapping_agent import ConceptMappingAgent
from app.agents.fix_hint_agent import FixHintAgent
from app.agents.improvement_agent import ImprovementAgent
from app.agents.overview_agent import OverviewAgent
from app.agents.scoring_agent import ScoringAgent
from app.services.review_code_service import ReviewCodeService


logger = logging.getLogger(__name__)

DEFAULT_FIREWORKS_MODEL = "fireworks/deepseek-v3p2"


def get_fireworks_client(request: Request) -> OpenAI:
    client = getattr(request.app.state, "fireworks_client", None)
    if client is None:
        raise RuntimeError("Fireworks client is not initialized on application startup.")
    return client


def get_fireworks_model_name() -> str:
    model_name = os.environ.get("FIREWORKS_MODEL", DEFAULT_FIREWORKS_MODEL)
    if model_name != DEFAULT_FIREWORKS_MODEL:
        logger.info("Using FIREWORKS_MODEL from environment: %s", model_name)
    else:
        logger.info("Using default Fireworks model: %s", model_name)
    return model_name


def get_logic_agent(client=Depends(get_fireworks_client)) -> LogicAgent:
    return LogicAgent(
        client=client,
        model_name=get_fireworks_model_name(),
    )


def get_concept_mapping_agent(
    client=Depends(get_fireworks_client),
) -> ConceptMappingAgent:
    return ConceptMappingAgent(client=client, model_name=get_fireworks_model_name())


def get_fix_hint_agent(client=Depends(get_fireworks_client)) -> FixHintAgent:
    return FixHintAgent(client=client, model_name=get_fireworks_model_name())


def get_improvement_agent(client=Depends(get_fireworks_client)) -> ImprovementAgent:
    return ImprovementAgent(client=client, model_name=get_fireworks_model_name())


def get_overview_agent(client=Depends(get_fireworks_client)) -> OverviewAgent:
    return OverviewAgent(client=client, model_name=get_fireworks_model_name())


def get_scoring_agent(client=Depends(get_fireworks_client)) -> ScoringAgent:
    return ScoringAgent(client=client, model_name=get_fireworks_model_name())


# -----------------------------
# Dependency for ReviewCodeService
# -----------------------------
def get_review_service(
    logic_agent: LogicAgent = Depends(get_logic_agent),
    concept_mapping_agent: ConceptMappingAgent = Depends(get_concept_mapping_agent),
    fix_hint_agent: FixHintAgent = Depends(get_fix_hint_agent),
    improvement_agent: ImprovementAgent = Depends(get_improvement_agent),
    overview_agent: OverviewAgent = Depends(get_overview_agent),
    scoring_agent: ScoringAgent = Depends(get_scoring_agent),
) -> ReviewCodeService:
    return ReviewCodeService(
        logic_agent=logic_agent,
        concept_mapping_agent=concept_mapping_agent,
        fix_hint_agent=fix_hint_agent,
        improvement_agent=improvement_agent,
        overview_agent=overview_agent,
        scoring_agent=scoring_agent,
    )
