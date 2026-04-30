import uvicorn

from code_review_ai.app import create_app
from code_review_ai.config import get_env_config


app = create_app()


def main() -> None:
    settings = get_env_config()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.uvicorn_reload,
    )


if __name__ == "__main__":
    main()
