from fastapi import FastAPI
from .api.review_code_route import router as review_router
import logging

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app():
    app = FastAPI(title="Code Review API")

    app.include_router(router=review_router, prefix="/api/v1")

    return app
