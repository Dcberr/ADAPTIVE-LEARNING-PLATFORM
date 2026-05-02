from fastapi import Depends, HTTPException, Request
from neo4j import Driver, GraphDatabase

from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from code_review_ai.api.review_code_deps import get_settings_dependency
from code_review_ai.config import EnvConfig, get_env_config
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.repositories.qdrant_repository import (
    QdrantRepository,
)
from code_review_ai.services.exercise_embedding_service import (
    ExerciseEmbeddingService,
)
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.services.exercise_vector_service import ExerciseVectorService
from code_review_ai.services.knowledge_graph_service import (
    KnowledgeGraphService,
)
from code_review_ai.utils.fireworks_embedding_client import FireworksEmbeddingClient


def get_neo4j_driver(request: Request) -> Driver:
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        driver = _initialize_neo4j_driver(request)
    return driver


def get_neo4j_repository(request: Request) -> Neo4jRepository:
    return Neo4jRepository(driver=get_neo4j_driver(request))


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
    driver.verify_connectivity()
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


def get_qdrant_repository(
    request: Request,
    settings: EnvConfig = Depends(get_settings_dependency),
) -> QdrantRepository:
    repository = getattr(request.app.state, "qdrant_repository", None)
    if repository is not None:
        return repository
    return _initialize_qdrant_repository(request=request, settings=settings)


def _initialize_qdrant_repository(
    *,
    request: Request,
    settings: EnvConfig,
) -> QdrantRepository:
    repository = QdrantRepository(
        base_url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection_name,
        timeout_seconds=settings.qdrant_timeout_seconds,
    )
    if not repository.is_configured:
        raise HTTPException(
            status_code=503,
            detail=(
                "Qdrant is not configured. Set QDRANT_URL and "
                "QDRANT_COLLECTION_NAME before using vector-backed endpoints."
            ),
        )
    repository.check_connection()
    request.app.state.qdrant_repository = repository
    return repository


def get_exercise_vector_service(
    settings: EnvConfig = Depends(get_settings_dependency),
    repository: QdrantRepository = Depends(get_qdrant_repository),
) -> ExerciseVectorService:
    return ExerciseVectorService(
        repository=repository,
        embedding_client=FireworksEmbeddingClient(
            api_key=settings.fireworks_api_key,
            base_url=settings.fireworks_base_url,
        ),
        model_name=settings.exercise_embedding_model,
    )


def get_knowledge_graph_service(
    neo4j_repository: Neo4jRepository = Depends(get_neo4j_repository),
    exercise_embedding_service: ExerciseEmbeddingService = Depends(
        get_exercise_embedding_service
    ),
    exercise_vector_service: ExerciseVectorService = Depends(
        get_exercise_vector_service
    ),
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
    prerequisite_weight_agent: PrerequisiteWeightAgent = Depends(
        get_prerequisite_weight_agent
    ),
) -> KnowledgeGraphService:
    return KnowledgeGraphService(
        neo4j_repository=neo4j_repository,
        exercise_embedding_service=exercise_embedding_service,
        exercise_vector_service=exercise_vector_service,
        exercise_relation_scoring_service=exercise_relation_scoring_service,
        prerequisite_weight_agent=prerequisite_weight_agent,
    )
