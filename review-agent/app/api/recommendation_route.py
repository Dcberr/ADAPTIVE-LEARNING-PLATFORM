import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.recommendation_deps import get_recommendation_service
from app.api.recommendation_schema import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/recommendation", response_model=RecommendationResponse)
async def generate_recommendation(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    try:
        return recommendation_service.generate_recommendation(request)
    except Exception as exc:
        logger.exception("Recommendation process failed")
        raise HTTPException(
            status_code=500, detail=f"Recommendation process failed: {exc}"
        )
