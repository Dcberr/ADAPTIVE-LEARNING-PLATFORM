import uvicorn

from app.app import create_app
from app.config import get_settings


app = create_app()


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.uvicorn_reload,
    )
