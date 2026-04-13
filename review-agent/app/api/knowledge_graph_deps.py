from fastapi import Depends, Request
from neo4j import Driver
from openai import OpenAI

from app.agents.exercise_weight_agent import ExerciseWeightAgent
from app.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from app.api.review_code_deps import (
    get_fireworks_client,
    get_fireworks_request_config,
)
from app.services.knowledge_graph_repository import KnowledgeGraphRepository


def get_neo4j_driver(request: Request) -> Driver:
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        raise RuntimeError("Neo4j driver is not initialized on application startup.")
    return driver


def get_knowledge_graph_repository(request: Request) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(driver=get_neo4j_driver(request))


def get_prerequisite_weight_agent(
    client: OpenAI = Depends(get_fireworks_client),
) -> PrerequisiteWeightAgent:
    config = get_fireworks_request_config("knowledge_graph", "prerequisite_weight")
    return PrerequisiteWeightAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_exercise_weight_agent(
    client: OpenAI = Depends(get_fireworks_client),
) -> ExerciseWeightAgent:
    config = get_fireworks_request_config("knowledge_graph", "exercise_weight")
    return ExerciseWeightAgent(
        client=client,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
