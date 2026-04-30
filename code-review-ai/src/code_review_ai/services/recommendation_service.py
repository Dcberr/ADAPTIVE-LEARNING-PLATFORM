from __future__ import annotations

from typing import Any, cast

from langgraph.graph import END, StateGraph
from openai import OpenAI

from code_review_ai.api.recommendation_schema import (
    ExplanationBlock,
    ExplanationRef,
    RecommendationExercise,
    RecommendationGraphSummary,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationRoadmapStep,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import AssignedPath
from code_review_ai.models.recommendation_framework import RecommendationScoringFramework
from code_review_ai.models.recommendation_state import RecommendationState
from code_review_ai.config import FireworksStageConfig
from code_review_ai.prompts.recommendation.context_planner import (
    build_context_planner_prompt,
    build_context_planner_system_prompt,
)
from code_review_ai.prompts.recommendation.candidate_reranker import (
    build_candidate_reranker_prompt,
    build_candidate_reranker_system_prompt,
)
from code_review_ai.prompts.recommendation.explanation_builder import (
    build_explanation_builder_prompt,
    build_explanation_builder_system_prompt,
)
from code_review_ai.prompts.recommendation.path_decider import (
    build_path_decider_prompt,
    build_path_decider_system_prompt,
)
from code_review_ai.prompts.recommendation.json_repair import (
    build_json_repair_prompt,
    build_json_repair_system_prompt,
)
from code_review_ai.prompts.recommendation.roadmap_builder import (
    build_roadmap_builder_prompt,
    build_roadmap_builder_system_prompt,
)
from code_review_ai.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from code_review_ai.utils.fireworks_client import create_chat_completion_with_retry
from code_review_ai.utils.parse_json_response import safe_parse_json_response


class RecommendationService:
    """LLM-led recommendation flow with constrained graph retrieval."""

    EXTRA_CONTEXT_BLOCKS = {
        "review_trend",
        "submission_trend",
        "exercise_graph",
        "student_history",
    }

    def __init__(
        self,
        knowledge_graph_repository: KnowledgeGraphRepository,
        client: OpenAI,
        stage_configs: dict[str, FireworksStageConfig],
    ):
        self.knowledge_graph_repository = knowledge_graph_repository
        self.client = client
        self.stage_configs = stage_configs
        self.context_subgraph = self._build_context_subgraph()
        self.path_subgraph = self._build_path_subgraph()
        self.roadmap_subgraph = self._build_roadmap_subgraph()
        self.explanation_subgraph = self._build_explanation_subgraph()
        self.workflow = self._build_workflow()

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        initial_state: RecommendationState = {
            "student_id": request.student_id,
            "exercise_id": request.exercise_id,
            "base_context": {},
            "context_plan": {},
            "context_plan_valid": False,
            "loaded_blocks": [],
            "anchor_concept": "",
            "anchor_concept_weight": 0.0,
            "current_concept": "",
            "review": None,
            "review_record": None,
            "review_history": [],
            "latest_submission": None,
            "previous_review_payload": None,
            "previous_submission_payload": None,
            "mastered_concepts": [],
            "attempted_exercise_ids": [],
            "assigned_exercise_ids": [],
            "critical_errors": 0,
            "latest_submission_improvement_ratio": 0.0,
            "latest_submission_regression_ratio": 0.0,
            "exercise_graph": {},
            "assigned_path": "IMPROVE",
            "path_decision_valid": False,
            "path_decision_confidence": 0.0,
            "path_decision_reason": "",
            "focus_concept_id": "",
            "reasoning": {"content": "", "refs": []},
            "explanation_valid": False,
            "framework": RecommendationScoringFramework(
                risk_level="medium",
                readiness_level="developing",
                explanation="",
            ),
            "graph_summary": {},
            "retrieved_candidates": [],
            "reranked_candidates": [],
            "roadmap_selection_valid": False,
            "selected_candidates": [],
            "selected_exercises": [],
            "roadmap_directives": [],
            "roadmap_summary": {"content": "", "refs": []},
        }

        final_state = cast(RecommendationState, self.workflow.invoke(initial_state))
        if not final_state["selected_exercises"]:
            raise ValueError("No exercises found in Neo4j for this recommendation roadmap.")

        self.knowledge_graph_repository.store_recommendation_roadmap(
            student_id=final_state["student_id"],
            assigned_path=final_state["assigned_path"],
            target_concept=final_state["focus_concept_id"],
            exercise_ids=[
                exercise.exercise_id for exercise in final_state["selected_exercises"]
            ],
            review_id=(
                final_state["review"].review_id if final_state["review"] is not None else None
            ),
        )
        exercise_concept_map = self.knowledge_graph_repository.get_concept_ids_by_exercise(
            [exercise.exercise_id for exercise in final_state["selected_exercises"]]
        )

        return RecommendationResponse(
            student_id=final_state["student_id"],
            current_exercise_id=final_state["exercise_id"],
            anchor_concept=final_state["anchor_concept"],
            assigned_path=final_state["assigned_path"],
            focus_concept_id=final_state["focus_concept_id"],
            critical_errors=final_state["critical_errors"],
            framework=final_state["framework"],
            graph_summary=RecommendationGraphSummary.model_validate(
                final_state["graph_summary"]
            ),
            reasoning=ExplanationBlock.model_validate(final_state["reasoning"]),
            roadmap_summary=ExplanationBlock.model_validate(
                final_state["roadmap_summary"]
            ),
            roadmap=[
                RecommendationRoadmapStep(
                    step=index,
                    exercise=RecommendationExercise(
                        concept_ids=exercise_concept_map.get(exercise.exercise_id, []),
                        directive=final_state["roadmap_directives"][index - 1],
                        **exercise.model_dump(),
                    ),
                )
                for index, exercise in enumerate(final_state["selected_exercises"], start=1)
            ],
        )

    def _build_workflow(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("context_subgraph", self._run_context_subgraph)
        workflow.add_node("path_subgraph", self._run_path_subgraph)
        workflow.add_node("roadmap_subgraph", self._run_roadmap_subgraph)
        workflow.add_node("explanation_subgraph", self._run_explanation_subgraph)
        workflow.set_entry_point("context_subgraph")
        workflow.add_edge("context_subgraph", "path_subgraph")
        workflow.add_edge("path_subgraph", "roadmap_subgraph")
        workflow.add_edge("roadmap_subgraph", "explanation_subgraph")
        workflow.set_finish_point("explanation_subgraph")
        return workflow.compile()

    def _build_context_subgraph(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("base_context_loader", self._base_context_loader)
        workflow.add_node("context_planner", self._context_planner)
        workflow.add_node("context_planner_fallback", self._context_planner_fallback)
        workflow.add_node("conditional_context_loader", self._conditional_context_loader)
        workflow.set_entry_point("base_context_loader")
        workflow.add_edge("base_context_loader", "context_planner")
        workflow.add_conditional_edges(
            "context_planner",
            self._route_context_plan,
            {
                "load": "conditional_context_loader",
                "fallback": "context_planner_fallback",
            },
        )
        workflow.add_edge("context_planner_fallback", "conditional_context_loader")
        workflow.set_finish_point("conditional_context_loader")
        return workflow.compile()

    def _build_path_subgraph(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("path_decider", self._path_decider)
        workflow.add_node("path_decider_fallback", self._path_decider_fallback)
        workflow.set_entry_point("path_decider")
        workflow.add_conditional_edges(
            "path_decider",
            self._route_path_decision,
            {
                "done": END,
                "fallback": "path_decider_fallback",
            },
        )
        workflow.set_finish_point("path_decider_fallback")
        return workflow.compile()

    def _build_roadmap_subgraph(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("candidate_retriever", self._candidate_retriever)
        workflow.add_node("candidate_reranker", self._candidate_reranker)
        workflow.add_node("roadmap_builder", self._roadmap_builder)
        workflow.add_node("roadmap_builder_fallback", self._roadmap_builder_fallback)
        workflow.set_entry_point("candidate_retriever")
        workflow.add_edge("candidate_retriever", "candidate_reranker")
        workflow.add_edge("candidate_reranker", "roadmap_builder")
        workflow.add_conditional_edges(
            "roadmap_builder",
            self._route_roadmap_selection,
            {
                "done": END,
                "fallback": "roadmap_builder_fallback",
            },
        )
        workflow.set_finish_point("roadmap_builder_fallback")
        return workflow.compile()

    def _build_explanation_subgraph(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("explanation_builder", self._explanation_builder)
        workflow.add_node(
            "explanation_builder_fallback", self._explanation_builder_fallback
        )
        workflow.set_entry_point("explanation_builder")
        workflow.add_conditional_edges(
            "explanation_builder",
            self._route_explanation,
            {
                "done": END,
                "fallback": "explanation_builder_fallback",
            },
        )
        workflow.set_finish_point("explanation_builder_fallback")
        return workflow.compile()

    def _run_context_subgraph(self, state: RecommendationState) -> RecommendationState:
        return cast(RecommendationState, self.context_subgraph.invoke(state))

    def _run_path_subgraph(self, state: RecommendationState) -> RecommendationState:
        return cast(RecommendationState, self.path_subgraph.invoke(state))

    def _run_roadmap_subgraph(self, state: RecommendationState) -> RecommendationState:
        return cast(RecommendationState, self.roadmap_subgraph.invoke(state))

    def _run_explanation_subgraph(self, state: RecommendationState) -> RecommendationState:
        return cast(RecommendationState, self.explanation_subgraph.invoke(state))

    def _base_context_loader(self, state: RecommendationState) -> RecommendationState:
        context = self.knowledge_graph_repository.fetch_recommendation_base_context(
            student_id=state["student_id"],
            exercise_id=state["exercise_id"],
        )
        new_state = dict(state)
        new_state["base_context"] = context
        new_state["anchor_concept"] = context["current_concept"]
        new_state["anchor_concept_weight"] = context["current_concept_weight"]
        new_state["current_concept"] = context["current_concept"]
        new_state["review"] = context["review"]
        new_state["review_record"] = context["review_record"]
        new_state["latest_submission"] = context["latest_submission"]
        new_state["mastered_concepts"] = context["mastered_concepts"]
        new_state["attempted_exercise_ids"] = context["attempted_exercise_ids"]
        new_state["critical_errors"] = context["critical_errors"]
        new_state["focus_concept_id"] = context["current_concept"]
        return cast(RecommendationState, new_state)

    def _context_planner(self, state: RecommendationState) -> RecommendationState:
        plan: dict[str, Any] = {}
        is_valid = False
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs["context_planner"].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_context_planner_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self._build_context_planner_prompt(state),
                    },
                ],
                temperature=self.stage_configs["context_planner"].temperature,
                max_tokens=self.stage_configs["context_planner"].max_tokens,
            )
            model_text = response.choices[0].message.content or ""
            parsed = self._parse_json_with_repair(
                raw_response=model_text,
                stage_key="context_planner",
            )
            blocks = []
            for block_name in self.EXTRA_CONTEXT_BLOCKS:
                if bool(parsed.get(f"need_{block_name}", False)):
                    blocks.append(block_name)
            provisional_focus = str(
                parsed.get("provisional_focus_concept_id", state["anchor_concept"])
            ).strip() or state["anchor_concept"]
            priority_signal = str(parsed.get("priority_signal", "")).strip()
            reason = str(parsed.get("reason", "")).strip()
            if blocks:
                plan = {
                    "blocks": blocks,
                    "provisional_focus_concept_id": provisional_focus,
                    "priority_signal": priority_signal or "current_review_issue",
                    "reason": reason or "LLM selected focused context blocks for the current case.",
                }
                is_valid = True
        except Exception:
            pass

        new_state = dict(state)
        new_state["context_plan"] = plan
        new_state["context_plan_valid"] = is_valid
        return cast(RecommendationState, new_state)

    def _parse_json_with_repair(
        self,
        *,
        raw_response: str,
        stage_key: str,
    ) -> dict[str, Any]:
        parsed = safe_parse_json_response(raw_response)
        if "raw" not in parsed:
            return parsed

        try:
            repair_response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs[stage_key].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_json_repair_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_json_repair_prompt(raw_response),
                    },
                ],
                temperature=0.0,
                max_tokens=min(self.stage_configs[stage_key].max_tokens, 400),
            )
            repaired_text = repair_response.choices[0].message.content or ""
            repaired = safe_parse_json_response(repaired_text)
            if "raw" not in repaired:
                return repaired
        except Exception:
            pass

        return parsed

    def _context_planner_fallback(self, state: RecommendationState) -> RecommendationState:
        new_state = dict(state)
        new_state["context_plan"] = self._fallback_context_plan(state)
        new_state["context_plan_valid"] = True
        return cast(RecommendationState, new_state)

    def _conditional_context_loader(
        self, state: RecommendationState
    ) -> RecommendationState:
        plan = state["context_plan"]
        blocks = plan.get("blocks", [])
        loaded_blocks: list[str] = []
        review_record = state["review_record"]
        latest_submission = state["latest_submission"]
        focus_hint = str(
            plan.get("provisional_focus_concept_id", state["anchor_concept"])
        ).strip() or state["anchor_concept"]

        review_history = list(state["review_history"])
        exercise_graph = dict(state["exercise_graph"])
        previous_review_payload = state["previous_review_payload"]
        previous_submission_payload = state["previous_submission_payload"]
        latest_submission_improvement_ratio = state["latest_submission_improvement_ratio"]
        latest_submission_regression_ratio = state["latest_submission_regression_ratio"]
        attempted_exercise_ids = list(state["attempted_exercise_ids"])
        assigned_exercise_ids = list(state["assigned_exercise_ids"])

        if "review_trend" in blocks and review_record is not None:
            review_trend = self.knowledge_graph_repository.fetch_review_trend_context(
                review_id=review_record.review_id,
                student_id=state["student_id"],
            )
            review_history = review_trend["review_history"]
            previous_review_id = review_trend.get("previous_review_id", "")
            if previous_review_id:
                previous_review_payload = self.knowledge_graph_repository.get_review_payload(
                    previous_review_id
                )
            loaded_blocks.append("review_trend")

        if "submission_trend" in blocks and latest_submission is not None:
            submission_trend = self.knowledge_graph_repository.fetch_submission_trend_context(
                submission_id=latest_submission.submission_id
            )
            latest_submission_improvement_ratio = submission_trend[
                "latest_submission_improvement_ratio"
            ]
            latest_submission_regression_ratio = submission_trend[
                "latest_submission_regression_ratio"
            ]
            previous_submission_id = submission_trend.get("previous_submission_id", "")
            if previous_submission_id:
                previous_submission_payload = (
                    self.knowledge_graph_repository.get_submission_payload(
                        previous_submission_id
                    )
                )
            loaded_blocks.append("submission_trend")

        if "exercise_graph" in blocks:
            exercise_graph = self.knowledge_graph_repository.fetch_exercise_graph_context(
                exercise_id=state["exercise_id"],
                focus_concept_id=focus_hint,
            )
            loaded_blocks.append("exercise_graph")

        if "student_history" in blocks:
            history = self.knowledge_graph_repository.fetch_student_history_context(
                student_id=state["student_id"]
            )
            attempted_exercise_ids = history.get("attempted_exercise_ids", [])
            assigned_exercise_ids = history.get("assigned_exercise_ids", [])
            loaded_blocks.append("student_history")

        new_state = dict(state)
        new_state["loaded_blocks"] = loaded_blocks
        new_state["review_history"] = review_history
        new_state["exercise_graph"] = exercise_graph
        new_state["previous_review_payload"] = previous_review_payload
        new_state["previous_submission_payload"] = previous_submission_payload
        new_state["latest_submission_improvement_ratio"] = (
            latest_submission_improvement_ratio
        )
        new_state["latest_submission_regression_ratio"] = (
            latest_submission_regression_ratio
        )
        new_state["attempted_exercise_ids"] = attempted_exercise_ids
        new_state["assigned_exercise_ids"] = assigned_exercise_ids
        return cast(RecommendationState, new_state)

    def _path_decider(self, state: RecommendationState) -> RecommendationState:
        decision: dict[str, Any] = {}
        is_valid = False
        fallback_decision = self._fallback_path_decision(state)
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs["path_decider"].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_path_decider_system_prompt(),
                    },
                    {"role": "user", "content": self._build_path_decider_prompt(state)},
                ],
                temperature=self.stage_configs["path_decider"].temperature,
                max_tokens=self.stage_configs["path_decider"].max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            assigned_path = self._parse_assigned_path(parsed.get("assigned_path"))
            focus_concept_id = str(
                parsed.get("focus_concept_id", fallback_decision["focus_concept_id"])
            ).strip() or fallback_decision["focus_concept_id"]
            valid_focus_ids = self._valid_focus_concept_ids(state)
            if focus_concept_id not in valid_focus_ids:
                focus_concept_id = fallback_decision["focus_concept_id"]
            confidence = self._clamp_float(
                parsed.get("confidence"), fallback_decision["confidence"]
            )
            risk_level = self._parse_risk_level(parsed.get("risk_level"), "medium")
            readiness_level = self._parse_readiness_level(
                parsed.get("readiness_level"), "developing"
            )
            reason = str(parsed.get("reason", "")).strip()
            decision = {
                "assigned_path": assigned_path,
                "focus_concept_id": focus_concept_id,
                "confidence": confidence,
                "risk_level": risk_level,
                "readiness_level": readiness_level,
                "reason": reason or "LLM selected the most suitable next learning path.",
            }
            is_valid = True
        except Exception:
            pass

        if not is_valid:
            new_state = dict(state)
            new_state["path_decision_valid"] = False
            return cast(RecommendationState, new_state)

        return self._apply_path_decision(state, decision, valid=True)

    def _path_decider_fallback(self, state: RecommendationState) -> RecommendationState:
        decision = self._fallback_path_decision(state)
        return self._apply_path_decision(state, decision, valid=True)

    def _candidate_retriever(self, state: RecommendationState) -> RecommendationState:
        focus_concept_id = state["focus_concept_id"] or state["anchor_concept"]

        candidates = self.knowledge_graph_repository.retrieve_candidates(
            student_id=state["student_id"],
            current_exercise_id=state["exercise_id"],
            current_concept=state["anchor_concept"],
            target_concept=focus_concept_id,
            attempted_exercise_ids=state["attempted_exercise_ids"],
            limit=12,
        )
        if not candidates and state["assigned_path"] != "IMPROVE":
            candidates = self.knowledge_graph_repository.retrieve_candidates(
                student_id=state["student_id"],
                current_exercise_id=state["exercise_id"],
                current_concept=state["anchor_concept"],
                target_concept=state["anchor_concept"],
                attempted_exercise_ids=state["attempted_exercise_ids"],
                limit=12,
            )

        new_state = dict(state)
        new_state["focus_concept_id"] = focus_concept_id
        new_state["retrieved_candidates"] = candidates
        new_state["reranked_candidates"] = []
        return cast(RecommendationState, new_state)

    def _candidate_reranker(self, state: RecommendationState) -> RecommendationState:
        candidates = state["retrieved_candidates"]
        if not candidates:
            new_state = dict(state)
            new_state["reranked_candidates"] = []
            return cast(RecommendationState, new_state)

        reranked_candidates = self._fallback_reranked_candidates(state)
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs["candidate_reranker"].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_candidate_reranker_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self._build_candidate_reranker_prompt(state),
                    },
                ],
                temperature=self.stage_configs["candidate_reranker"].temperature,
                max_tokens=self.stage_configs["candidate_reranker"].max_tokens,
            )
            parsed = self._parse_json_with_repair(
                raw_response=response.choices[0].message.content or "",
                stage_key="candidate_reranker",
            )
            reranked_ids = parsed.get("exercise_ids") or []
            if isinstance(reranked_ids, list):
                selected = self._select_candidates_by_ids(
                    candidates,
                    [str(item).strip() for item in reranked_ids if str(item).strip()],
                )
                if selected:
                    seen_ids = {candidate["exercise"].exercise_id for candidate in selected}
                    remainder = [
                        candidate
                        for candidate in reranked_candidates
                        if candidate["exercise"].exercise_id not in seen_ids
                    ]
                    reranked_candidates = selected + remainder
        except Exception:
            pass

        new_state = dict(state)
        new_state["reranked_candidates"] = reranked_candidates
        return cast(RecommendationState, new_state)

    def _roadmap_builder(self, state: RecommendationState) -> RecommendationState:
        candidates = state["reranked_candidates"] or state["retrieved_candidates"]
        if not candidates:
            raise ValueError("Neo4j did not return any recommendation roadmap candidates.")

        selected_ids: list[str] = []
        directives: list[str] = []
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs["roadmap_builder"].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_roadmap_builder_system_prompt(),
                    },
                    {"role": "user", "content": self._build_roadmap_prompt(state)},
                ],
                temperature=self.stage_configs["roadmap_builder"].temperature,
                max_tokens=self.stage_configs["roadmap_builder"].max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            raw_ids = parsed.get("exercise_ids") or []
            if isinstance(raw_ids, list):
                selected_ids = [
                    str(item).strip()
                    for item in raw_ids
                    if str(item).strip()
                ]
            raw_directives = parsed.get("directives") or []
            if isinstance(raw_directives, list):
                directives = [
                    str(item).strip()
                    for item in raw_directives
                    if str(item).strip()
                ]
        except Exception:
            pass

        selected_candidates = self._select_candidates_by_ids(candidates, selected_ids)
        if not selected_candidates:
            new_state = dict(state)
            new_state["roadmap_selection_valid"] = False
            return cast(RecommendationState, new_state)

        return self._apply_roadmap_selection(
            state,
            selected_candidates=selected_candidates,
            directives=directives,
            valid=True,
        )

    def _roadmap_builder_fallback(self, state: RecommendationState) -> RecommendationState:
        candidates = state["reranked_candidates"] or state["retrieved_candidates"]
        if not candidates:
            raise ValueError("Neo4j did not return any recommendation roadmap candidates.")
        selected_candidates = candidates[:3]
        directives = self._fallback_directives(
            state, [candidate["exercise"] for candidate in selected_candidates]
        )
        return self._apply_roadmap_selection(
            state,
            selected_candidates=selected_candidates,
            directives=directives,
            valid=True,
        )

    def _explanation_builder(self, state: RecommendationState) -> RecommendationState:
        selected_exercises = state["selected_exercises"]
        if not selected_exercises:
            raise ValueError("Explanation builder requires selected exercises.")

        ref_catalog = self._build_reference_catalog(state)
        fallback_reasoning = self._fallback_reasoning_block(state, ref_catalog)
        fallback_summary = self._fallback_roadmap_summary_block(state, ref_catalog)

        reasoning: dict[str, Any] | None = None
        roadmap_summary: dict[str, Any] | None = None
        try:
            response = create_chat_completion_with_retry(
                self.client,
                model=self.stage_configs["explanation_builder"].model_name,
                messages=[
                    {
                        "role": "system",
                        "content": build_explanation_builder_system_prompt(),
                    },
                    {"role": "user", "content": self._build_explanation_prompt(state, ref_catalog)},
                ],
                temperature=self.stage_configs["explanation_builder"].temperature,
                max_tokens=self.stage_configs["explanation_builder"].max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            reasoning = self._make_explanation_block(
                content=str(parsed.get("reasoning_content", "")).strip(),
                ref_ids=parsed.get("reasoning_ref_ids") or [],
                ref_catalog=ref_catalog,
            )
            roadmap_summary = self._make_explanation_block(
                content=str(parsed.get("roadmap_summary_content", "")).strip(),
                ref_ids=parsed.get("roadmap_summary_ref_ids") or [],
                ref_catalog=ref_catalog,
            )
        except Exception:
            pass

        if not self._is_explanation_block_valid(reasoning) or not self._is_explanation_block_valid(
            roadmap_summary
        ):
            new_state = dict(state)
            new_state["explanation_valid"] = False
            return cast(RecommendationState, new_state)

        new_state = dict(state)
        new_state["reasoning"] = reasoning
        new_state["roadmap_summary"] = roadmap_summary
        new_state["explanation_valid"] = True
        return cast(RecommendationState, new_state)

    def _explanation_builder_fallback(
        self, state: RecommendationState
    ) -> RecommendationState:
        ref_catalog = self._build_reference_catalog(state)
        new_state = dict(state)
        new_state["reasoning"] = self._fallback_reasoning_block(state, ref_catalog)
        new_state["roadmap_summary"] = self._fallback_roadmap_summary_block(
            state, ref_catalog
        )
        new_state["explanation_valid"] = True
        return cast(RecommendationState, new_state)

    @staticmethod
    def _route_context_plan(state: RecommendationState) -> str:
        return "load" if state["context_plan_valid"] else "fallback"

    @staticmethod
    def _route_path_decision(state: RecommendationState) -> str:
        return "done" if state["path_decision_valid"] else "fallback"

    @staticmethod
    def _route_roadmap_selection(state: RecommendationState) -> str:
        return "done" if state["roadmap_selection_valid"] else "fallback"

    @staticmethod
    def _route_explanation(state: RecommendationState) -> str:
        return "done" if state["explanation_valid"] else "fallback"

    def _apply_path_decision(
        self, state: RecommendationState, decision: dict[str, Any], valid: bool
    ) -> RecommendationState:
        assigned_path = cast(
            AssignedPath,
            decision.get("assigned_path", self._fallback_path_decision(state)["assigned_path"]),
        )
        focus_concept_id = str(
            decision.get("focus_concept_id", state["anchor_concept"])
        ).strip() or state["anchor_concept"]
        new_state = dict(state)
        new_state["assigned_path"] = assigned_path
        new_state["focus_concept_id"] = focus_concept_id
        new_state["path_decision_valid"] = valid
        new_state["path_decision_confidence"] = self._clamp_float(
            decision.get("confidence"), state["path_decision_confidence"]
        )
        reason = str(decision.get("reason", "")).strip()
        new_state["path_decision_reason"] = reason or state["path_decision_reason"]
        new_state["framework"] = RecommendationScoringFramework(
            risk_level=self._parse_risk_level(
                decision.get("risk_level"), state["framework"].risk_level
            ),
            readiness_level=self._parse_readiness_level(
                decision.get("readiness_level"), state["framework"].readiness_level
            ),
            explanation=reason or state["framework"].explanation,
        )
        new_state["graph_summary"] = {
            **state["graph_summary"],
            "current_concept_weight": state["anchor_concept_weight"],
            "best_related_exercise_weight": state["exercise_graph"].get(
                "best_related_exercise_weight", 0.0
            ),
            "best_recommended_weight": state["exercise_graph"].get(
                "best_recommended_weight", 0.0
            ),
            "latest_submission_improvement_ratio": state[
                "latest_submission_improvement_ratio"
            ],
            "latest_submission_regression_ratio": state[
                "latest_submission_regression_ratio"
            ],
        }
        return cast(RecommendationState, new_state)

    def _apply_roadmap_selection(
        self,
        state: RecommendationState,
        selected_candidates: list[dict[str, Any]],
        directives: list[str],
        valid: bool,
    ) -> RecommendationState:
        selected_exercises = [
            cast(ExerciseRecord, candidate["exercise"]) for candidate in selected_candidates
        ]
        normalized_directives = [
            str(item).strip() for item in directives if str(item).strip()
        ]
        if len(normalized_directives) < len(selected_exercises):
            normalized_directives.extend(
                self._fallback_directives(
                    state, selected_exercises[len(normalized_directives) :]
                )
            )
        normalized_directives = normalized_directives[: len(selected_exercises)]
        new_state = dict(state)
        new_state["selected_candidates"] = selected_candidates
        new_state["selected_exercises"] = selected_exercises
        new_state["roadmap_directives"] = normalized_directives
        new_state["roadmap_selection_valid"] = valid
        return cast(RecommendationState, new_state)

    @staticmethod
    def _is_explanation_block_valid(block: dict[str, Any] | None) -> bool:
        if not isinstance(block, dict):
            return False
        content = str(block.get("content", "")).strip()
        refs = block.get("refs")
        return bool(content) and isinstance(refs, list)

    def _build_context_planner_prompt(self, state: RecommendationState) -> str:
        base = state["base_context"]
        review = cast(Any, base["review"])
        latest_submission = base.get("latest_submission")
        return build_context_planner_prompt(
            student_id=state["student_id"],
            exercise_id=state["exercise_id"],
            current_concept=base["current_concept"],
            critical_errors=base["critical_errors"],
            review_summary=review.summary,
            review_detail=review.detail,
            tested_concepts=base["tested_concepts"],
            recommended_concepts=base["recommended_concepts"],
            has_latest_submission=latest_submission is not None,
        )

    def _build_path_decider_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        review_trend_summary = self._review_trend_summary(state)
        submission_trend_summary = self._submission_trend_summary(state)
        student_history_summary = self._student_history_summary(state)
        exercise_graph_summary = (
            state["exercise_graph"] if "exercise_graph" in state["loaded_blocks"] else None
        )
        return build_path_decider_prompt(
            anchor_concept=state["anchor_concept"],
            suggested_focus_concept=state["context_plan"].get(
                "provisional_focus_concept_id", state["anchor_concept"]
            ),
            critical_errors=state["critical_errors"],
            latest_review_summary=review.summary if review else "",
            review_trend_summary=review_trend_summary,
            submission_trend_summary=submission_trend_summary,
            student_history_summary=student_history_summary,
            exercise_graph=exercise_graph_summary,
            valid_focus_concepts=self._valid_focus_concept_ids(state),
        )

    def _build_roadmap_prompt(self, state: RecommendationState) -> str:
        candidates = []
        source_candidates = state["reranked_candidates"] or state["retrieved_candidates"]
        for candidate in source_candidates[:8]:
            exercise = candidate["exercise"]
            candidates.append(
                {
                    "exercise_id": exercise.exercise_id,
                    "title": exercise.title,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "concept_slugs": exercise.concept_slugs,
                    "recommended_weight": candidate["recommended_weight"],
                    "tests_weight": candidate["tests_weight"],
                    "related_weight": candidate["related_weight"],
                    "progression_score": candidate["progression_score"],
                    "similarity_score": candidate["similarity_score"],
                    "relation_type": candidate["relation_type"],
                    "difficulty_gap": candidate["difficulty_gap"],
                }
            )
        return build_roadmap_builder_prompt(
            assigned_path=state["assigned_path"],
            focus_concept_id=state["focus_concept_id"],
            path_reason=state["path_decision_reason"],
            candidates=candidates,
        )

    def _build_candidate_reranker_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        candidates = []
        for candidate in state["retrieved_candidates"][:12]:
            exercise = candidate["exercise"]
            candidates.append(
                {
                    "exercise_id": exercise.exercise_id,
                    "title": exercise.title,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "concept_slugs": exercise.concept_slugs,
                    "recommended_weight": candidate["recommended_weight"],
                    "tests_weight": candidate["tests_weight"],
                    "related_weight": candidate["related_weight"],
                    "relation_type": candidate["relation_type"],
                    "difficulty_gap": candidate["difficulty_gap"],
                    "progression_score": candidate["progression_score"],
                    "similarity_score": candidate["similarity_score"],
                }
            )
        return build_candidate_reranker_prompt(
            assigned_path=state["assigned_path"],
            anchor_concept=state["anchor_concept"],
            focus_concept_id=state["focus_concept_id"],
            path_reason=state["path_decision_reason"],
            critical_errors=state["critical_errors"],
            latest_review_summary=review.summary if review else "",
            candidates=candidates,
        )

    def _build_explanation_prompt(
        self, state: RecommendationState, ref_catalog: dict[str, dict[str, str]]
    ) -> str:
        refs = list(ref_catalog.values())
        selected_exercises = [
            {
                "exercise_id": exercise.exercise_id,
                "title": exercise.title,
                "description": exercise.description,
                "directive": directive,
            }
            for exercise, directive in zip(
                state["selected_exercises"], state["roadmap_directives"]
            )
        ]
        return build_explanation_builder_prompt(
            assigned_path=state["assigned_path"],
            anchor_concept=state["anchor_concept"],
            focus_concept_id=state["focus_concept_id"],
            path_reason=state["path_decision_reason"],
            selected_exercises=selected_exercises,
            refs=refs,
        )

    def _fallback_context_plan(self, state: RecommendationState) -> dict[str, Any]:
        latest_submission = state["latest_submission"]
        critical_errors = state["critical_errors"]
        blocks = ["exercise_graph", "review_trend", "student_history"]
        if latest_submission is not None:
            blocks.append("submission_trend")
        return {
            "blocks": blocks,
            "provisional_focus_concept_id": state["anchor_concept"],
            "priority_signal": (
                "current_review_issue" if critical_errors > 0 else "progress_readiness"
            ),
            "reason": "Fallback context plan loads trend, graph, and history before path selection.",
        }

    @staticmethod
    def _review_trend_summary(state: RecommendationState) -> dict[str, Any] | None:
        if "review_trend" not in state["loaded_blocks"]:
            return None
        previous_review_payload = state["previous_review_payload"]
        if not previous_review_payload:
            return None
        previous_review = previous_review_payload.get("review")
        previous_submission = previous_review_payload.get("submission")
        return {
            "previous_review_id": getattr(previous_review, "review_id", ""),
            "previous_review_summary": getattr(previous_review, "summary", ""),
            "previous_review_concept": getattr(previous_review, "current_concept", ""),
            "previous_submission_id": getattr(previous_submission, "submission_id", ""),
            "history_count": len(state["review_history"]),
        }

    @staticmethod
    def _submission_trend_summary(state: RecommendationState) -> dict[str, Any] | None:
        if "submission_trend" not in state["loaded_blocks"]:
            return None
        previous_submission_payload = state["previous_submission_payload"]
        if not previous_submission_payload:
            return None
        previous_submission = previous_submission_payload.get("submission")
        return {
            "previous_submission_id": getattr(previous_submission, "submission_id", ""),
            "improvement_ratio": state["latest_submission_improvement_ratio"],
            "regression_ratio": state["latest_submission_regression_ratio"],
        }

    @staticmethod
    def _student_history_summary(state: RecommendationState) -> dict[str, Any] | None:
        if "student_history" not in state["loaded_blocks"]:
            return None
        return {
            "attempted_exercise_count": len(state["attempted_exercise_ids"]),
            "assigned_exercise_count": len(state["assigned_exercise_ids"]),
            "recent_attempted_exercise_ids": state["attempted_exercise_ids"][:5],
            "recent_assigned_exercise_ids": state["assigned_exercise_ids"][:5],
        }

    def _fallback_path_decision(self, state: RecommendationState) -> dict[str, Any]:
        review_summary = (state["review"].summary if state["review"] else "").lower()
        review_detail = (state["review"].detail if state["review"] else "").lower()
        review_text = f"{review_summary} {review_detail}".strip()
        improvement_ratio = state["latest_submission_improvement_ratio"]
        regression_ratio = state["latest_submission_regression_ratio"]
        exercise_graph = state["exercise_graph"]
        related_exercises = exercise_graph.get("related_exercises", [])
        strongest_relation_type = (
            str(related_exercises[0].get("relation_type", "")).strip()
            if related_exercises
            else ""
        )
        student_history = self._student_history_summary(state) or {}
        attempted_count = int(student_history.get("attempted_exercise_count", 0) or 0)
        assigned_count = int(student_history.get("assigned_exercise_count", 0) or 0)
        repeated_exposure = attempted_count + assigned_count
        foundation_signals = (
            "prerequisite" in review_text
            or "foundation" in review_text
            or "fundamental" in review_text
            or strongest_relation_type == "PREREQUISITE_REVIEW"
        )

        if foundation_signals and (
            state["critical_errors"] >= 2 or regression_ratio >= improvement_ratio
        ):
            return {
                "assigned_path": "PREREQUISITE_REVIEW",
                "focus_concept_id": state["anchor_concept"],
                "confidence": 0.62,
                "risk_level": "high",
                "readiness_level": "emerging",
                "reason": "The evidence points to a missing foundation, so prerequisite review is safer than staying at the current level.",
            }
        if (
            state["critical_errors"] >= 2
            or regression_ratio > improvement_ratio
        ):
            return {
                "assigned_path": "REINFORCE",
                "focus_concept_id": state["anchor_concept"],
                "confidence": 0.6,
                "risk_level": "high",
                "readiness_level": "emerging",
                "reason": "The latest evidence shows unstable understanding on the current concept, so reinforcement is safest.",
            }
        if (
            state["critical_errors"] == 0
            and improvement_ratio >= 0.45
            and regression_ratio <= 0.1
            and repeated_exposure >= 4
        ):
            return {
                "assigned_path": "TRANSFER",
                "focus_concept_id": state["anchor_concept"],
                "confidence": 0.59,
                "risk_level": "low",
                "readiness_level": "ready",
                "reason": "The student looks stable on the current concept and has enough repeated exposure that a transfer-style variation is a better next check.",
            }
        if (
            state["critical_errors"] == 0
            and improvement_ratio >= 0.35
            and regression_ratio <= 0.1
        ):
            return {
                "assigned_path": "HARDER",
                "focus_concept_id": state["anchor_concept"],
                "confidence": 0.57,
                "risk_level": "low",
                "readiness_level": "ready",
                "reason": "The recent signals are strong enough to try a harder same-concept exercise.",
            }
        return {
            "assigned_path": "IMPROVE",
            "focus_concept_id": state["anchor_concept"],
            "confidence": 0.58,
            "risk_level": "medium",
            "readiness_level": "developing",
            "reason": "The student is making progress, but still needs nearby practice before moving on.",
        }

    def _fallback_directives(
        self, state: RecommendationState, exercises: list[ExerciseRecord]
    ) -> list[str]:
        if state["assigned_path"] == "PREREQUISITE_REVIEW":
            prefix = "Step back to prerequisite foundations with this exercise."
        elif state["assigned_path"] == "REINFORCE":
            prefix = "Stabilize the same concept with this practice task."
        elif state["assigned_path"] == "HARDER":
            prefix = "Use this harder exercise to deepen the same concept."
        elif state["assigned_path"] == "TRANSFER":
            prefix = "Apply the same concept in a different problem form with this exercise."
        else:
            prefix = "Use this exercise to improve the current concept with a slightly broader task."
        return [f"Step {index}: {prefix}" for index, _ in enumerate(exercises, start=1)]

    def _fallback_reranked_candidates(
        self, state: RecommendationState
    ) -> list[dict[str, Any]]:
        return sorted(
            state["retrieved_candidates"],
            key=self._candidate_sort_key,
            reverse=True,
        )

    @staticmethod
    def _candidate_sort_key(
        candidate: dict[str, Any]
    ) -> tuple[float, float, float, float, float]:
        return (
            float(candidate.get("recommended_weight", 0.0)),
            float(candidate.get("tests_weight", 0.0)),
            float(candidate.get("related_weight", 0.0)),
            float(candidate.get("progression_score", 0.0)),
            float(candidate.get("similarity_score", 0.0)),
        )

    def _fallback_reasoning_block(
        self, state: RecommendationState, ref_catalog: dict[str, dict[str, str]]
    ) -> dict[str, Any]:
        ref_ids = []
        if "ref_review_current" in ref_catalog:
            ref_ids.append("ref_review_current")
        if "ref_review_previous" in ref_catalog:
            ref_ids.append("ref_review_previous")
        if "ref_code_previous" in ref_catalog:
            ref_ids.append("ref_code_previous")
        content = (
            f"The selected path is {state['assigned_path']} because the latest review "
            f"and recent progress signals still center on {state['focus_concept_id']}."
        )
        if ref_ids:
            content += f" See {self._join_ref_tokens(ref_ids[:2])}."
        return self._make_explanation_block(content, ref_ids[:3], ref_catalog)

    def _fallback_roadmap_summary_block(
        self, state: RecommendationState, ref_catalog: dict[str, dict[str, str]]
    ) -> dict[str, Any]:
        ref_ids = [
            ref_id
            for ref_id in ref_catalog
            if ref_id.startswith("ref_exercise_step_")
        ]
        content = (
            "The roadmap starts with the closest exercise match, then broadens practice "
            "while staying aligned with the selected concept."
        )
        if ref_ids:
            content += f" See {self._join_ref_tokens(ref_ids[:2])}."
        return self._make_explanation_block(content, ref_ids[:3], ref_catalog)

    def _select_candidates_by_ids(
        self, candidates: list[dict[str, Any]], selected_ids: list[str]
    ) -> list[dict[str, Any]]:
        candidate_map = {
            candidate["exercise"].exercise_id: candidate for candidate in candidates
        }
        selected = []
        seen_ids: set[str] = set()
        for exercise_id in selected_ids:
            if exercise_id in candidate_map and exercise_id not in seen_ids:
                selected.append(candidate_map[exercise_id])
                seen_ids.add(exercise_id)
            if len(selected) == 3:
                break
        return selected

    def _build_reference_catalog(
        self, state: RecommendationState
    ) -> dict[str, dict[str, str]]:
        ref_catalog: dict[str, dict[str, str]] = {}
        review = state["review"]
        if review is not None:
            ref_catalog["ref_review_current"] = {
                "ref_id": "ref_review_current",
                "content": review.summary or review.detail,
                "ref_category": "review",
            }
        previous_review_payload = state["previous_review_payload"]
        if previous_review_payload:
            ref_catalog["ref_review_previous"] = {
                "ref_id": "ref_review_previous",
                "content": previous_review_payload["review"].summary,
                "ref_category": "review",
            }
        latest_submission = state["latest_submission"]
        if latest_submission is not None and latest_submission.code.strip():
            ref_catalog["ref_code_current"] = {
                "ref_id": "ref_code_current",
                "content": self._extract_code_snippet(latest_submission.code),
                "ref_category": "code",
            }
        previous_submission_payload = state["previous_submission_payload"]
        if previous_submission_payload:
            previous_submission = previous_submission_payload["submission"]
            if previous_submission.code.strip():
                ref_catalog["ref_code_previous"] = {
                    "ref_id": "ref_code_previous",
                    "content": self._extract_code_snippet(previous_submission.code),
                    "ref_category": "code",
                }
        base_context = state["base_context"]
        exercise = base_context.get("exercise")
        if exercise is not None:
            tested = ", ".join(
                item["concept_id"] for item in base_context.get("tested_concepts", [])[:3]
            )
            ref_catalog["ref_exercise_current"] = {
                "ref_id": "ref_exercise_current",
                "content": f"{exercise.title}: {exercise.description}. Concepts: {tested}",
                "ref_category": "exercise",
            }
        for index, exercise in enumerate(state["selected_exercises"], start=1):
            ref_catalog[f"ref_exercise_step_{index}"] = {
                "ref_id": f"ref_exercise_step_{index}",
                "content": f"{exercise.title}: {exercise.description}",
                "ref_category": "exercise",
            }
        return ref_catalog

    def _make_explanation_block(
        self,
        content: str,
        ref_ids: list[Any],
        ref_catalog: dict[str, dict[str, str]],
        fallback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cleaned_ref_ids = []
        for ref_id in ref_ids:
            ref_id_str = str(ref_id).strip()
            if ref_id_str in ref_catalog and ref_id_str not in cleaned_ref_ids:
                cleaned_ref_ids.append(ref_id_str)
        if not content.strip():
            return fallback or {"content": "", "refs": []}
        refs = [ref_catalog[ref_id] for ref_id in cleaned_ref_ids]
        return {
            "content": content,
            "refs": [ExplanationRef.model_validate(ref).model_dump() for ref in refs],
        }

    @staticmethod
    def _extract_code_snippet(code: str, max_lines: int = 6) -> str:
        lines = [line.rstrip() for line in code.splitlines() if line.strip()]
        snippet = "\n".join(lines[:max_lines]).strip()
        return snippet or code.strip()[:240]

    @staticmethod
    def _join_ref_tokens(ref_ids: list[str]) -> str:
        return " and ".join(f"{{{ref_id}}}" for ref_id in ref_ids)

    def _valid_focus_concept_ids(self, state: RecommendationState) -> list[str]:
        focus_ids = {state["anchor_concept"]}
        focus_ids.update(item["concept_id"] for item in state["base_context"].get("tested_concepts", []))
        return [concept_id for concept_id in focus_ids if concept_id]

    @staticmethod
    def _parse_assigned_path(value: Any) -> AssignedPath:
        text = str(value).strip().upper()
        if text in {
            "REINFORCE",
            "IMPROVE",
            "HARDER",
            "PREREQUISITE_REVIEW",
            "TRANSFER",
        }:
            return cast(AssignedPath, text)
        return "IMPROVE"

    @staticmethod
    def _parse_risk_level(value: Any, fallback: str) -> str:
        text = str(value).strip().lower()
        if text in {"high", "medium", "low"}:
            return text
        return fallback

    @staticmethod
    def _parse_readiness_level(value: Any, fallback: str) -> str:
        text = str(value).strip().lower()
        if text in {"emerging", "developing", "ready"}:
            return text
        return fallback

    @staticmethod
    def _clamp_float(value: Any, fallback: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return fallback
