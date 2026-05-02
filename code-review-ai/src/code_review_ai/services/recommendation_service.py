from __future__ import annotations

import json
import logging
from typing import Any, cast

from langgraph.graph import StateGraph
from openai import OpenAI

from code_review_ai.api.recommendation_schema import (
    RecommendationExercise,
    RecommendationRequest,
    RecommendationRoadmapExercise,
    RecommendationRoadmapStep,
    RecommendationResponse,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.recommendation_state import RecommendationState
from code_review_ai.config import FireworksStageConfig
from code_review_ai.prompts.recommendation.rerank_context_builder import (
    build_rerank_context_builder_system_prompt,
    build_rerank_context_finalize_prompt,
    build_rerank_context_plan_prompt,
)
from code_review_ai.prompts.recommendation.roadmap_builder import (
    build_roadmap_builder_prompt,
    build_roadmap_builder_system_prompt,
)
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.repositories.qdrant_repository import QdrantSearchResult
from code_review_ai.services.exercise_relation_scoring_service import (
    ExerciseRelationScoringService,
)
from code_review_ai.services.exercise_vector_service import ExerciseVectorService
from code_review_ai.utils.debug_logging import truncate_text
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.fireworks_rerank_client import (
    FireworksRerankError,
    rerank_documents_with_retry,
)
from code_review_ai.utils.parse_json_response import safe_parse_json_response

logger = logging.getLogger(__name__)


class RecommendationService:
    """Retrieve from graph and vector first, rerank with context, then explain."""

    ROADMAP_POOL_SIZE = 8

    def __init__(
        self,
        neo4j_repository: Neo4jRepository,
        exercise_vector_service: ExerciseVectorService,
        exercise_relation_scoring_service: ExerciseRelationScoringService,
        client: OpenAI,
        fireworks_api_key: str,
        fireworks_base_url: str,
        rerank_context_builder_stage_config: FireworksStageConfig,
        reranker_stage_config: FireworksStageConfig,
        roadmap_builder_stage_config: FireworksStageConfig,
    ):
        self.neo4j_repository = neo4j_repository
        self.exercise_vector_service = exercise_vector_service
        self.exercise_relation_scoring_service = exercise_relation_scoring_service
        self.client = client
        self.fireworks_api_key = fireworks_api_key
        self.fireworks_base_url = fireworks_base_url
        self.rerank_context_builder_stage_config = rerank_context_builder_stage_config
        self.reranker_stage_config = reranker_stage_config
        self.roadmap_builder_stage_config = roadmap_builder_stage_config
        self.workflow = self._build_workflow()

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        logger.debug(
            "Starting recommendation flow for student=%s exercise=%s focus_concepts=%s attempted_count=%s review_present=%s submission_present=%s",
            request.student_id,
            request.exercise.exercise_id,
            request.focus_concept_ids,
            len(request.attempted_exercise_ids),
            bool(request.review),
            bool(request.submission),
        )
        initial_state: RecommendationState = {
            "student_id": request.student_id,
            "exercise_id": request.exercise.exercise_id,
            "exercise": request.exercise,
            "focus_concept_ids": list(request.focus_concept_ids),
            "review": request.review,
            "submission": request.submission,
            "attempted_exercise_ids": list(request.attempted_exercise_ids),
            "retrieved_candidates": [],
            "rerank_query": {},
            "rerank_overview": "",
            "reranked_candidates": [],
            "roadmap_summary": "",
            "roadmap_steps": [],
        }

        logger.debug(
            "Initial recommendation state summary: %s",
            self._summarize_state(initial_state),
        )
        final_state = cast(RecommendationState, self.workflow.invoke(initial_state))
        logger.debug(
            "Recommendation workflow finished with state summary: %s",
            self._summarize_state(final_state),
        )
        if not final_state["reranked_candidates"]:
            raise ValueError("No exercises found for this recommendation result.")

        roadmap_summary = str(final_state.get("roadmap_summary", "")).strip()
        roadmap_steps = list(final_state.get("roadmap_steps", []))
        if not roadmap_steps:
            roadmap_summary, roadmap_steps = self._fallback_roadmap(
                final_state,
                final_state["reranked_candidates"][: self.ROADMAP_POOL_SIZE],
            )

        selected_exercise_ids: list[str] = []
        for step in roadmap_steps:
            for item in step.get("exercises", []):
                exercise_id = str(item.get("exercise_id", "")).strip()
                if exercise_id and exercise_id not in selected_exercise_ids:
                    selected_exercise_ids.append(exercise_id)
        selected_candidate_map = {
            candidate["exercise"].exercise_id: candidate
            for candidate in final_state["reranked_candidates"]
        }
        selected_candidates = [
            selected_candidate_map[exercise_id]
            for exercise_id in selected_exercise_ids
            if exercise_id in selected_candidate_map
        ]
        selected_exercises = [
            candidate["exercise"] for candidate in selected_candidates
        ]
        logger.debug(
            "Selected roadmap exercises: %s",
            [exercise.exercise_id for exercise in selected_exercises],
        )

        self.neo4j_repository.store_recommendation_roadmap(
            student_id=final_state["student_id"],
            assigned_path="IMPROVE",
            target_concept=self._primary_focus_concept(final_state),
            exercise_ids=[exercise.exercise_id for exercise in selected_exercises],
            review_id=None,
        )
        exercise_ids_for_response = list(dict.fromkeys(selected_exercise_ids))
        exercise_concept_map = self.neo4j_repository.get_concept_ids_by_exercise(
            exercise_ids_for_response
        )
        exercise_map = self._resolve_roadmap_exercises(
            selected_exercise_ids=exercise_ids_for_response,
            candidate_map=selected_candidate_map,
        )

        return RecommendationResponse(
            student_id=final_state["student_id"],
            current_exercise_id=final_state["exercise_id"],
            focus_concept_ids=final_state["focus_concept_ids"],
            summary=roadmap_summary,
            roadmap=self._build_response_roadmap(
                roadmap_steps=roadmap_steps,
                candidate_map=selected_candidate_map,
                exercise_map=exercise_map,
                exercise_concept_map=exercise_concept_map,
            ),
        )

    def _build_workflow(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node(
            "candidate_retriever",
            self._instrument_node("candidate_retriever", self._candidate_retriever),
        )
        workflow.add_node(
            "rerank_context_builder",
            self._instrument_node(
                "rerank_context_builder", self._rerank_context_builder
            ),
        )
        workflow.add_node(
            "candidate_ranker",
            self._instrument_node("candidate_ranker", self._candidate_ranker),
        )
        workflow.add_node(
            "roadmap_builder",
            self._instrument_node("roadmap_builder", self._roadmap_builder),
        )
        workflow.set_entry_point("candidate_retriever")
        workflow.add_edge("candidate_retriever", "rerank_context_builder")
        workflow.add_edge("rerank_context_builder", "candidate_ranker")
        workflow.add_edge("candidate_ranker", "roadmap_builder")
        workflow.set_finish_point("roadmap_builder")
        return workflow.compile()

    def _candidate_retriever(self, state: RecommendationState) -> RecommendationState:
        focus_concept_ids = state["focus_concept_ids"]
        graph_limit, vector_limit = self._source_candidate_limits(state)
        logger.debug(
            "Candidate retrieval started for exercise=%s focus_concepts=%s graph_limit=%s vector_limit=%s attempted_count=%s",
            state["exercise_id"],
            focus_concept_ids,
            graph_limit,
            vector_limit,
            len(state["attempted_exercise_ids"]),
        )

        graph_candidates = self.neo4j_repository.retrieve_candidates(
            current_exercise_id=state["exercise_id"],
            target_concept_ids=focus_concept_ids,
            attempted_exercise_ids=state["attempted_exercise_ids"],
            limit=graph_limit,
        )
        graph_candidates = self._recalculate_non_direct_graph_candidates(
            state=state,
            graph_candidates=graph_candidates,
        )
        logger.debug(
            "Graph retrieval returned %s candidates: %s",
            len(graph_candidates),
            self._candidate_ids(graph_candidates),
        )

        vector_candidates: list[dict[str, Any]] = []
        if self.exercise_vector_service.is_enabled and vector_limit > 0:
            try:
                excluded_vector_ids = {
                    state["exercise_id"],
                    *state["attempted_exercise_ids"],
                }
                vector_hits = self.exercise_vector_service.search_exercises(
                    query_text=self._build_vector_query_text(state),
                    limit=vector_limit,
                )
                vector_hit_map = {
                    hit.exercise_id: hit.score
                    for hit in vector_hits
                    if hit.exercise_id not in excluded_vector_ids
                }
                logger.debug(
                    "Vector search returned %s hits, %s remained after exclusions: %s",
                    len(vector_hits),
                    len(vector_hit_map),
                    list(vector_hit_map.keys()),
                )
                if vector_hit_map:
                    vector_candidates = self._build_vector_candidates(
                        state=state,
                        vector_hits=[
                            hit
                            for hit in vector_hits
                            if hit.exercise_id in vector_hit_map
                        ],
                    )
                    logger.debug(
                        "Vector enrichment returned %s candidates: %s",
                        len(vector_candidates),
                        self._candidate_ids(vector_candidates),
                    )
            except Exception:
                logger.exception(
                    "Vector or Neo4j candidate retrieval failed during recommendation flow"
                )
                raise

        candidates = self._merge_candidates(graph_candidates, vector_candidates)
        logger.debug(
            "Merged candidates count=%s ids=%s",
            len(candidates),
            self._candidate_ids(candidates),
        )

        new_state = dict(state)
        new_state["focus_concept_ids"] = list(state["focus_concept_ids"])
        new_state["retrieved_candidates"] = candidates
        new_state["reranked_candidates"] = []
        new_state["roadmap_summary"] = ""
        new_state["roadmap_steps"] = []
        return cast(RecommendationState, new_state)

    def _build_vector_candidates(
        self,
        *,
        state: RecommendationState,
        vector_hits: list[QdrantSearchResult],
    ) -> list[dict[str, Any]]:
        related_exercises = [
            self._exercise_from_vector_hit(hit)
            for hit in vector_hits
            if hit.exercise_id.strip()
        ]
        if not related_exercises:
            return []

        focus_concept_ids = list(state["focus_concept_ids"])
        related_metadata = self._related_metadata_by_exercise(
            state=state,
            related_exercises=related_exercises,
        )

        candidates: list[dict[str, Any]] = []
        for hit, exercise in zip(vector_hits, related_exercises):
            relation_metrics = related_metadata.get(
                exercise.exercise_id,
                self.exercise_relation_scoring_service.DEFAULT_RELATION_METADATA,
            )
            concept_fit = self._concept_fit_weight(
                focus_concept_ids=focus_concept_ids,
                candidate_concept_slugs=exercise.concept_slugs,
            )
            target_concept = self._candidate_target_concept_for_vector(
                focus_concept_ids=focus_concept_ids,
                candidate_concept_slugs=exercise.concept_slugs,
            )
            candidates.append(
                {
                    "target_concept": target_concept,
                    "concept_name": target_concept,
                    "concept_description": "",
                    "recommended_weight": concept_fit,
                    "tests_weight": concept_fit,
                    "related_weight": float(relation_metrics.get("weight", 0.0)),
                    "difficulty_gap": float(
                        relation_metrics.get("difficulty_gap", 0.0)
                    ),
                    "progression_score": float(
                        relation_metrics.get("progression_score", 0.0)
                    ),
                    "similarity_score": float(
                        relation_metrics.get("similarity_score", 0.0)
                    ),
                    "root_connection_mode": "vector",
                    "root_connection_weight": float(
                        relation_metrics.get("weight", 0.0)
                    ),
                    "root_hop_count": 0,
                    "vector_similarity": float(hit.score or 0.0),
                    "retrieval_sources": ["vector"],
                    "exercise": exercise,
                }
            )
        return candidates

    def _recalculate_non_direct_graph_candidates(
        self,
        *,
        state: RecommendationState,
        graph_candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        non_direct_exercises = [
            candidate["exercise"]
            for candidate in graph_candidates
            if str(candidate.get("root_connection_mode", "")).strip().lower()
            == "non-direct"
        ]
        if not non_direct_exercises:
            return graph_candidates

        related_metadata = self._related_metadata_by_exercise(
            state=state,
            related_exercises=non_direct_exercises,
        )
        recalculated: list[dict[str, Any]] = []
        for candidate in graph_candidates:
            if str(candidate.get("root_connection_mode", "")).strip().lower() != "non-direct":
                recalculated.append(candidate)
                continue
            relation_metrics = related_metadata.get(
                candidate["exercise"].exercise_id,
                self.exercise_relation_scoring_service.DEFAULT_RELATION_METADATA,
            )
            recalculated.append(
                {
                    **candidate,
                    "related_weight": float(relation_metrics.get("weight", 0.0)),
                    "difficulty_gap": float(
                        relation_metrics.get("difficulty_gap", 0.0)
                    ),
                    "progression_score": float(
                        relation_metrics.get("progression_score", 0.0)
                    ),
                    "similarity_score": float(
                        relation_metrics.get("similarity_score", 0.0)
                    ),
                }
            )
        return recalculated

    def _related_metadata_by_exercise(
        self,
        *,
        state: RecommendationState,
        related_exercises: list[ExerciseRecord],
    ) -> dict[str, dict[str, Any]]:
        if not related_exercises:
            return {}
        return self.exercise_relation_scoring_service.evaluate(
            main_exercise=state["exercise"],
            concepts=[],
            related_exercises=related_exercises,
            main_concept_slugs=list(state["focus_concept_ids"]),
            related_concept_slugs_by_exercise={
                exercise.exercise_id: list(exercise.concept_slugs)
                for exercise in related_exercises
            },
        )[2]

    @staticmethod
    def _exercise_from_vector_hit(hit: QdrantSearchResult) -> ExerciseRecord:
        payload = hit.payload or {}
        return ExerciseRecord(
            exercise_id=hit.exercise_id,
            slug=str(payload.get("slug", "") or ""),
            title=str(payload.get("title", "") or hit.exercise_id),
            description=str(payload.get("description", "") or ""),
            content=str(payload.get("content", "") or ""),
            difficulty=str(payload.get("difficulty", "") or "medium"),
            concept_slugs=[
                str(concept_slug).strip()
                for concept_slug in (payload.get("concept_slugs") or [])
                if str(concept_slug).strip()
            ],
        )

    @staticmethod
    def _concept_fit_weight(
        *,
        focus_concept_ids: list[str],
        candidate_concept_slugs: list[str],
    ) -> float:
        focus_set = {
            concept_id.strip().lower()
            for concept_id in focus_concept_ids
            if concept_id.strip()
        }
        candidate_set = {
            concept_slug.strip().lower()
            for concept_slug in candidate_concept_slugs
            if concept_slug.strip()
        }
        if not focus_set:
            return 0.7
        if not candidate_set:
            return 0.3
        overlap = len(focus_set & candidate_set) / len(focus_set)
        if overlap >= 0.85:
            return 1.0
        if overlap >= 0.5:
            return 0.7
        return 0.3

    @staticmethod
    def _candidate_target_concept_for_vector(
        *,
        focus_concept_ids: list[str],
        candidate_concept_slugs: list[str],
    ) -> str:
        candidate_lookup = {
            concept_slug.strip().lower(): concept_slug.strip()
            for concept_slug in candidate_concept_slugs
            if concept_slug.strip()
        }
        for concept_id in focus_concept_ids:
            normalized = concept_id.strip().lower()
            if normalized in candidate_lookup:
                return candidate_lookup[normalized]
        if candidate_concept_slugs:
            return candidate_concept_slugs[0].strip()
        return focus_concept_ids[0].strip() if focus_concept_ids else ""

    def _rerank_context_builder(
        self, state: RecommendationState
    ) -> RecommendationState:
        # Testing mode: keep rerank context deterministic and skip the LLM planner/finalizer.
        rerank_query = self._build_rerank_query(state)
        rerank_overview = self._fallback_rerank_overview(state)
        logger.debug(
            "Built rerank context with query keys=%s overview_preview=%s",
            list(rerank_query.keys()),
            rerank_overview[:160],
        )

        new_state = dict(state)
        new_state["rerank_query"] = rerank_query
        new_state["rerank_overview"] = rerank_overview
        return cast(RecommendationState, new_state)

    def _candidate_ranker(self, state: RecommendationState) -> RecommendationState:
        candidates = state["retrieved_candidates"]
        if not candidates:
            logger.debug(
                "Candidate ranker skipped because there are no retrieved candidates"
            )
            return cast(RecommendationState, dict(state))

        reranked_candidates = self._rerank_candidates(state)
        logger.debug(
            "Candidate ranker produced %s candidates in final order: %s",
            len(reranked_candidates),
            self._candidate_ids(reranked_candidates),
        )
        new_state = dict(state)
        new_state["reranked_candidates"] = reranked_candidates
        return cast(RecommendationState, new_state)

    def _roadmap_builder(self, state: RecommendationState) -> RecommendationState:
        pool_candidates = list(state["reranked_candidates"][: self.ROADMAP_POOL_SIZE])
        if not pool_candidates:
            logger.debug("Roadmap builder skipped because reranked pool is empty")
            return cast(RecommendationState, dict(state))

        fallback_summary, fallback_steps = self._fallback_roadmap(
            state, pool_candidates
        )
        roadmap_summary = fallback_summary
        roadmap_steps = fallback_steps
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.roadmap_builder_stage_config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_roadmap_builder_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_roadmap_builder_prompt(
                            roadmap_context=self._build_roadmap_builder_context(
                                state, pool_candidates
                            ),
                            candidate_pool=self._roadmap_candidate_pool(
                                pool_candidates
                            ),
                        ),
                    },
                ],
                temperature=self.roadmap_builder_stage_config.temperature,
                max_tokens=self.roadmap_builder_stage_config.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            roadmap_summary, roadmap_steps = self._normalize_roadmap_response(
                state=state,
                pool_candidates=pool_candidates,
                parsed=parsed,
                fallback_summary=fallback_summary,
                fallback_steps=fallback_steps,
            )
        except Exception:
            logger.exception("Roadmap builder failed, using fallback roadmap")

        logger.debug(
            "Roadmap builder produced %s steps with summary=%s",
            len(roadmap_steps),
            roadmap_summary,
        )
        new_state = dict(state)
        new_state["roadmap_summary"] = roadmap_summary
        new_state["roadmap_steps"] = roadmap_steps
        return cast(RecommendationState, new_state)

    def _rerank_candidates(self, state: RecommendationState) -> list[dict[str, Any]]:
        fallback_candidates = self._fallback_reranked_candidates(state)
        if not fallback_candidates:
            logger.debug("Fallback ranking produced no candidates")
            return fallback_candidates

        logger.debug(
            "Rerank pool count=%s ids=%s",
            len(fallback_candidates),
            self._candidate_ids(fallback_candidates),
        )
        documents = self._build_rerank_documents(state, fallback_candidates)
        query = self._serialize_rerank_query(
            rerank_query=state.get("rerank_query", {}),
            rerank_overview=str(state.get("rerank_overview", "")),
        )
        logger.debug(
            "Submitting %s candidate documents to reranker",
            len(documents),
        )
        try:
            response = rerank_documents_with_retry(
                api_key=self.fireworks_api_key,
                base_url=self.fireworks_base_url,
                model_name=self.reranker_stage_config.model_name,
                query=query,
                documents=documents,
                top_n=len(documents),
                return_documents=False,
                task=(
                    "Rank the candidate exercises for the student's next best coding practice step "
                    "using the provided student context, current exercise context, and candidate evidence."
                ),
            )
        except FireworksRerankError:
            logger.exception("Reranker failed, using fallback candidate order")
            return fallback_candidates

        rerank_scores = {
            int(item.get("index", -1)): float(item.get("relevance_score", 0.0) or 0.0)
            for item in response.get("data", [])
        }
        if not rerank_scores:
            logger.debug("Reranker returned no scores, using fallback candidate order")
            return fallback_candidates
        logger.debug("Reranker scores by index: %s", rerank_scores)

        reranked = [dict(candidate) for candidate in fallback_candidates]
        for index, candidate in enumerate(reranked):
            rerank_score = rerank_scores.get(index, 0.0)
            candidate["rerank_score"] = rerank_score
            candidate["final_score"] = self._clamp_float(
                0.65 * float(candidate.get("final_score", 0.0)) + 0.35 * rerank_score,
                0.0,
            )
        return sorted(
            reranked,
            key=lambda candidate: (
                float(candidate.get("final_score", 0.0)),
                float(candidate.get("rerank_score", 0.0)),
                float(candidate.get("recommended_weight", 0.0)),
            ),
            reverse=True,
        )

    def _build_response_roadmap(
        self,
        *,
        roadmap_steps: list[dict[str, Any]],
        candidate_map: dict[str, dict[str, Any]],
        exercise_map: dict[str, Any],
        exercise_concept_map: dict[str, list[str]],
    ) -> list[RecommendationRoadmapStep]:
        response_steps: list[RecommendationRoadmapStep] = []
        for step_index, step in enumerate(roadmap_steps, start=1):
            response_exercises: list[RecommendationRoadmapExercise] = []
            sorted_items = sorted(
                step.get("exercises", []),
                key=lambda item: int(item.get("priority", 999)),
            )
            for item_index, item in enumerate(sorted_items, start=1):
                exercise_id = str(item.get("exercise_id", "")).strip()
                candidate = candidate_map.get(exercise_id)
                exercise = exercise_map.get(exercise_id)
                if exercise is None:
                    continue
                response_exercises.append(
                    RecommendationRoadmapExercise(
                        priority=int(item.get("priority", item_index) or item_index),
                        reason=str(item.get("reason", "")).strip()
                        or self._reason_for_candidate(candidate or {}),
                        exercise=RecommendationExercise(
                            concept_ids=exercise_concept_map.get(
                                exercise.exercise_id, []
                            ),
                            **exercise.model_dump(),
                        ),
                    )
                )
            if not response_exercises:
                continue
            response_steps.append(
                RecommendationRoadmapStep(
                    step=int(step.get("step", step_index) or step_index),
                    summary=str(step.get("summary", "")).strip()
                    or "Continue with the next recommended practice set.",
                    target_concepts=list(step.get("target_concepts", [])),
                    exercises=response_exercises,
                )
            )
        return response_steps

    def _resolve_roadmap_exercises(
        self,
        *,
        selected_exercise_ids: list[str],
        candidate_map: dict[str, dict[str, Any]],
    ) -> dict[str, ExerciseRecord]:
        exercise_map: dict[str, ExerciseRecord] = {}
        missing_ids: list[str] = []
        for exercise_id in selected_exercise_ids:
            candidate = candidate_map.get(exercise_id)
            exercise = candidate.get("exercise") if candidate else None
            if exercise is not None:
                exercise_map[exercise_id] = exercise
            else:
                missing_ids.append(exercise_id)
        if missing_ids:
            logger.debug(
                "Backfilling %s roadmap exercises from Neo4j: %s",
                len(missing_ids),
                missing_ids,
            )
            exercise_map.update(self.neo4j_repository.get_exercises_by_ids(missing_ids))
        return exercise_map

    def _build_rerank_query(self, state: RecommendationState) -> dict[str, Any]:
        exercise = state["exercise"]
        review = state["review"]

        return {
            "goal": "rank the best next exercises for the student",
            "goal_query": "Rank the best next exercises for the student's current concept.",
            "student_id": state["student_id"],
            "current_exercise_id": state["exercise_id"],
            "focus_concept_ids": state["focus_concept_ids"],
            "current_exercise": {
                "title": getattr(exercise, "title", ""),
                "description": getattr(exercise, "description", ""),
                "difficulty": getattr(exercise, "difficulty", ""),
            },
            "latest_review": {
                "summary": review.summary if review else "",
                "detail": review.detail if review else "",
            },
            "exercise_concepts": exercise.concept_slugs[:5],
        }

    def _plan_rerank_context(self, state: RecommendationState) -> dict[str, Any]:
        base_context = self._llm_base_context_summary(state)
        fallback = {
            "goal_query": "Rank the best next exercises for the student's current concept.",
        }
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.rerank_context_builder_stage_config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_rerank_context_builder_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_rerank_context_plan_prompt(
                            base_context=base_context
                        ),
                    },
                ],
                temperature=self.rerank_context_builder_stage_config.temperature,
                max_tokens=self.rerank_context_builder_stage_config.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            return {
                "goal_query": str(
                    parsed.get("goal_query", fallback["goal_query"])
                ).strip()
                or fallback["goal_query"],
            }
        except Exception:
            return fallback

    def _finalize_rerank_context(
        self,
        state: RecommendationState,
        *,
        planner_goal_query: str,
    ) -> tuple[dict[str, Any], str]:
        base_context = self._llm_base_context_summary(state)
        fallback_query = self._build_rerank_query(state)
        fallback_overview = self._fallback_rerank_overview(
            state,
        )
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.rerank_context_builder_stage_config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_rerank_context_builder_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_rerank_context_finalize_prompt(
                            base_context=base_context,
                            planner_goal_query=planner_goal_query,
                        ),
                    },
                ],
                temperature=self.rerank_context_builder_stage_config.temperature,
                max_tokens=self.rerank_context_builder_stage_config.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            goal_query = (
                str(parsed.get("goal_query", planner_goal_query)).strip()
                or planner_goal_query
            )
            rerank_query = {
                **fallback_query,
                "goal_query": goal_query,
                "query_facets": parsed.get("query_facets") or [],
            }
            rerank_overview = (
                str(parsed.get("student_overview", fallback_overview)).strip()
                or fallback_overview
            )
            return rerank_query, rerank_overview
        except Exception:
            return fallback_query, fallback_overview

    def _llm_base_context_summary(self, state: RecommendationState) -> dict[str, Any]:
        exercise = state["exercise"]
        review = state["review"]
        submission = state["submission"]
        review_items = review.review_items if review else []

        return {
            "goal": "build rerank query and student context for recommendation",
            "student_id": state["student_id"],
            "current_exercise": {
                "exercise_id": state["exercise_id"],
                "title": getattr(exercise, "title", ""),
                "description": getattr(exercise, "description", ""),
                "difficulty": getattr(exercise, "difficulty", ""),
                "concept_slugs": getattr(exercise, "concept_slugs", []),
            },
            "focus_concept": {
                "concept_ids": state["focus_concept_ids"],
            },
            "latest_review": {
                "summary": review.summary if review else "",
                "detail": review.detail if review else "",
                "issues": [
                    {
                        "type": item.type,
                        "issue": item.issue,
                    }
                    for item in review_items[:4]
                ],
            },
            "latest_submission": {
                "submission_id": (submission.submission_id if submission else ""),
                "created_at": submission.created_at if submission else "",
                "code_preview": (
                    self._extract_code_snippet(submission.code)
                    if submission and submission.code.strip()
                    else ""
                ),
                "testcase_output_count": (
                    len(submission.testcases) if submission else 0
                ),
                "testcases": [
                    {
                        "input": testcase.input,
                        "expect": testcase.expect,
                        "output": testcase.output,
                    }
                    for testcase in (submission.testcases if submission else [])
                ][:6],
            },
            "history": {
                "attempted_exercise_count": len(state["attempted_exercise_ids"]),
                "recent_attempted_exercise_ids": state["attempted_exercise_ids"][:5],
            },
            "retrieval": {
                "candidate_count": len(state["retrieved_candidates"]),
            },
        }

    def _fallback_rerank_overview(
        self,
        state: RecommendationState,
    ) -> str:
        exercise = state["exercise"]
        review = state["review"]
        exercise_title = getattr(exercise, "title", state["exercise_id"])
        attempted_count = len(state["attempted_exercise_ids"])
        parts = [
            (
                f"The student is currently working on {exercise_title} and the recommendation "
                f"should stay focused on concepts {', '.join(state['focus_concept_ids']) or 'none'}."
            ),
            f"They have already submitted {attempted_count} prior exercises.",
        ]
        if review and review.summary.strip():
            parts.append(f"The latest review highlights: {review.summary.strip()}")
        return " ".join(parts)

    def _fallback_roadmap(
        self,
        state: RecommendationState,
        pool_candidates: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        remaining = list(pool_candidates)
        steps: list[dict[str, Any]] = []
        difficulty_plans = [
            (
                "easy",
                "Start with close practice that reinforces the main pattern, gives the student a cleaner chance to apply the same idea, and reduces the risk of repeating the current mistake.",
            ),
            (
                "medium",
                "Move into broader follow-up problems that still stay close to the same concepts, but ask for stronger planning and more deliberate control over the solution steps.",
            ),
            (
                "hard",
                "Finish with harder practice that stretches edge-case handling, deeper control of the solution flow, and more stable reasoning under tougher constraints.",
            ),
        ]
        for difficulty, summary in difficulty_plans:
            matching = [
                candidate
                for candidate in remaining
                if self._normalize_difficulty(candidate["exercise"].difficulty)
                == difficulty
            ]
            selected = matching[:2]
            if not selected:
                continue
            for candidate in selected:
                remaining.remove(candidate)
            steps.append(
                {
                    "step": len(steps) + 1,
                    "summary": summary,
                    "target_concepts": self._merge_target_concepts(state, selected),
                    "exercises": [
                        {
                            "exercise_id": candidate["exercise"].exercise_id,
                            "priority": index,
                            "reason": self._reason_for_candidate(candidate),
                        }
                        for index, candidate in enumerate(selected, start=1)
                    ],
                }
            )

        while remaining and len(steps) < 3:
            selected = remaining[:2]
            remaining = remaining[2:]
            steps.append(
                {
                    "step": len(steps) + 1,
                    "summary": "Continue with the next strongest exercises from the recommendation pool so the student can keep building confidence while extending the same core ideas into a slightly broader setting.",
                    "target_concepts": self._merge_target_concepts(state, selected),
                    "exercises": [
                        {
                            "exercise_id": candidate["exercise"].exercise_id,
                            "priority": index,
                            "reason": self._reason_for_candidate(candidate),
                        }
                        for index, candidate in enumerate(selected, start=1)
                    ],
                }
            )

        summary = (
            f"This roadmap focuses on {', '.join(state['focus_concept_ids']) or 'the current concepts'} "
            "and moves from reinforcement into broader follow-up practice. The earlier steps are meant to stabilize the student's current weakness, while the later steps gradually widen the challenge without losing concept continuity."
        )
        return summary, steps

    def _build_rerank_documents(
        self, state: RecommendationState, candidates: list[dict[str, Any]]
    ) -> list[str]:
        documents = []
        for candidate in candidates:
            exercise = candidate["exercise"]
            documents.append(
                "\n".join(
                    [
                        f"exercise_id: {exercise.exercise_id}",
                        f"title: {exercise.title}",
                        f"description: {exercise.description}",
                        f"difficulty: {exercise.difficulty}",
                        f"concept_slugs: {', '.join(exercise.concept_slugs)}",
                        f"recommended_weight: {float(candidate.get('recommended_weight', 0.0)):.4f}",
                        f"tests_weight: {float(candidate.get('tests_weight', 0.0)):.4f}",
                        f"related_weight: {float(candidate.get('related_weight', 0.0)):.4f}",
                        f"progression_score: {float(candidate.get('progression_score', 0.0)):.4f}",
                        f"similarity_score: {float(candidate.get('similarity_score', 0.0)):.4f}",
                        f"vector_similarity: {float(candidate.get('vector_similarity', 0.0)):.4f}",
                        f"history_fit_score: {float(candidate.get('history_fit_score', 0.0)):.4f}",
                        f"root_connection_mode: {candidate.get('root_connection_mode', 'fallback')}",
                        f"root_connection_weight: {float(candidate.get('root_connection_weight', 0.0)):.4f}",
                        f"root_hop_count: {int(candidate.get('root_hop_count', 0) or 0)}",
                        f"retrieval_sources: {', '.join(candidate.get('retrieval_sources', []))}",
                    ]
                )
            )
        return documents

    def _roadmap_candidate_pool(
        self, candidates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        pool: list[dict[str, Any]] = []
        for index, candidate in enumerate(candidates, start=1):
            exercise = candidate["exercise"]
            pool.append(
                {
                    "rank": index,
                    "exercise_id": exercise.exercise_id,
                    "title": exercise.title,
                    "description": truncate_text(exercise.description, limit=140),
                    "difficulty": exercise.difficulty,
                    "concept_slugs": list(exercise.concept_slugs),
                    "target_concepts": self._candidate_target_concepts({}, candidate),
                    "root_connection_mode": candidate.get(
                        "root_connection_mode", "fallback"
                    ),
                    "root_hop_count": int(candidate.get("root_hop_count", 0) or 0),
                    "retrieval_sources": list(candidate.get("retrieval_sources", [])),
                    "connection_hint": self._connection_hint(candidate),
                    "suggested_reason": self._reason_for_candidate(candidate),
                }
            )
        return pool

    def _build_roadmap_builder_context(
        self,
        state: RecommendationState,
        pool_candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        review = state["review"]
        submission = state["submission"]
        review_items = review.review_items if review else []
        base_context = self._llm_base_context_summary(state)
        return {
            "goal": "build a sequenced roadmap from a reranked recommendation pool",
            "student_context": base_context,
            "roadmap_constraints": {
                "prefer_step_count": 3,
                "max_step_count": 3,
                "max_exercises_per_step": 2,
                "min_exercises_per_step": 1,
                "focus_concept_ids": list(state["focus_concept_ids"]),
                "attempted_exercise_ids": list(state["attempted_exercise_ids"][:8]),
            },
            "student_learning_signals": {
                "review_summary": review.summary if review else "",
                "review_detail": review.detail if review else "",
                "top_review_issues": [
                    {
                        "type": item.type,
                        "issue": item.issue,
                        "fix_suggestion": item.fix_suggestion,
                    }
                    for item in review_items[:4]
                ],
                "submission_code_preview": (
                    self._extract_code_snippet(submission.code)
                    if submission and submission.code.strip()
                    else ""
                ),
                "failing_testcases": [
                    {
                        "input": testcase.input,
                        "expect": testcase.expect,
                        "output": testcase.output,
                    }
                    for testcase in (submission.testcases if submission else [])
                    if str(testcase.expect).strip() != str(testcase.output).strip()
                ][:4],
            },
            "rerank_context": {
                "query": state.get("rerank_query", {}),
                "overview": str(state.get("rerank_overview", "")),
            },
            "pool_summary": {
                "candidate_count": len(pool_candidates),
                "difficulty_mix": self._pool_difficulty_mix(pool_candidates),
                "candidate_ids": self._candidate_ids(pool_candidates),
            },
        }

    @staticmethod
    def _serialize_rerank_query(
        *, rerank_query: dict[str, Any], rerank_overview: str
    ) -> str:
        return json.dumps(
            {
                "query": rerank_query,
                "overview": rerank_overview,
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _source_candidate_limits(state: RecommendationState) -> tuple[int, int]:
        return 20, 20

    def _fallback_reranked_candidates(
        self, state: RecommendationState
    ) -> list[dict[str, Any]]:
        reranked = [dict(candidate) for candidate in state["retrieved_candidates"]]
        for candidate in reranked:
            candidate["history_fit_score"] = self._history_fit_score(state, candidate)
            candidate["final_score"] = self._final_candidate_score(state, candidate)
        return sorted(
            reranked,
            key=lambda candidate: (
                float(candidate.get("final_score", 0.0)),
                float(candidate.get("recommended_weight", 0.0)),
                float(candidate.get("tests_weight", 0.0)),
            ),
            reverse=True,
        )

    def _merge_candidates(
        self,
        graph_candidates: list[dict[str, Any]],
        vector_candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}

        for candidate in graph_candidates:
            exercise_id = candidate["exercise"].exercise_id
            merged[exercise_id] = {
                **candidate,
                "vector_similarity": float(candidate.get("vector_similarity", 0.0)),
                "root_connection_mode": str(
                    candidate.get("root_connection_mode", "fallback")
                ),
                "root_connection_weight": float(
                    candidate.get("root_connection_weight", 0.0)
                ),
                "root_hop_count": int(candidate.get("root_hop_count", 0) or 0),
                "retrieval_sources": ["graph"],
            }

        for candidate in vector_candidates:
            exercise_id = candidate["exercise"].exercise_id
            if exercise_id in merged:
                merged[exercise_id]["vector_similarity"] = max(
                    float(merged[exercise_id].get("vector_similarity", 0.0)),
                    float(candidate.get("vector_similarity", 0.0)),
                )
                merged[exercise_id]["retrieval_sources"] = ["graph", "vector"]
                continue
            merged[exercise_id] = {
                **candidate,
                "vector_similarity": float(candidate.get("vector_similarity", 0.0)),
                "root_connection_mode": str(
                    candidate.get("root_connection_mode", "fallback")
                ),
                "root_connection_weight": float(
                    candidate.get("root_connection_weight", 0.0)
                ),
                "root_hop_count": int(candidate.get("root_hop_count", 0) or 0),
                "retrieval_sources": list(
                    candidate.get("retrieval_sources", ["vector"])
                ),
            }

        return list(merged.values())

    def _instrument_node(self, node_name: str, handler):
        def wrapped(state: RecommendationState):
            logger.debug(
                "Entering recommendation node '%s' with state summary: %s",
                node_name,
                self._summarize_state(state),
            )
            result = handler(state)
            logger.debug(
                "Leaving recommendation node '%s' with state summary: %s",
                node_name,
                self._summarize_state(result),
            )
            logger.debug(
                "Recommendation state snapshot after node '%s': %s",
                node_name,
                self._snapshot_state(result),
            )
            return result

        return wrapped

    @staticmethod
    def _candidate_ids(candidates: list[dict[str, Any]]) -> list[str]:
        return [
            str(candidate.get("exercise").exercise_id)
            for candidate in candidates
            if candidate.get("exercise") is not None
        ]

    @staticmethod
    def _summarize_state(state: RecommendationState) -> dict[str, Any]:
        return {
            "student_id": state.get("student_id", ""),
            "exercise_id": state.get("exercise_id", ""),
            "focus_concept_ids": list(state.get("focus_concept_ids", [])),
            "attempted_exercise_count": len(state.get("attempted_exercise_ids", [])),
            "retrieved_candidates": len(state.get("retrieved_candidates", [])),
            "reranked_candidates": len(state.get("reranked_candidates", [])),
            "roadmap_steps": len(state.get("roadmap_steps", [])),
            "review_present": bool(state.get("review")),
            "submission_present": bool(state.get("submission")),
        }

    @staticmethod
    def _snapshot_state(state: RecommendationState) -> dict[str, Any]:
        review = state.get("review")
        submission = state.get("submission")
        return {
            "rerank_query_keys": list((state.get("rerank_query") or {}).keys())[:8],
            "rerank_overview": truncate_text(
                state.get("rerank_overview", ""), limit=180
            ),
            "retrieved_candidate_ids": [
                candidate["exercise"].exercise_id
                for candidate in (state.get("retrieved_candidates") or [])[:5]
                if candidate.get("exercise") is not None
            ],
            "reranked_candidate_ids": [
                candidate["exercise"].exercise_id
                for candidate in (state.get("reranked_candidates") or [])[:5]
                if candidate.get("exercise") is not None
            ],
            "roadmap_step_summaries": [
                truncate_text(str(step.get("summary", "")), limit=100)
                for step in (state.get("roadmap_steps") or [])[:3]
            ],
            "review_summary": truncate_text(getattr(review, "summary", ""), limit=160),
            "submission_preview": truncate_text(
                getattr(submission, "code", ""),
                limit=160,
            ),
        }

    def _build_vector_query_text(self, state: RecommendationState) -> str:
        exercise = state["exercise"]
        review = state["review"]
        review_summary = review.summary if review else ""
        review_detail = review.detail if review else ""
        exercise_title = exercise.title
        exercise_description = exercise.description
        return "\n".join(
            [
                "Recommendation retrieval query",
                f"Current exercise: {exercise_title}",
                f"Exercise description: {exercise_description}",
                f"Current concepts: {', '.join(state['focus_concept_ids'])}",
                f"Latest review summary: {review_summary}",
                f"Latest review detail: {review_detail}",
                f"History: attempted={len(state['attempted_exercise_ids'])}",
            ]
        )

    @staticmethod
    def _primary_focus_concept(state: RecommendationState) -> str:
        focus_concept_ids = state.get("focus_concept_ids", [])
        return focus_concept_ids[0] if focus_concept_ids else ""

    def _history_fit_score(
        self,
        state: RecommendationState,
        candidate: dict[str, Any],
    ) -> float:
        similarity_score = float(candidate.get("similarity_score", 0.0))
        progression_score = float(candidate.get("progression_score", 0.0))
        difficulty_gap = abs(float(candidate.get("difficulty_gap", 0.0)))
        vector_similarity = float(candidate.get("vector_similarity", 0.0))
        repeated_exposure = len(state["attempted_exercise_ids"])
        return self._clamp_float(
            0.35 * progression_score
            + 0.25 * vector_similarity
            + 0.20 * similarity_score
            + 0.20 * min(repeated_exposure / 6.0, 1.0)
            + 0.10 * max(0.0, 1.0 - difficulty_gap),
            0.0,
        )

    def _final_candidate_score(
        self,
        state: RecommendationState,
        candidate: dict[str, Any],
    ) -> float:
        source_bonus = 0.05 if len(candidate.get("retrieval_sources", [])) > 1 else 0.0
        root_mode = (
            str(candidate.get("root_connection_mode", "fallback")).strip().lower()
        )
        root_bonus = (
            0.04 if root_mode == "direct" else 0.02 if root_mode == "indirect" else 0.0
        )
        return self._clamp_float(
            0.24 * float(candidate.get("recommended_weight", 0.0))
            + 0.16 * float(candidate.get("tests_weight", 0.0))
            + 0.14 * float(candidate.get("related_weight", 0.0))
            + 0.14 * float(candidate.get("progression_score", 0.0))
            + 0.12 * float(candidate.get("similarity_score", 0.0))
            + 0.15 * float(candidate.get("vector_similarity", 0.0))
            + 0.10 * float(candidate.get("history_fit_score", 0.0))
            + source_bonus
            + root_bonus,
            0.0,
        )

    @staticmethod
    def _reason_for_candidate(candidate: dict[str, Any]) -> str:
        root_mode = (
            str(candidate.get("root_connection_mode", "fallback")).strip().lower()
        )
        if root_mode == "direct":
            return (
                "A strong next step because it stays directly connected to the current concept and gives the student a clearer chance to reinforce the same core reasoning pattern."
            )
        if root_mode == "indirect":
            return "A useful bridge exercise because it stays close to the current concept while expanding the student's practice into a nearby pattern that needs slightly broader reasoning."
        return "A relevant reinforcement exercise chosen from similar problem patterns, so the student can keep practicing the same ideas in a fresh but still familiar setting."

    @staticmethod
    def _candidate_target_concepts(
        state: RecommendationState,
        candidate: dict[str, Any],
    ) -> list[str]:
        target_concept = str(candidate.get("target_concept", "")).strip()
        if target_concept:
            return [target_concept]
        return list(state.get("focus_concept_ids", []))

    def _merge_target_concepts(
        self,
        state: RecommendationState,
        candidates: list[dict[str, Any]],
    ) -> list[str]:
        merged: list[str] = []
        for candidate in candidates:
            for concept in self._candidate_target_concepts(state, candidate):
                if concept and concept not in merged:
                    merged.append(concept)
        return merged or list(state.get("focus_concept_ids", []))

    def _normalize_roadmap_response(
        self,
        *,
        state: RecommendationState,
        pool_candidates: list[dict[str, Any]],
        parsed: dict[str, Any],
        fallback_summary: str,
        fallback_steps: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        valid_ids = {
            candidate["exercise"].exercise_id: candidate
            for candidate in pool_candidates
        }
        raw_steps = parsed.get("roadmap")
        if not isinstance(raw_steps, list):
            return fallback_summary, fallback_steps

        normalized_steps: list[dict[str, Any]] = []
        for step_index, raw_step in enumerate(raw_steps, start=1):
            if not isinstance(raw_step, dict):
                continue
            raw_exercises = raw_step.get("exercises")
            if not isinstance(raw_exercises, list):
                continue
            normalized_exercises: list[dict[str, Any]] = []
            seen_step_ids: set[str] = set()
            for item_index, raw_item in enumerate(raw_exercises, start=1):
                if not isinstance(raw_item, dict):
                    continue
                exercise_id = str(raw_item.get("exercise_id", "")).strip()
                if (
                    not exercise_id
                    or exercise_id not in valid_ids
                    or exercise_id in seen_step_ids
                ):
                    continue
                seen_step_ids.add(exercise_id)
                normalized_exercises.append(
                    {
                        "exercise_id": exercise_id,
                        "priority": int(
                            raw_item.get("priority", item_index) or item_index
                        ),
                        "reason": str(raw_item.get("reason", "")).strip()
                        or self._reason_for_candidate(valid_ids[exercise_id]),
                    }
                )
            if not normalized_exercises:
                continue
            target_concepts = raw_step.get("target_concepts")
            normalized_steps.append(
                {
                    "step": int(raw_step.get("step", step_index) or step_index),
                    "summary": str(raw_step.get("summary", "")).strip()
                    or "Continue with the next recommended practice set.",
                    "target_concepts": (
                        list(target_concepts)
                        if isinstance(target_concepts, list)
                        else self._merge_target_concepts(
                            state,
                            [
                                valid_ids[item["exercise_id"]]
                                for item in normalized_exercises
                            ],
                        )
                    ),
                    "exercises": sorted(
                        normalized_exercises,
                        key=lambda item: int(item.get("priority", 999)),
                    ),
                }
            )

        if not normalized_steps:
            return fallback_summary, fallback_steps

        summary = str(parsed.get("summary", "")).strip() or fallback_summary
        return summary, normalized_steps

    def _pool_difficulty_mix(
        self,
        candidates: list[dict[str, Any]],
    ) -> dict[str, int]:
        mix = {"easy": 0, "medium": 0, "hard": 0, "other": 0}
        for candidate in candidates:
            difficulty = self._normalize_difficulty(
                getattr(candidate.get("exercise"), "difficulty", "")
            )
            if difficulty in mix:
                mix[difficulty] += 1
            else:
                mix["other"] += 1
        return mix

    @staticmethod
    def _normalize_difficulty(difficulty: str) -> str:
        normalized = str(difficulty or "").strip().lower()
        return normalized if normalized in {"easy", "medium", "hard"} else ""

    @staticmethod
    def _connection_hint(candidate: dict[str, Any]) -> str:
        root_mode = (
            str(candidate.get("root_connection_mode", "fallback")).strip().lower()
        )
        hop_count = int(candidate.get("root_hop_count", 0) or 0)
        if root_mode == "direct":
            return "Directly related to the current exercise in the graph."
        if root_mode == "indirect":
            return f"Connected through a nearby graph path of {hop_count} hops."
        return "Included as a similar fallback recommendation."

    @staticmethod
    def _extract_code_snippet(code: str, max_lines: int = 6) -> str:
        lines = [line.rstrip() for line in code.splitlines() if line.strip()]
        snippet = "\n".join(lines[:max_lines]).strip()
        return snippet or code.strip()[:240]

    @staticmethod
    def _clamp_float(value: Any, fallback: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return fallback
