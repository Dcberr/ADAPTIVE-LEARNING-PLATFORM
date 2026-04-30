from __future__ import annotations

import json
from typing import Any, cast

from langgraph.graph import StateGraph
from openai import OpenAI

from code_review_ai.api.recommendation_schema import (
    RecommendationExercise,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationRoadmapStep,
)
from code_review_ai.models.recommendation_state import RecommendationState
from code_review_ai.config import FireworksStageConfig
from code_review_ai.prompts.recommendation.rerank_context_builder import (
    build_rerank_context_builder_system_prompt,
    build_rerank_context_finalize_prompt,
    build_rerank_context_plan_prompt,
)
from code_review_ai.repositories.neo4j_repository import Neo4jRepository
from code_review_ai.services.exercise_vector_service import ExerciseVectorService
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.fireworks_rerank_client import (
    FireworksRerankError,
    rerank_documents_with_retry,
)
from code_review_ai.utils.parse_json_response import safe_parse_json_response


class RecommendationService:
    """Retrieve from graph and vector first, rerank with context, then explain."""

    ROADMAP_SIZE = 3

    def __init__(
        self,
        neo4j_repository: Neo4jRepository,
        exercise_vector_service: ExerciseVectorService,
        client: OpenAI,
        fireworks_api_key: str,
        fireworks_base_url: str,
        rerank_context_builder_stage_config: FireworksStageConfig,
        reranker_stage_config: FireworksStageConfig,
    ):
        self.neo4j_repository = neo4j_repository
        self.exercise_vector_service = exercise_vector_service
        self.client = client
        self.fireworks_api_key = fireworks_api_key
        self.fireworks_base_url = fireworks_base_url
        self.rerank_context_builder_stage_config = rerank_context_builder_stage_config
        self.reranker_stage_config = reranker_stage_config
        self.context_subgraph = self._build_context_subgraph()
        self.workflow = self._build_workflow()

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        initial_state: RecommendationState = {
            "student_id": request.student_id,
            "exercise_id": request.exercise_id,
            "base_context": {},
            "focus_concept_id": "",
            "focus_concept_weight": 0.0,
            "review": None,
            "review_record": None,
            "review_history": [],
            "submission_record": None,
            "submission_history": [],
            "attempted_exercise_ids": [],
            "retrieved_candidates": [],
            "rerank_query": {},
            "rerank_overview": "",
            "reranked_candidates": [],
        }

        final_state = cast(RecommendationState, self.workflow.invoke(initial_state))
        if not final_state["reranked_candidates"]:
            raise ValueError("No exercises found for this recommendation roadmap.")

        selected_candidates = final_state["reranked_candidates"][: self.ROADMAP_SIZE]
        selected_exercises = [candidate["exercise"] for candidate in selected_candidates]
        roadmap_directives = [
            self._directive_for_candidate(candidate, index)
            for index, candidate in enumerate(selected_candidates, start=1)
        ]

        self.neo4j_repository.store_recommendation_roadmap(
            student_id=final_state["student_id"],
            assigned_path="IMPROVE",
            target_concept=final_state["focus_concept_id"],
            exercise_ids=[exercise.exercise_id for exercise in selected_exercises],
            review_id=(
                final_state["review"].review_id if final_state["review"] is not None else None
            ),
        )
        exercise_concept_map = self.neo4j_repository.get_concept_ids_by_exercise(
            [exercise.exercise_id for exercise in selected_exercises]
        )

        return RecommendationResponse(
            student_id=final_state["student_id"],
            current_exercise_id=final_state["exercise_id"],
            focus_concept_id=final_state["focus_concept_id"],
            roadmap=[
                RecommendationRoadmapStep(
                    step=index,
                    exercise=RecommendationExercise(
                        concept_ids=exercise_concept_map.get(exercise.exercise_id, []),
                        directive=roadmap_directives[index - 1],
                        **exercise.model_dump(),
                    ),
                )
                for index, exercise in enumerate(selected_exercises, start=1)
            ],
        )

    def _build_workflow(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("context_subgraph", self._run_context_subgraph)
        workflow.add_node("candidate_retriever", self._candidate_retriever)
        workflow.add_node("rerank_context_builder", self._rerank_context_builder)
        workflow.add_node("candidate_ranker", self._candidate_ranker)
        workflow.set_entry_point("context_subgraph")
        workflow.add_edge("context_subgraph", "candidate_retriever")
        workflow.add_edge("candidate_retriever", "rerank_context_builder")
        workflow.add_edge("rerank_context_builder", "candidate_ranker")
        workflow.set_finish_point("candidate_ranker")
        return workflow.compile()

    def _build_context_subgraph(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("base_context_loader", self._base_context_loader)
        workflow.set_entry_point("base_context_loader")
        workflow.set_finish_point("base_context_loader")
        return workflow.compile()

    def _run_context_subgraph(self, state: RecommendationState) -> RecommendationState:
        return cast(RecommendationState, self.context_subgraph.invoke(state))

    def _base_context_loader(self, state: RecommendationState) -> RecommendationState:
        context = self.neo4j_repository.fetch_recommendation_base_context(
            student_id=state["student_id"],
            exercise_id=state["exercise_id"],
        )
        new_state = dict(state)
        new_state["base_context"] = context
        new_state["focus_concept_id"] = context["current_concept"]
        new_state["focus_concept_weight"] = context["current_concept_weight"]
        new_state["review"] = context["review"]
        new_state["review_record"] = context["review_record"]
        new_state["submission_record"] = context["latest_submission"]
        new_state["submission_history"] = []
        new_state["attempted_exercise_ids"] = context["attempted_exercise_ids"]
        return cast(RecommendationState, new_state)

    def _candidate_retriever(self, state: RecommendationState) -> RecommendationState:
        focus_concept_id = state["focus_concept_id"]
        graph_limit, vector_limit = self._source_candidate_limits(state)

        graph_candidates = self.neo4j_repository.retrieve_candidates(
            student_id=state["student_id"],
            current_exercise_id=state["exercise_id"],
            current_concept=state["focus_concept_id"],
            target_concept=focus_concept_id,
            attempted_exercise_ids=state["attempted_exercise_ids"],
            limit=graph_limit,
            allow_indirect_paths=False,
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
                if vector_hit_map:
                    vector_candidates = self.neo4j_repository.retrieve_candidates(
                        student_id=state["student_id"],
                        current_exercise_id=state["exercise_id"],
                        current_concept=state["focus_concept_id"],
                        target_concept=focus_concept_id,
                        attempted_exercise_ids=state["attempted_exercise_ids"],
                        candidate_exercise_ids=list(vector_hit_map.keys()),
                        limit=vector_limit,
                        allow_indirect_paths=True,
                    )
                    for candidate in vector_candidates:
                        candidate["vector_similarity"] = float(
                            vector_hit_map.get(candidate["exercise"].exercise_id, 0.0)
                        )
                        candidate["retrieval_sources"] = ["vector"]
            except Exception:
                vector_candidates = []

        candidates = self._merge_candidates(graph_candidates, vector_candidates)

        new_state = dict(state)
        new_state["focus_concept_id"] = state["focus_concept_id"]
        new_state["retrieved_candidates"] = candidates
        new_state["reranked_candidates"] = []
        return cast(RecommendationState, new_state)

    def _rerank_context_builder(self, state: RecommendationState) -> RecommendationState:
        plan = self._plan_rerank_context(state)
        review_history = list(state["review_history"])
        submission_history = list(state["submission_history"])

        if plan["need_review_history"] and state["review_record"] is not None:
            review_trend = self.neo4j_repository.fetch_review_trend_context(
                review_id=state["review_record"].review_id,
                student_id=state["student_id"],
                history_limit=plan["review_history_limit"],
            )
            review_history = review_trend.get("review_history", [])

        if plan["need_submission_history"] and state["submission_record"] is not None:
            submission_trend = self.neo4j_repository.fetch_submission_history_context(
                submission_id=state["submission_record"].submission_id,
                history_limit=plan["submission_history_limit"],
            )
            submission_history = submission_trend.get("submission_history", [])

        rerank_query, rerank_overview = self._finalize_rerank_context(
            state,
            review_history=review_history,
            submission_history=submission_history,
            planner_goal_query=plan["goal_query"],
        )

        new_state = dict(state)
        new_state["review_history"] = review_history
        new_state["submission_history"] = submission_history
        new_state["rerank_query"] = rerank_query
        new_state["rerank_overview"] = rerank_overview
        return cast(RecommendationState, new_state)

    def _candidate_ranker(self, state: RecommendationState) -> RecommendationState:
        candidates = state["retrieved_candidates"]
        if not candidates:
            return cast(RecommendationState, dict(state))

        reranked_candidates = self._rerank_candidates(state)
        new_state = dict(state)
        new_state["reranked_candidates"] = reranked_candidates
        return cast(RecommendationState, new_state)

    def _rerank_candidates(self, state: RecommendationState) -> list[dict[str, Any]]:
        fallback_candidates = self._fallback_reranked_candidates(state)
        if not fallback_candidates:
            return fallback_candidates

        documents = self._build_rerank_documents(state, fallback_candidates)
        query = self._serialize_rerank_query(
            rerank_query=state.get("rerank_query", {}),
            rerank_overview=str(state.get("rerank_overview", "")),
        )
        try:
            response = rerank_documents_with_retry(
                api_key=self.fireworks_api_key,
                base_url=self.fireworks_base_url,
                model_name=self.reranker_stage_config.model_name,
                query=query,
                documents=documents,
                top_n=min(len(documents), max(self.ROADMAP_SIZE * 3, 8)),
                return_documents=False,
                task=(
                    "Rank the candidate exercises for the student's next best coding practice step "
                    "using the provided student context, current exercise context, and candidate evidence."
                ),
            )
        except FireworksRerankError:
            return fallback_candidates

        rerank_scores = {
            int(item.get("index", -1)): float(item.get("relevance_score", 0.0) or 0.0)
            for item in response.get("data", [])
        }
        if not rerank_scores:
            return fallback_candidates

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

    def _build_rerank_query(self, state: RecommendationState) -> dict[str, Any]:
        base_context = state["base_context"]
        exercise = base_context.get("exercise")
        review = state["review"]
        tested_concepts = base_context.get("tested_concepts", [])
        recommended_concepts = base_context.get("recommended_concepts", [])

        return {
            "goal": "rank the best next exercises for the student",
            "goal_query": "Rank the best next exercises for the student's current concept.",
            "student_id": state["student_id"],
            "current_exercise_id": state["exercise_id"],
            "focus_concept_id": state["focus_concept_id"],
            "current_exercise": {
                "title": getattr(exercise, "title", ""),
                "description": getattr(exercise, "description", ""),
                "difficulty": getattr(exercise, "difficulty", ""),
            },
            "latest_review": {
                "summary": review.summary if review else "",
                "detail": review.detail if review else "",
            },
            "tested_concepts": tested_concepts[:5],
            "recommended_concepts": recommended_concepts[:5],
        }

    def _plan_rerank_context(self, state: RecommendationState) -> dict[str, Any]:
        base_context = self._llm_base_context_summary(state)
        fallback = {
            "goal_query": "Rank the best next exercises for the student's current concept.",
            "need_review_history": bool(state["review_record"]),
            "review_history_limit": 2,
            "need_submission_history": bool(state["submission_record"]),
            "submission_history_limit": 2,
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
                "goal_query": str(parsed.get("goal_query", fallback["goal_query"])).strip()
                or fallback["goal_query"],
                "need_review_history": bool(parsed.get("need_review_history", fallback["need_review_history"])),
                "review_history_limit": max(
                    0,
                    min(3, int(parsed.get("review_history_limit", fallback["review_history_limit"]))),
                ),
                "need_submission_history": bool(
                    parsed.get("need_submission_history", fallback["need_submission_history"])
                ),
                "submission_history_limit": max(
                    0,
                    min(
                        3,
                        int(
                            parsed.get(
                                "submission_history_limit",
                                fallback["submission_history_limit"],
                            )
                        ),
                    ),
                ),
            }
        except Exception:
            return fallback

    def _finalize_rerank_context(
        self,
        state: RecommendationState,
        *,
        review_history: list[Any],
        submission_history: list[Any],
        planner_goal_query: str,
    ) -> tuple[dict[str, Any], str]:
        base_context = self._llm_base_context_summary(state)
        submission_history_summary = self._summarize_submission_history(
            current_submission=state["submission_record"],
            submission_history=submission_history,
        )
        review_history_summary = [
            {
                "summary": review.summary,
                "detail": review.detail,
            }
            for review in review_history
        ]
        submission_history_summary = [
            {
                "code_preview": item.get("code_preview", ""),
                "comparison_to_current": item.get("comparison_to_current", {}),
            }
            for item in submission_history_summary
        ]
        fallback_query = self._build_rerank_query(state)
        fallback_overview = self._fallback_rerank_overview(
            state,
            review_history=review_history_summary,
            submission_history=submission_history_summary,
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
                            review_history=review_history_summary,
                            submission_history=submission_history_summary,
                            planner_goal_query=planner_goal_query,
                        ),
                    },
                ],
                temperature=self.rerank_context_builder_stage_config.temperature,
                max_tokens=self.rerank_context_builder_stage_config.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            goal_query = str(parsed.get("goal_query", planner_goal_query)).strip() or planner_goal_query
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
        base_context = state["base_context"]
        exercise = base_context.get("exercise")
        review = state["review"]
        submission_record = state["submission_record"]
        review_items = review.review_items if review else []
        review_history_summary = [
            {
                "summary": item.summary,
                "detail": item.detail,
            }
            for item in state["review_history"]
        ]
        submission_history_summary = self._summarize_submission_history(
            current_submission=submission_record,
            submission_history=state["submission_history"],
        )

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
                "concept_id": state["focus_concept_id"],
                "weight": state["focus_concept_weight"],
            },
            "latest_review": {
                "review_id": state["review_record"].review_id if state["review_record"] else "",
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
            "review_history": review_history_summary,
            "latest_submission": {
                "submission_id": (
                    submission_record.submission_id if submission_record else ""
                ),
                "created_at": submission_record.created_at if submission_record else "",
                "code_preview": (
                    self._extract_code_snippet(submission_record.code)
                    if submission_record and submission_record.code.strip()
                    else ""
                ),
                "testcase_output_count": (
                    len(submission_record.testcase_outputs) if submission_record else 0
                ),
            },
            "submission_history": [
                {
                    "code_preview": item.get("code_preview", ""),
                    "comparison_to_current": item.get("comparison_to_current", {}),
                }
                for item in submission_history_summary
            ],
            "history": {
                "attempted_exercise_count": len(state["attempted_exercise_ids"]),
                "recent_attempted_exercise_ids": state["attempted_exercise_ids"][:5],
            },
            "retrieval": {
                "candidate_count": len(state["retrieved_candidates"]),
            },
        }

    def _summarize_submission_history(
        self,
        *,
        current_submission: Any,
        submission_history: list[Any],
    ) -> list[dict[str, Any]]:
        if current_submission is None:
            return []

        current_outputs = list(getattr(current_submission, "testcase_outputs", []) or [])
        current_pass_count, current_total = self._submission_pass_stats(current_outputs)
        summaries: list[dict[str, Any]] = []
        for previous_submission in submission_history:
            previous_outputs = list(
                getattr(previous_submission, "testcase_outputs", []) or []
            )
            previous_pass_count, previous_total = self._submission_pass_stats(
                previous_outputs
            )
            improvement_ratio, regression_ratio = self._calculate_attempt_transition_scores(
                previous_outputs=previous_outputs,
                current_outputs=current_outputs,
            )
            summaries.append(
                {
                    "submission_id": previous_submission.submission_id,
                    "created_at": previous_submission.created_at,
                    "code_preview": self._extract_code_snippet(previous_submission.code),
                    "comparison_to_current": {
                        "improvement_ratio": improvement_ratio,
                        "regression_ratio": regression_ratio,
                        "previous_pass_count": previous_pass_count,
                        "previous_testcase_count": previous_total,
                        "current_pass_count": current_pass_count,
                        "current_testcase_count": current_total,
                        "pass_count_delta": current_pass_count - previous_pass_count,
                    },
                }
            )
        return summaries

    @staticmethod
    def _submission_pass_stats(outputs: list[Any]) -> tuple[int, int]:
        total = len(outputs)
        pass_count = 0
        for output in outputs:
            if hasattr(output, "expect"):
                expect_value = getattr(output, "expect", "")
                actual_value = getattr(output, "output", "")
            else:
                expect_value = output.get("expect", "") if isinstance(output, dict) else ""
                actual_value = output.get("output", "") if isinstance(output, dict) else ""
            expect = str(expect_value).strip()
            actual = str(actual_value).strip()
            if expect == actual:
                pass_count += 1
        return pass_count, total

    def _calculate_attempt_transition_scores(
        self,
        *,
        previous_outputs: list[Any],
        current_outputs: list[Any],
    ) -> tuple[float, float]:
        previous_failed = {
            index
            for index, item in enumerate(previous_outputs)
            if not self._did_testcase_pass(item)
        }
        current_failed = {
            index
            for index, item in enumerate(current_outputs)
            if not self._did_testcase_pass(item)
        }

        fixed_count = len(previous_failed - current_failed)
        newly_broken_count = len(current_failed - previous_failed)

        previous_total = max(len(previous_outputs), 1)
        current_total = max(len(current_outputs), 1)
        previous_pass_rate = (previous_total - len(previous_failed)) / previous_total
        current_pass_rate = (current_total - len(current_failed)) / current_total
        score_delta = current_pass_rate - previous_pass_rate

        fixed_ratio = fixed_count / max(len(previous_failed), 1)
        broken_ratio = newly_broken_count / max(len(previous_failed), 1)

        improvement_ratio = max(
            0.0,
            min(1.0, 0.5 * max(score_delta, 0.0) + 0.5 * fixed_ratio),
        )
        regression_ratio = max(
            0.0,
            min(1.0, 0.5 * max(-score_delta, 0.0) + 0.5 * broken_ratio),
        )
        return improvement_ratio, regression_ratio

    @staticmethod
    def _did_testcase_pass(output: Any) -> bool:
        if hasattr(output, "expect"):
            expect_value = getattr(output, "expect", "")
            actual_value = getattr(output, "output", "")
        else:
            expect_value = output.get("expect", "") if isinstance(output, dict) else ""
            actual_value = output.get("output", "") if isinstance(output, dict) else ""
        return str(expect_value).strip() == str(actual_value).strip()

    def _fallback_rerank_overview(
        self,
        state: RecommendationState,
        *,
        review_history: list[dict[str, Any]],
        submission_history: list[dict[str, Any]],
    ) -> str:
        base_context = state["base_context"]
        exercise = base_context.get("exercise")
        review = state["review"]
        exercise_title = getattr(exercise, "title", state["exercise_id"])
        attempted_count = len(state["attempted_exercise_ids"])
        parts = [
            (
                f"The student is currently working on {exercise_title} and the recommendation "
                f"should stay focused on concept {state['focus_concept_id']}."
            ),
            f"They have already submitted {attempted_count} prior exercises.",
        ]
        if review and review.summary.strip():
            parts.append(f"The latest review highlights: {review.summary.strip()}")
        if review_history:
            parts.append(
                f"{len(review_history)} earlier review records are available for repeated-pattern checking."
            )
        if submission_history:
            parts.append(
                f"{len(submission_history)} earlier submissions are available for progress comparison."
            )
        return " ".join(parts)

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
                        f"path_relation_types: {', '.join(candidate.get('path_relation_types', []))}",
                        f"retrieval_sources: {', '.join(candidate.get('retrieval_sources', []))}",
                    ]
                )
            )
        return documents

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
        return 6, 6

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
                "path_relation_types": list(candidate.get("path_relation_types", [])),
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
                "path_relation_types": list(candidate.get("path_relation_types", [])),
                "retrieval_sources": list(candidate.get("retrieval_sources", ["vector"])),
            }

        return list(merged.values())

    def _build_vector_query_text(self, state: RecommendationState) -> str:
        base_context = state["base_context"]
        exercise = base_context.get("exercise")
        review = state["review"]
        review_summary = review.summary if review else ""
        review_detail = review.detail if review else ""
        exercise_title = exercise.title if exercise is not None else state["exercise_id"]
        exercise_description = exercise.description if exercise is not None else ""
        return "\n".join(
            [
                "Recommendation retrieval query",
                f"Current exercise: {exercise_title}",
                f"Exercise description: {exercise_description}",
                f"Current concept: {state['focus_concept_id']}",
                f"Latest review summary: {review_summary}",
                f"Latest review detail: {review_detail}",
                f"History: attempted={len(state['attempted_exercise_ids'])}",
            ]
        )

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
        root_mode = str(candidate.get("root_connection_mode", "fallback")).strip().lower()
        root_bonus = 0.04 if root_mode == "direct" else 0.02 if root_mode == "indirect" else 0.0
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
    def _directive_for_candidate(candidate: dict[str, Any], index: int) -> str:
        root_mode = str(candidate.get("root_connection_mode", "fallback")).strip().lower()
        if root_mode == "direct":
            prefix = "Continue with a directly related exercise on the current concept."
        elif root_mode == "indirect":
            prefix = "Broaden practice with a nearby exercise that still connects through the graph."
        else:
            prefix = "Try a semantically similar exercise to reinforce the current concept."
        return f"Step {index}: {prefix}"

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
