import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import GraphDatabase
from openai import OpenAI

from .config import get_env_config
from .api.knowledge_graph_route import router as knowledge_graph_router
from .api.recommendation_route import router as recommendation_router
from .api.review_code_route import router as review_router
from .config import get_env_config
from .repositories.qdrant_repository import QdrantRepository

settings = get_env_config()


def _configure_noisy_dependency_loggers() -> None:
    """Keep app debug logs while muting verbose SDK/network internals."""
    for logger_name in (
        "openai",
        "openai._base_client",
        "httpx",
        "httpcore",
        "urllib3",
        "neo4j.notifications",
    ):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_configure_noisy_dependency_loggers()

logger = logging.getLogger(__name__)


def _safe_startup_config_summary(settings) -> dict[str, object]:
    return {
        "host": settings.host,
        "port": settings.port,
        "log_level": settings.log_level,
        "uvicorn_reload": settings.uvicorn_reload,
        "fireworks_base_url": settings.fireworks_base_url,
        "exercise_embedding_model": settings.exercise_embedding_model,
        "neo4j_configured": settings.neo4j_is_configured,
        "neo4j_uri": settings.neo4j_uri or "",
        "qdrant_configured": settings.qdrant_is_configured,
        "qdrant_url": settings.qdrant_url or "",
        "qdrant_collection_name": settings.qdrant_collection_name,
        "qdrant_timeout_seconds": settings.qdrant_timeout_seconds,
        "review_logic_model": settings.get_stage_config("review", "logic").model_name,
        "recommendation_rerank_context_builder_model": settings.get_stage_config(
            "recommendation", "rerank_context_builder"
        ).model_name,
        "recommendation_reranker_model": settings.get_stage_config(
            "recommendation", "reranker"
        ).model_name,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_env_config()
    base_url = settings.fireworks_base_url
    app.state.settings = settings
    logger.info("Startup config: %s", _safe_startup_config_summary(settings))
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
        app.state.neo4j_driver.verify_connectivity()
        logger.info(
            "Initialized Neo4j driver at application startup with uri=%s",
            settings.neo4j_uri,
        )
    else:
        app.state.neo4j_driver = None
        logger.warning("Neo4j environment variables are not fully configured.")

    qdrant_repository = QdrantRepository(
        base_url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection_name,
        timeout_seconds=settings.qdrant_timeout_seconds,
    )
    if qdrant_repository.is_configured:
        qdrant_repository.check_connection()
        app.state.qdrant_repository = qdrant_repository
        logger.info(
            "Initialized Qdrant repository at application startup with base_url=%s collection=%s",
            settings.qdrant_url,
            settings.qdrant_collection_name,
        )
    else:
        app.state.qdrant_repository = None
        logger.warning("Qdrant environment variables are not fully configured.")

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
