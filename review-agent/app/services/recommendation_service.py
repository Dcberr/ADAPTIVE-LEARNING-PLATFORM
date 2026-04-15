from __future__ import annotations

from typing import Any, cast

from langgraph.graph import StateGraph
from openai import OpenAI

from app.api.recommendation_schema import (
    ExplanationBlock,
    ExplanationRef,
    RecommendationExercise,
    RecommendationGraphSummary,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationRoadmapStep,
)
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath
from app.models.recommendation_framework import RecommendationScoringFramework
from app.models.recommendation_state import RecommendationState
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.utils.parse_json_response import safe_parse_json_response


class RecommendationService:
    """LLM-led recommendation flow with constrained graph retrieval."""

    EXTRA_CONTEXT_BLOCKS = {
        "review_trend",
        "submission_trend",
        "exercise_graph",
        "concept_progression",
        "student_history",
    }

    def __init__(
        self,
        knowledge_graph_repository: KnowledgeGraphRepository,
        client: OpenAI,
        model_name: str,
        temperature: float = 0.2,
        max_tokens: int = 1400,
    ):
        self.knowledge_graph_repository = knowledge_graph_repository
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.workflow = self._build_workflow()

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        initial_state: RecommendationState = {
            "student_id": request.student_id,
            "exercise_id": request.exercise_id,
            "base_context": {},
            "context_plan": {},
            "loaded_blocks": [],
            "anchor_concept": "",
            "anchor_concept_weight": 0.0,
            "current_concept": "",
            "review": None,
            "review_record": None,
            "review_history": [],
            "student_profile": None,
            "latest_submission": None,
            "previous_review_payload": None,
            "previous_submission_payload": None,
            "mastered_concepts": [],
            "attempted_exercise_ids": [],
            "critical_errors": 0,
            "latest_review_improvement_signal": 0.0,
            "latest_review_severity_change": 0.0,
            "latest_submission_improvement_ratio": 0.0,
            "latest_submission_regression_ratio": 0.0,
            "exercise_graph": {},
            "concept_progression": [],
            "assigned_path": "IMPROVE",
            "path_decision_confidence": 0.0,
            "path_decision_reason": "",
            "focus_concept_id": "",
            "reasoning": {"content": "", "refs": []},
            "framework": RecommendationScoringFramework(
                risk_level="medium",
                readiness_level="developing",
                explanation="",
            ),
            "graph_summary": {},
            "retrieved_candidates": [],
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
        workflow.add_node("base_context_loader", self._base_context_loader)
        workflow.add_node("context_planner", self._context_planner)
        workflow.add_node("conditional_context_loader", self._conditional_context_loader)
        workflow.add_node("path_decider", self._path_decider)
        workflow.add_node("candidate_retriever", self._candidate_retriever)
        workflow.add_node("roadmap_builder", self._roadmap_builder)
        workflow.add_node("explanation_builder", self._explanation_builder)
        workflow.set_entry_point("base_context_loader")
        workflow.add_edge("base_context_loader", "context_planner")
        workflow.add_edge("context_planner", "conditional_context_loader")
        workflow.add_edge("conditional_context_loader", "path_decider")
        workflow.add_edge("path_decider", "candidate_retriever")
        workflow.add_edge("candidate_retriever", "roadmap_builder")
        workflow.add_edge("roadmap_builder", "explanation_builder")
        workflow.set_finish_point("explanation_builder")
        return workflow.compile()

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
        new_state["student_profile"] = context["student_profile"]
        new_state["latest_submission"] = context["latest_submission"]
        new_state["mastered_concepts"] = context["mastered_concepts"]
        new_state["attempted_exercise_ids"] = context["attempted_exercise_ids"]
        new_state["critical_errors"] = context["critical_errors"]
        new_state["focus_concept_id"] = context["current_concept"]
        return cast(RecommendationState, new_state)

    def _context_planner(self, state: RecommendationState) -> RecommendationState:
        plan = self._fallback_context_plan(state)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a context-loading planner for a CS1 exercise recommendation flow. "
                            "Choose only from these extra context blocks: review_trend, submission_trend, "
                            "exercise_graph, concept_progression, student_history. Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_context_planner_prompt(state)},
                ],
                temperature=0.1,
                max_tokens=min(self.max_tokens, 900),
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
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
                    "priority_signal": priority_signal or plan["priority_signal"],
                    "reason": reason or plan["reason"],
                }
        except Exception:
            pass

        new_state = dict(state)
        new_state["context_plan"] = plan
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
        concept_progression = list(state["concept_progression"])
        previous_review_payload = state["previous_review_payload"]
        previous_submission_payload = state["previous_submission_payload"]
        latest_review_improvement_signal = state["latest_review_improvement_signal"]
        latest_review_severity_change = state["latest_review_severity_change"]
        latest_submission_improvement_ratio = state["latest_submission_improvement_ratio"]
        latest_submission_regression_ratio = state["latest_submission_regression_ratio"]
        attempted_exercise_ids = list(state["attempted_exercise_ids"])

        if "review_trend" in blocks and review_record is not None:
            review_trend = self.knowledge_graph_repository.fetch_review_trend_context(
                review_id=review_record.review_id,
                student_id=state["student_id"],
            )
            review_history = review_trend["review_history"]
            latest_review_improvement_signal = review_trend[
                "latest_review_improvement_signal"
            ]
            latest_review_severity_change = review_trend[
                "latest_review_severity_change"
            ]
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

        if "concept_progression" in blocks and state["anchor_concept"]:
            concept_progression = (
                self.knowledge_graph_repository.fetch_concept_progression_context(
                    current_concept=state["anchor_concept"],
                    attempted_exercise_ids=attempted_exercise_ids,
                    mastered_concepts=state["mastered_concepts"],
                )
            )
            loaded_blocks.append("concept_progression")

        if "student_history" in blocks:
            history = self.knowledge_graph_repository.fetch_student_history_context(
                student_id=state["student_id"]
            )
            attempted_exercise_ids = history.get("attempted_exercise_ids", [])
            loaded_blocks.append("student_history")

        new_state = dict(state)
        new_state["loaded_blocks"] = loaded_blocks
        new_state["review_history"] = review_history
        new_state["exercise_graph"] = exercise_graph
        new_state["concept_progression"] = concept_progression
        new_state["previous_review_payload"] = previous_review_payload
        new_state["previous_submission_payload"] = previous_submission_payload
        new_state["latest_review_improvement_signal"] = latest_review_improvement_signal
        new_state["latest_review_severity_change"] = latest_review_severity_change
        new_state["latest_submission_improvement_ratio"] = (
            latest_submission_improvement_ratio
        )
        new_state["latest_submission_regression_ratio"] = (
            latest_submission_regression_ratio
        )
        new_state["attempted_exercise_ids"] = attempted_exercise_ids
        return cast(RecommendationState, new_state)

    def _path_decider(self, state: RecommendationState) -> RecommendationState:
        decision = self._fallback_path_decision(state)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a CS1 recommendation path decider. "
                            "Choose one assigned_path from REINFORCE, IMPROVE, NEXT_CONCEPT. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_path_decider_prompt(state)},
                ],
                temperature=0.1,
                max_tokens=min(self.max_tokens, 900),
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            assigned_path = self._parse_assigned_path(parsed.get("assigned_path"))
            focus_concept_id = str(
                parsed.get("focus_concept_id", decision["focus_concept_id"])
            ).strip() or decision["focus_concept_id"]
            valid_focus_ids = self._valid_focus_concept_ids(state)
            if focus_concept_id not in valid_focus_ids:
                focus_concept_id = decision["focus_concept_id"]
            confidence = self._clamp_float(parsed.get("confidence"), decision["confidence"])
            risk_level = self._parse_risk_level(
                parsed.get("risk_level"), decision["risk_level"]
            )
            readiness_level = self._parse_readiness_level(
                parsed.get("readiness_level"), decision["readiness_level"]
            )
            reason = str(parsed.get("reason", "")).strip() or decision["reason"]
            decision = {
                "assigned_path": assigned_path,
                "focus_concept_id": focus_concept_id,
                "confidence": confidence,
                "risk_level": risk_level,
                "readiness_level": readiness_level,
                "reason": reason,
            }
        except Exception:
            pass

        new_state = dict(state)
        new_state["assigned_path"] = decision["assigned_path"]
        new_state["focus_concept_id"] = decision["focus_concept_id"]
        new_state["path_decision_confidence"] = decision["confidence"]
        new_state["path_decision_reason"] = decision["reason"]
        new_state["framework"] = RecommendationScoringFramework(
            risk_level=cast(Any, decision["risk_level"]),
            readiness_level=cast(Any, decision["readiness_level"]),
            explanation=decision["reason"],
        )
        return cast(RecommendationState, new_state)

    def _candidate_retriever(self, state: RecommendationState) -> RecommendationState:
        focus_concept_id = state["focus_concept_id"] or state["anchor_concept"]
        if (
            state["assigned_path"] == "NEXT_CONCEPT"
            and focus_concept_id == state["anchor_concept"]
            and state["concept_progression"]
        ):
            focus_concept_id = state["concept_progression"][0]["concept_id"]

        candidates = self.knowledge_graph_repository.retrieve_candidates(
            student_id=state["student_id"],
            current_exercise_id=state["exercise_id"],
            current_concept=state["anchor_concept"],
            target_concept=focus_concept_id,
            assigned_path=state["assigned_path"],
            attempted_exercise_ids=state["attempted_exercise_ids"],
            limit=12,
        )
        if not candidates and state["assigned_path"] != "IMPROVE":
            candidates = self.knowledge_graph_repository.retrieve_candidates(
                student_id=state["student_id"],
                current_exercise_id=state["exercise_id"],
                current_concept=state["anchor_concept"],
                target_concept=state["anchor_concept"],
                assigned_path="IMPROVE",
                attempted_exercise_ids=state["attempted_exercise_ids"],
                limit=12,
            )

        new_state = dict(state)
        new_state["focus_concept_id"] = focus_concept_id
        new_state["retrieved_candidates"] = candidates
        return cast(RecommendationState, new_state)

    def _roadmap_builder(self, state: RecommendationState) -> RecommendationState:
        candidates = state["retrieved_candidates"]
        if not candidates:
            raise ValueError("Neo4j did not return any recommendation roadmap candidates.")

        selected_ids: list[str] = []
        directives: list[str] = []
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a CS1 roadmap selector. Choose the most important exercises "
                            "from the provided candidate list. Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_roadmap_prompt(state)},
                ],
                temperature=0.2,
                max_tokens=min(self.max_tokens, 1200),
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
            selected_candidates = candidates[:3]

        selected_exercises = [candidate["exercise"] for candidate in selected_candidates]
        if len(directives) < len(selected_exercises):
            directives = self._fallback_directives(state, selected_exercises)
        else:
            directives = directives[: len(selected_exercises)]

        best_candidate = selected_candidates[0]
        graph_summary = {
            "current_concept_weight": state["anchor_concept_weight"],
            "best_path_weight": float(best_candidate["path_weight"] or 0.0),
            "best_related_exercise_weight": float(best_candidate["related_weight"] or 0.0),
            "latest_review_improvement_signal": state["latest_review_improvement_signal"],
            "latest_review_severity_change": state["latest_review_severity_change"],
            "latest_submission_improvement_ratio": state[
                "latest_submission_improvement_ratio"
            ],
            "latest_submission_regression_ratio": state[
                "latest_submission_regression_ratio"
            ],
        }

        new_state = dict(state)
        new_state["selected_candidates"] = selected_candidates
        new_state["selected_exercises"] = selected_exercises
        new_state["roadmap_directives"] = directives
        new_state["graph_summary"] = graph_summary
        return cast(RecommendationState, new_state)

    def _explanation_builder(self, state: RecommendationState) -> RecommendationState:
        selected_exercises = state["selected_exercises"]
        if not selected_exercises:
            raise ValueError("Explanation builder requires selected exercises.")

        ref_catalog = self._build_reference_catalog(state)
        fallback_reasoning = self._fallback_reasoning_block(state, ref_catalog)
        fallback_summary = self._fallback_roadmap_summary_block(state, ref_catalog)

        reasoning = fallback_reasoning
        roadmap_summary = fallback_summary
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a CS1 recommendation explainer. Use only the provided refs. "
                            "Write reasoning_content and roadmap_summary_content with placeholders like {ref_id}. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_explanation_prompt(state, ref_catalog)},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            parsed = safe_parse_json_response(response.choices[0].message.content)
            reasoning = self._make_explanation_block(
                content=str(parsed.get("reasoning_content", "")).strip(),
                ref_ids=parsed.get("reasoning_ref_ids") or [],
                ref_catalog=ref_catalog,
                fallback=fallback_reasoning,
            )
            roadmap_summary = self._make_explanation_block(
                content=str(parsed.get("roadmap_summary_content", "")).strip(),
                ref_ids=parsed.get("roadmap_summary_ref_ids") or [],
                ref_catalog=ref_catalog,
                fallback=fallback_summary,
            )
        except Exception:
            pass

        new_state = dict(state)
        new_state["reasoning"] = reasoning
        new_state["roadmap_summary"] = roadmap_summary
        return cast(RecommendationState, new_state)

    def _build_context_planner_prompt(self, state: RecommendationState) -> str:
        base = state["base_context"]
        review = cast(Any, base["review"])
        profile = cast(Any, base["student_profile"])
        latest_submission = base.get("latest_submission")
        return (
            "Decide which extra context blocks are needed before path selection.\n"
            f"Student: {state['student_id']}\n"
            f"Current exercise: {state['exercise_id']}\n"
            f"Anchor concept: {base['current_concept']}\n"
            f"Critical errors: {base['critical_errors']}\n"
            f"Review summary: {review.summary}\n"
            f"Review detail: {review.detail}\n"
            f"Tested concepts: {base['tested_concepts']}\n"
            f"Recommended paths on current exercise: {base['recommended_paths']}\n"
            f"Has latest submission: {latest_submission is not None}\n"
            f"Student profile: concept_mastery={profile.concept_mastery}, "
            f"debugging_independence={profile.debugging_independence}, "
            f"concept_transfer={profile.concept_transfer}, "
            f"learning_velocity={profile.learning_velocity}\n"
            "Return JSON with:\n"
            "{\n"
            '  "need_review_trend": true|false,\n'
            '  "need_submission_trend": true|false,\n'
            '  "need_exercise_graph": true|false,\n'
            '  "need_concept_progression": true|false,\n'
            '  "need_student_history": true|false,\n'
            '  "provisional_focus_concept_id": "string",\n'
            '  "priority_signal": "string",\n'
            '  "reason": "string"\n'
            "}"
        )

    def _build_path_decider_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        profile = state["student_profile"]
        next_concepts = [item["concept_id"] for item in state["concept_progression"]]
        return (
            "Choose the most appropriate next recommendation path.\n"
            f"Anchor concept: {state['anchor_concept']}\n"
            f"Suggested focus concept: {state['context_plan'].get('provisional_focus_concept_id', state['anchor_concept'])}\n"
            f"Critical errors: {state['critical_errors']}\n"
            f"Latest review summary: {review.summary if review else ''}\n"
            f"Latest review improvement signal: {state['latest_review_improvement_signal']}\n"
            f"Latest review severity change: {state['latest_review_severity_change']}\n"
            f"Latest submission improvement ratio: {state['latest_submission_improvement_ratio']}\n"
            f"Latest submission regression ratio: {state['latest_submission_regression_ratio']}\n"
            f"Exercise graph summary: {state['exercise_graph']}\n"
            f"Next concept candidates: {state['concept_progression']}\n"
            f"Student profile: {profile.model_dump() if profile else {}}\n"
            f"Valid focus concepts: {self._valid_focus_concept_ids(state)}\n"
            "Return JSON with:\n"
            "{\n"
            '  "assigned_path": "REINFORCE|IMPROVE|NEXT_CONCEPT",\n'
            '  "focus_concept_id": "string",\n'
            '  "confidence": 0.0,\n'
            '  "risk_level": "high|medium|low",\n'
            '  "readiness_level": "emerging|developing|ready",\n'
            '  "reason": "string"\n'
            "}"
        )

    def _build_roadmap_prompt(self, state: RecommendationState) -> str:
        candidates = []
        for candidate in state["retrieved_candidates"][:8]:
            exercise = candidate["exercise"]
            candidates.append(
                {
                    "exercise_id": exercise.exercise_id,
                    "title": exercise.title,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "tags": exercise.tags,
                    "path_weight": candidate["path_weight"],
                    "tests_weight": candidate["tests_weight"],
                    "related_weight": candidate["related_weight"],
                    "progression_score": candidate["progression_score"],
                    "similarity_score": candidate["similarity_score"],
                    "relation_type": candidate["relation_type"],
                    "difficulty_gap": candidate["difficulty_gap"],
                }
            )
        return (
            "Select up to 3 exercises for the roadmap in order.\n"
            f"Assigned path: {state['assigned_path']}\n"
            f"Focus concept: {state['focus_concept_id']}\n"
            f"Path reason: {state['path_decision_reason']}\n"
            f"Candidates: {candidates}\n"
            "Return JSON with:\n"
            "{\n"
            '  "exercise_ids": ["id1", "id2"],\n'
            '  "directives": ["step 1 directive", "step 2 directive"]\n'
            "}"
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
        return (
            "Explain the roadmap using only the provided refs.\n"
            f"Assigned path: {state['assigned_path']}\n"
            f"Anchor concept: {state['anchor_concept']}\n"
            f"Focus concept: {state['focus_concept_id']}\n"
            f"Path reason: {state['path_decision_reason']}\n"
            f"Selected exercises: {selected_exercises}\n"
            f"Available refs: {refs}\n"
            "Return JSON with:\n"
            "{\n"
            '  "reasoning_content": "text with {ref_id}",\n'
            '  "reasoning_ref_ids": ["ref_1"],\n'
            '  "roadmap_summary_content": "text with {ref_id}",\n'
            '  "roadmap_summary_ref_ids": ["ref_2"]\n'
            "}"
        )

    def _fallback_context_plan(self, state: RecommendationState) -> dict[str, Any]:
        latest_submission = state["latest_submission"]
        critical_errors = state["critical_errors"]
        blocks = ["exercise_graph", "review_trend", "student_history"]
        if latest_submission is not None:
            blocks.append("submission_trend")
        if critical_errors == 0:
            blocks.append("concept_progression")
        return {
            "blocks": blocks,
            "provisional_focus_concept_id": state["anchor_concept"],
            "priority_signal": (
                "current_review_issue" if critical_errors > 0 else "progress_readiness"
            ),
            "reason": "Fallback context plan loads trend, graph, and history before path selection.",
        }

    def _fallback_path_decision(self, state: RecommendationState) -> dict[str, Any]:
        profile = state["student_profile"]
        mastery = profile.concept_mastery if profile else 0.5
        debugging = profile.debugging_independence if profile else 0.5
        if (
            state["critical_errors"] >= 2
            or state["latest_submission_regression_ratio"] > state["latest_submission_improvement_ratio"]
            or debugging < 0.45
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
            mastery >= 0.7
            and state["latest_review_improvement_signal"] >= 0.35
            and state["latest_submission_regression_ratio"] <= 0.05
            and state["concept_progression"]
        ):
            return {
                "assigned_path": "NEXT_CONCEPT",
                "focus_concept_id": state["concept_progression"][0]["concept_id"],
                "confidence": 0.62,
                "risk_level": "low",
                "readiness_level": "ready",
                "reason": "The student is showing stable progress and has a viable next concept available.",
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
        if state["assigned_path"] == "REINFORCE":
            prefix = "Stabilize the same concept with this practice task."
        elif state["assigned_path"] == "NEXT_CONCEPT":
            prefix = "Use this exercise as the next concept step."
        else:
            prefix = "Use this exercise to improve the current concept with a slightly broader task."
        return [f"Step {index}: {prefix}" for index, _ in enumerate(exercises, start=1)]

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
        focus_ids.update(item["concept_id"] for item in state["concept_progression"])
        return [concept_id for concept_id in focus_ids if concept_id]

    @staticmethod
    def _parse_assigned_path(value: Any) -> AssignedPath:
        text = str(value).strip().upper()
        if text in {"REINFORCE", "IMPROVE", "NEXT_CONCEPT"}:
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
