import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from openai import OpenAI

from .api.review_code_route import router as review_router

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
DEFAULT_FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        raise ValueError("Environment variable FIREWORKS_API_KEY is not set.")

    base_url = os.environ.get("FIREWORKS_BASE_URL", DEFAULT_FIREWORKS_BASE_URL)
    app.state.fireworks_client = OpenAI(api_key=api_key, base_url=base_url)
    logger.info("Initialized Fireworks client at application startup with base_url=%s", base_url)

    yield


def create_app():
    app = FastAPI(title="Code Review API", lifespan=lifespan)

    app.include_router(router=review_router, prefix="/api/v1")

    return app
