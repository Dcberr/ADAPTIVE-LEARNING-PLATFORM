from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from code_review_ai.api.recommendation_schema import (
    RecommendationReviewRequest,
    RecommendationSubmissionRequest,
)
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.tools import (
    get_student_review_history,
    get_student_submission_history,
)


@dataclass(frozen=True)
class _ToolRegistration:
    build_definition: callable
    execute: callable


def _review_history_executor(
    *,
    raw_arguments: str,
    neo4j_repository: Neo4jRepository,
    current_review: RecommendationReviewRequest | None,
    current_submission: RecommendationSubmissionRequest | None,
    default_focus_concept_id: str,
) -> dict[str, Any]:
    return get_student_review_history.execute(
        raw_arguments=raw_arguments,
        neo4j_repository=neo4j_repository,
        default_focus_concept_id=default_focus_concept_id,
    )


def _submission_history_executor(
    *,
    raw_arguments: str,
    neo4j_repository: Neo4jRepository,
    current_review: RecommendationReviewRequest | None,
    current_submission: RecommendationSubmissionRequest | None,
    default_focus_concept_id: str,
) -> dict[str, Any]:
    return get_student_submission_history.execute(
        raw_arguments=raw_arguments,
        neo4j_repository=neo4j_repository,
        current_review=current_review,
        current_submission=current_submission,
    )


_TOOL_REGISTRY: dict[str, _ToolRegistration] = {
    get_student_review_history.TOOL_NAME: _ToolRegistration(
        build_definition=get_student_review_history.build_tool_definition,
        execute=_review_history_executor,
    ),
    get_student_submission_history.TOOL_NAME: _ToolRegistration(
        build_definition=get_student_submission_history.build_tool_definition,
        execute=_submission_history_executor,
    ),
}


def build_recommendation_context_tools() -> list[dict[str, Any]]:
    return [
        registration.build_definition()
        for registration in _TOOL_REGISTRY.values()
    ]


def execute_recommendation_context_tool(
    *,
    tool_name: str,
    raw_arguments: str,
    neo4j_repository: Neo4jRepository,
    current_review: RecommendationReviewRequest | None,
    current_submission: RecommendationSubmissionRequest | None,
    default_focus_concept_id: str,
) -> dict[str, Any]:
    registration = _TOOL_REGISTRY.get(tool_name)
    if registration is not None:
        return registration.execute(
            raw_arguments=raw_arguments,
            neo4j_repository=neo4j_repository,
            current_review=current_review,
            current_submission=current_submission,
            default_focus_concept_id=default_focus_concept_id,
        )
    return {
        "ok": False,
        "error": f"Unsupported tool '{tool_name}'",
    }

__all__ = [
    "build_recommendation_context_tools",
    "execute_recommendation_context_tool",
]
