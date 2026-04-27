import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import GraphDatabase
from openai import OpenAI

from .config import get_env_config
from .api.knowledge_graph_route import router as knowledge_graph_router
from .api.recommendation_route import router as recommendation_router
from .api.review_code_route import router as review_router

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_env_config()
    base_url = settings.fireworks_base_url
    app.state.settings = settings
    app.state.fireworks_client = OpenAI(
        api_key=settings.fireworks_api_key,
        base_url=base_url,
    )
    logger.info("Initialized Fireworks client at application startup with base_url=%s", base_url)

    if settings.neo4j_is_configured:
        app.state.neo4j_driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
        logger.info(
            "Initialized Neo4j driver at application startup with uri=%s",
            settings.neo4j_uri,
        )
    else:
        app.state.neo4j_driver = None
        logger.warning("Neo4j environment variables are not fully configured.")

    yield

    driver = getattr(app.state, "neo4j_driver", None)
    if driver is not None:
        driver.close()


def create_app():
    app = FastAPI(title="CodeReviewAI API", lifespan=lifespan)

    app.include_router(router=review_router, prefix="/api/v1")
    app.include_router(router=recommendation_router, prefix="/api/v1")
    app.include_router(router=knowledge_graph_router, prefix="/api/v1")

    return app
