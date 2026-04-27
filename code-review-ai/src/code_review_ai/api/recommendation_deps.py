from fastapi import Depends
from openai import OpenAI

from code_review_ai.api.knowledge_graph_deps import get_knowledge_graph_repository
from code_review_ai.api.review_code_deps import (
    get_fireworks_client,
    get_settings_dependency,
    get_stage_model_config,
)
from code_review_ai.config import EnvConfig
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from code_review_ai.services.recommendation_service import RecommendationService


def get_recommendation_service(
    knowledge_graph_repository: KnowledgeGraphRepository = Depends(
        get_knowledge_graph_repository
    ),
    client: OpenAI = Depends(get_fireworks_client),
    settings: EnvConfig = Depends(get_settings_dependency),
) -> RecommendationService:
    return RecommendationService(
        knowledge_graph_repository=knowledge_graph_repository,
        client=client,
        stage_configs={
            "context_planner": get_stage_model_config(
                "recommendation", "context_planner", settings=settings
            ),
            "path_decider": get_stage_model_config(
                "recommendation", "path_decider", settings=settings
            ),
            "roadmap_builder": get_stage_model_config(
                "recommendation", "roadmap_builder", settings=settings
            ),
            "explanation_builder": get_stage_model_config(
                "recommendation", "explanation_builder", settings=settings
            ),
        },
    )
