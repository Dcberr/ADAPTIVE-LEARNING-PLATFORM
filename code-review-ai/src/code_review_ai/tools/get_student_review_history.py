from __future__ import annotations

import json
from typing import Any

from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.repositories.neo4j_repository import Neo4jRepository


TOOL_NAME = "get_student_review_history"


def build_tool_definition() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": (
                "Fetch stored review history for a student to sharpen rerank context. "
                "Use the filter argument to limit the concept scope and history size."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier for review history lookup.",
                    },
                    "filter": {
                        "type": "object",
                        "properties": {
                            "history_limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                                "description": "Maximum number of review history items to fetch.",
                            },
                            "concept_id": {
                                "type": "string",
                                "description": "Optional concept filter for review history.",
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
    default_focus_concept_id: str,
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
    concept_id = str(
        filter_args.get("concept_id", "") or default_focus_concept_id
    ).strip()

    result: dict[str, Any] = {
        "ok": True,
        "student_id": student_id,
        "filter": {
            "history_limit": history_limit,
            "concept_id": concept_id,
        },
        "review_history": [],
    }
    if not student_id:
        result["ok"] = False
        result["error"] = "student_id is required."
        return result

    try:
        latest_review, review_history = neo4j_repository.get_latest_review_with_history(
            student_id=student_id,
            current_concept=concept_id,
            history_limit=history_limit,
        )
        result["latest_stored_review"] = {
            "review_id": latest_review.review_id,
            "summary": latest_review.summary,
            "detail": latest_review.detail,
        }
        result["review_history"] = [
            _serialize_review_record(review) for review in review_history
        ]
    except Exception as exc:
        result["ok"] = False
        result["error"] = str(exc)

    return result


def _serialize_review_record(review: ReviewRecord) -> dict[str, Any]:
    return {
        "review_id": review.review_id,
        "exercise_id": review.exercise_id,
        "submission_id": review.submission_id,
        "current_concept": review.current_concept,
        "created_at": review.created_at,
        "summary": review.summary,
        "detail_preview": review.detail[:320],
    }


def _bounded_history_limit(value: Any) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return 3
    return max(1, min(limit, 10))
