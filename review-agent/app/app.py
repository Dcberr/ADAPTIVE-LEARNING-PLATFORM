import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import GraphDatabase
from openai import OpenAI

from .api.knowledge_graph_route import router as knowledge_graph_router
from .api.recommendation_route import router as recommendation_router
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

    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_username = os.environ.get("NEO4J_USERNAME")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    if neo4j_uri and neo4j_username and neo4j_password:
        app.state.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_username, neo4j_password),
        )
        logger.info("Initialized Neo4j driver at application startup with uri=%s", neo4j_uri)
    else:
        app.state.neo4j_driver = None
        logger.warning("Neo4j environment variables are not fully configured.")

    yield

    driver = getattr(app.state, "neo4j_driver", None)
    if driver is not None:
        driver.close()


def create_app():
    app = FastAPI(title="Code Review API", lifespan=lifespan)

    app.include_router(router=review_router, prefix="/api/v1")
    app.include_router(router=recommendation_router, prefix="/api/v1")
    app.include_router(router=knowledge_graph_router, prefix="/api/v1")

    return app
