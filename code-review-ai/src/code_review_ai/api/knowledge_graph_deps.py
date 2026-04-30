from fastapi import Depends, HTTPException, Request
from neo4j import Driver, GraphDatabase

from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from code_review_ai.api.review_code_deps import get_settings_dependency
from code_review_ai.config import EnvConfig, get_env_config
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from code_review_ai.services.exercise_embedding_service import (
    ExerciseEmbeddingService,
)
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.utils.fireworks_embedding_client import FireworksEmbeddingClient


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


def get_prerequisite_weight_agent() -> PrerequisiteWeightAgent:
    return PrerequisiteWeightAgent()


def get_exercise_relation_scoring_service() -> ExerciseRelationScoringService:
    return ExerciseRelationScoringService()


def get_exercise_embedding_service(
    settings: EnvConfig = Depends(get_settings_dependency),
) -> ExerciseEmbeddingService:
    return ExerciseEmbeddingService(
        client=FireworksEmbeddingClient(
            api_key=settings.fireworks_api_key,
            base_url=settings.fireworks_base_url,
        ),
        model_name=settings.exercise_embedding_model,
    )
