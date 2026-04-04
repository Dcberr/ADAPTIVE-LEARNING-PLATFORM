import os

import uvicorn
from dotenv import load_dotenv


from app.app import create_app


app = create_app()


def main() -> None:
    load_dotenv()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("UVICORN_RELOAD", "false").lower() == "true"

    uvicorn.run(app, host=host, port=port, reload=reload)
