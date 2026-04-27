from fastapi import Depends, HTTPException, Request
from neo4j import Driver, GraphDatabase
from openai import OpenAI

from code_review_ai.agents.exercise_weight_agent import ExerciseWeightAgent
from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from code_review_ai.api.review_code_deps import (
    get_fireworks_client,
    get_settings_dependency,
    get_stage_model_config,
)
from code_review_ai.config import EnvConfig, get_env_config
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository


def get_neo4j_driver(request: Request) -> Driver:
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        driver = _initialize_neo4j_driver(request)
    return driver


def get_knowledge_graph_repository(request: Request) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(driver=get_neo4j_driver(request))


def _initialize_neo4j_driver(request: Request) -> Driver:
    settings = getattr(request.app.state, "settings", None) or get_env_config()
    request.app.state.settings = settings

    if not settings.neo4j_is_configured:
        raise HTTPException(
            status_code=503,
            detail=(
                "Neo4j is not configured. Set NEO4J_URI, NEO4J_USERNAME, and "
                "NEO4J_PASSWORD before using knowledge graph endpoints."
            ),
        )

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    request.app.state.neo4j_driver = driver
    return driver


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
