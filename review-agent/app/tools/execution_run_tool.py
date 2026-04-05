import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CODEREVIEW_API_BASE_URL = "http://localhost:8080"
DEFAULT_TIMEOUT_SECONDS = 30.0


def _ensure_openapi_client_importable() -> None:
    """Make the generated OpenAPI package importable at runtime."""
    client_root = Path(__file__).resolve().parents[1] / "clients" / "codereview"
    client_root_str = str(client_root)

    if client_root_str not in sys.path:
        sys.path.insert(0, client_root_str)


def _build_execution_api(
    *,
    base_url: str,
    access_token: str | None,
):
    _ensure_openapi_client_importable()

    from app.clients.codereview.openapi_client.api.execution_api import ExecutionApi
    from app.clients.codereview.openapi_client.api_client import ApiClient
    from app.clients.codereview.openapi_client.configuration import Configuration

    configuration = Configuration(host=base_url, access_token=access_token)
    return ExecutionApi, ApiClient, configuration


def run_code(
    *,
    language: str,
    code: str,
    stdin: str = "",
    base_url: str | None = None,
    access_token: str | None = None,
    request_timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """
    Call the code-review API `/execution/run` endpoint and return the response as a dict.

    Environment variables:
    - `CODEREVIEW_API_BASE_URL`
    - `CODEREVIEW_API_TOKEN`
    """
    resolved_base_url = base_url or os.getenv(
        "CODEREVIEW_API_BASE_URL", DEFAULT_CODEREVIEW_API_BASE_URL
    )
    resolved_access_token = access_token or os.getenv("CODEREVIEW_API_TOKEN")

    execution_api_cls, api_client_cls, configuration = _build_execution_api(
        base_url=resolved_base_url,
        access_token=resolved_access_token,
    )

    with api_client_cls(configuration) as api_client:
        from app.clients.codereview.openapi_client.models.run_code_request import (
            RunCodeRequest,
        )

        execution_api = execution_api_cls(api_client)
        response = execution_api.run(
            RunCodeRequest(language=language, code=code, input=stdin),
            _request_timeout=request_timeout,
        )
        return response.to_dict()


@dataclass(slots=True)
class ExecutionRunTool:
    """Small wrapper object agents can hold and call repeatedly."""

    base_url: str = DEFAULT_CODEREVIEW_API_BASE_URL
    access_token: str | None = None
    request_timeout: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "ExecutionRunTool":
        return cls(
            base_url=os.getenv(
                "CODEREVIEW_API_BASE_URL", DEFAULT_CODEREVIEW_API_BASE_URL
            ),
            access_token=os.getenv("CODEREVIEW_API_TOKEN"),
        )

    def run_code(self, *, language: str, code: str, stdin: str = "") -> dict[str, Any]:
        return run_code(
            language=language,
            code=code,
            stdin=stdin,
            base_url=self.base_url,
            access_token=self.access_token,
            request_timeout=self.request_timeout,
        )
