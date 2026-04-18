from fastapi import Depends, Request
from neo4j import Driver
from openai import OpenAI

from app.agents.exercise_weight_agent import ExerciseWeightAgent
from app.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from app.api.review_code_deps import (
    get_fireworks_client,
    get_settings_dependency,
    get_stage_model_config,
)
from app.config import EnvConfig
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository


def get_neo4j_driver(request: Request) -> Driver:
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        raise RuntimeError("Neo4j driver is not initialized on application startup.")
    return driver


def get_knowledge_graph_repository(request: Request) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(driver=get_neo4j_driver(request))


def get_prerequisite_weight_agent(
    client: OpenAI = Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> PrerequisiteWeightAgent:
    config = get_stage_model_config(
        "knowledge_graph", "prerequisite_weight", settings=settings
    )
    return PrerequisiteWeightAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_exercise_weight_agent(
    client: OpenAI = Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> ExerciseWeightAgent:
    config = get_stage_model_config(
        "knowledge_graph", "exercise_weight", settings=settings
    )
    return ExerciseWeightAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
