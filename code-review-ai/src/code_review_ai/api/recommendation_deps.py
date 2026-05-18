from fastapi import Depends
from openai import OpenAI

from code_review_ai.api.knowledge_graph_deps import (
    get_exercise_relation_scoring_service,
    get_exercise_vector_service,
    get_neo4j_repository,
)
from code_review_ai.api.review_code_deps import (
    get_fireworks_client,
    get_settings_dependency,
    get_stage_model_config,
)
from code_review_ai.config import EnvConfig
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.services.exercise_vector_service import ExerciseVectorService
from code_review_ai.services.recommendation_service import RecommendationService


def get_recommendation_service(
    neo4j_repository: Neo4jRepository = Depends(get_neo4j_repository),
    exercise_vector_service: ExerciseVectorService = Depends(get_exercise_vector_service),
    exercise_relation_scoring_service: ExerciseRelationScoringService = Depends(
        get_exercise_relation_scoring_service
    ),
    client: OpenAI = Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> RecommendationService:
    return RecommendationService(
        neo4j_repository=neo4j_repository,
        exercise_vector_service=exercise_vector_service,
        exercise_relation_scoring_service=exercise_relation_scoring_service,
        client=client,
        fireworks_api_key=settings.fireworks_api_key,
        fireworks_base_url=settings.fireworks_base_url,
        fireworks_rerank_base_url=settings.fireworks_rerank_base_url,
        rerank_context_builder_stage_config=get_stage_model_config(
            "recommendation", "rerank_context_builder", settings=settings
        ),
        reranker_stage_config=get_stage_model_config(
            "recommendation", "reranker", settings=settings
        ),
        roadmap_builder_stage_config=get_stage_model_config(
            "recommendation", "roadmap_builder", settings=settings
        ),
    )
