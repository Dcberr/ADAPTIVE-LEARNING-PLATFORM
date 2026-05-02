from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from code_review_ai.models.exercise_record import ExerciseRecord

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QdrantSearchResult:
    exercise_id: str
    score: float
    payload: dict[str, Any]


class QdrantRepository:
    def __init__(
        self,
        *,
        base_url: str | None,
        api_key: str | None,
        collection_name: str,
        timeout_seconds: float = 5.0,
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = (api_key or "").strip()
        self.collection_name = collection_name.strip()
        self.timeout_seconds = timeout_seconds
        self._initialized_vector_size: int | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.collection_name)

    def check_connection(self) -> None:
        if not self.is_configured:
            return
        self._request("GET", "/collections")

    def upsert_exercises(self, exercises: list[ExerciseRecord]) -> None:
        if not self.is_configured:
            return

        points = []
        vector_size = 0
        for exercise in exercises:
            if not exercise.embedding:
                continue
            vector_size = len(exercise.embedding)
            points.append(
                {
                    "id": exercise.exercise_id,
                    "vector": exercise.embedding,
                    "payload": {
                        "exercise_id": exercise.exercise_id,
                        "slug": exercise.slug,
                        "title": exercise.title,
                        "description": exercise.description,
                        "difficulty": exercise.difficulty,
                        "concept_slugs": exercise.concept_slugs,
                        "embedding_model": exercise.embedding_model,
                    },
                }
            )

        if not points:
            return

        logger.debug(
            "Qdrant upsert_exercises collection=%s exercise_count=%s point_count=%s vector_dim=%s",
            self.collection_name,
            len(exercises),
            len(points),
            vector_size,
        )
        self._ensure_collection(vector_size)
        self._request(
            "PUT",
            f"/collections/{parse.quote(self.collection_name, safe='')}/points?wait=true",
            {"points": points},
        )

    def search_exercises(
        self,
        *,
        query_vector: list[float],
        limit: int,
    ) -> list[QdrantSearchResult]:
        if not self.is_configured or not query_vector or limit <= 0:
            return []

        logger.debug(
            "Qdrant search_exercises params: collection=%s limit=%s vector_dim=%s",
            self.collection_name,
            limit,
            len(query_vector),
        )
        response = self._request(
            "POST",
            f"/collections/{parse.quote(self.collection_name, safe='')}/points/search",
            {
                "vector": query_vector,
                "limit": limit,
                "with_payload": True,
                "with_vector": False,
            },
        )
        rows = response.get("result", [])
        results: list[QdrantSearchResult] = []
        for row in rows:
            payload = row.get("payload") or {}
            exercise_id = str(payload.get("exercise_id") or row.get("id") or "").strip()
            if not exercise_id:
                continue
            results.append(
                QdrantSearchResult(
                    exercise_id=exercise_id,
                    score=float(row.get("score") or 0.0),
                    payload=payload,
                )
            )
        logger.debug(
            "Qdrant search_exercises result_count=%s collection=%s",
            len(results),
            self.collection_name,
        )
        return results

    def _ensure_collection(self, vector_size: int) -> None:
        if self._initialized_vector_size == vector_size:
            return

        collection_path = f"/collections/{parse.quote(self.collection_name, safe='')}"
        try:
            response = self._request("GET", collection_path)
            config = (((response.get("result") or {}).get("config") or {}).get("params") or {})
            vectors = config.get("vectors") or {}
            existing_size = int(vectors.get("size") or 0)
            if existing_size and existing_size != vector_size:
                raise RuntimeError(
                    "Qdrant collection vector size does not match exercise embeddings."
                )
        except RuntimeError as exc:
            if "404" not in str(exc):
                raise
            self._request(
                "PUT",
                collection_path,
                {
                    "vectors": {
                        "size": vector_size,
                        "distance": "Cosine",
                    }
                },
            )
        self._initialized_vector_size = vector_size

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured:
            return {}

        body = None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        debug_payload: dict[str, Any] | None = None
        if payload is not None:
            debug_payload = dict(payload)
            if "vector" in debug_payload:
                vector = debug_payload.pop("vector")
                debug_payload["vector_dim"] = len(vector) if isinstance(vector, list) else None
            if "points" in debug_payload:
                points = debug_payload.get("points") or []
                debug_payload["point_count"] = len(points) if isinstance(points, list) else None
                debug_payload.pop("points", None)
        logger.debug(
            "Qdrant request params: method=%s collection=%s path=%s payload=%s",
            method,
            self.collection_name,
            path,
            debug_payload,
        )

        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8") or "{}"
        except error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Qdrant request failed with status {exc.code}: {body_text}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"Qdrant request failed: {exc.reason}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Qdrant returned invalid JSON.") from exc
