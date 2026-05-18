from __future__ import annotations

import json
from typing import Any

from code_review_ai.api.recommendation_schema import (
    RecommendationReviewRequest,
    RecommendationSubmissionRequest,
)
from code_review_ai.models.submission_record import SubmissionRecord
from code_review_ai.repositories.neo4j_repository import Neo4jRepository


TOOL_NAME = "get_student_submission_history"


def build_tool_definition() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": (
                "Fetch submission attempt history tied to the current submission context "
                "to sharpen rerank context. Use the filter argument to control history size "
                "and whether code previews are included."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier for submission history lookup.",
                    },
                    "filter": {
                        "type": "object",
                        "properties": {
                            "history_limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                                "description": "Maximum number of submission history items to fetch.",
                            },
                            "include_code": {
                                "type": "boolean",
                                "description": "Whether submission history should include a short code preview.",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "required": ["student_id"],
                "additionalProperties": False,
            },
        },
    }


def execute(
    *,
    raw_arguments: str,
    neo4j_repository: Neo4jRepository,
    current_review: RecommendationReviewRequest | None,
    current_submission: RecommendationSubmissionRequest | None,
) -> dict[str, Any]:
    try:
        arguments = json.loads(raw_arguments or "{}")
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "Tool arguments were not valid JSON.",
        }

    student_id = str(arguments.get("student_id", "")).strip()
    filter_args = arguments.get("filter") or {}
    history_limit = _bounded_history_limit(filter_args.get("history_limit"))
    include_code = bool(filter_args.get("include_code", False))

    result: dict[str, Any] = {
        "ok": True,
        "student_id": student_id,
        "filter": {
            "history_limit": history_limit,
            "include_code": include_code,
        },
        "submission_history": [],
    }
    if not student_id:
        result["ok"] = False
        result["error"] = "student_id is required."
        return result

    submission_id = (
        current_submission.submission_id.strip()
        if current_submission and current_submission.submission_id.strip()
        else (
            current_review.submission_id.strip()
            if current_review and hasattr(current_review, "submission_id")
            else ""
        )
    )
    if not submission_id:
        result["ok"] = False
        result["error"] = (
            "No current submission_id was available for submission history lookup."
        )
        return result

    try:
        submission_context = neo4j_repository.fetch_submission_history_context(
            submission_id=submission_id,
            history_limit=history_limit,
        )
        result["submission_history"] = [
            _serialize_submission_record(
                submission,
                include_code=include_code,
            )
            for submission in submission_context.get("submission_history", [])
        ]
    except Exception as exc:
        result["ok"] = False
        result["error"] = str(exc)

    return result


def _serialize_submission_record(
    submission: SubmissionRecord,
    *,
    include_code: bool,
) -> dict[str, Any]:
    payload = {
        "submission_id": submission.submission_id,
        "exercise_id": submission.exercise_id,
        "created_at": submission.created_at,
        "testcase_outputs": [
            testcase.model_dump() for testcase in submission.testcase_outputs[:8]
        ],
    }
    if include_code:
        payload["code_preview"] = _code_preview(submission.code)
    return payload


def _code_preview(code: str, max_lines: int = 8) -> str:
    lines = [line.rstrip() for line in code.splitlines() if line.strip()]
    return "\n".join(lines[:max_lines]).strip()


def _bounded_history_limit(value: Any) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return 3
    return max(1, min(limit, 10))
