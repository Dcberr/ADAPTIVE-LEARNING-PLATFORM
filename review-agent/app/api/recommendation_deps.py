from fastapi import Depends
from openai import OpenAI

from app.api.knowledge_graph_deps import get_knowledge_graph_repository
from app.api.review_code_deps import get_fireworks_client, get_fireworks_model_name
from app.services.knowledge_graph_repository import KnowledgeGraphRepository
from app.services.recommendation_service import RecommendationService


def get_recommendation_service(
    knowledge_graph_repository: KnowledgeGraphRepository = Depends(
        get_knowledge_graph_repository
    ),
    client: OpenAI = Depends(get_fireworks_client),
) -> RecommendationService:
    return RecommendationService(
        knowledge_graph_repository=knowledge_graph_repository,
        client=client,
        model_name=get_fireworks_model_name(),
    )
