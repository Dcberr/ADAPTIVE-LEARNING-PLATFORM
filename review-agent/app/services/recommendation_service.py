from __future__ import annotations

from typing import Any, cast

from langgraph.graph import StateGraph
from openai import OpenAI

from app.api.recommendation_schema import (
    RecommendationExercise,
    RecommendationGraphSummary,
    RecommendationRequest,
    RecommendationRoadmapStep,
    RecommendationResponse,
)
from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import AssignedPath
from app.models.recommendation_framework import RecommendationScoringFramework
from app.models.recommendation_state import RecommendationState
from app.services.knowledge_graph_repository import KnowledgeGraphRepository
from app.utils.parse_json_response import safe_parse_json_response


class RecommendationService:
    """Graph-first recommendation flow with LLM explanation only."""

    QUERY_PLANS = {
        "review_reinforce_plan": {
            "start_entity": "Review",
            "assigned_path": "REINFORCE",
        },
        "review_improve_plan": {
            "start_entity": "Review",
            "assigned_path": "IMPROVE",
        },
        "concept_next_concept_plan": {
            "start_entity": "Concept",
            "assigned_path": "NEXT_CONCEPT",
        },
        "submission_progress_plan": {
            "start_entity": "Submission",
            "assigned_path": "IMPROVE",
        },
        "exercise_related_plan": {
            "start_entity": "Exercise",
            "assigned_path": "IMPROVE",
        },
        "full_progression_plan": {
            "start_entity": "Student",
            "assigned_path": "IMPROVE",
        },
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
            "planner_start_entity": "",
            "planner_query_plan_id": "",
            "planner_confidence": 0.0,
            "planner_rationale": "",
            "planner_target_concept_hint": "",
            "anchor_concept": "",
            "anchor_concept_weight": 0.0,
            "current_concept": "",
            "review": None,
            "review_history": [],
            "student_profile": None,
            "mastered_concepts": [],
            "attempted_exercise_ids": [],
            "critical_errors": 0,
            "latest_review_improvement_signal": 0.0,
            "latest_review_severity_change": 0.0,
            "latest_submission_improvement_ratio": 0.0,
            "latest_submission_regression_ratio": 0.0,
            "assigned_path": "IMPROVE",
            "target_concept": "",
            "reasoning": "",
            "framework": RecommendationScoringFramework(
                risk_level="medium",
                readiness_level="developing",
                explanation="",
            ),
            "graph_summary": {},
            "retrieved_candidates": [],
            "target_concept_candidates": [],
            "selected_exercises": [],
            "roadmap_directives": [],
            "roadmap_summary": "",
        }

        final_state = cast(RecommendationState, self.workflow.invoke(initial_state))
        selected_exercises = final_state["selected_exercises"]
        if not selected_exercises:
            raise ValueError("No exercises found in Neo4j for this recommendation roadmap.")

        self.knowledge_graph_repository.store_recommendation_roadmap(
            student_id=final_state["student_id"],
            assigned_path=final_state["assigned_path"],
            target_concept=final_state["target_concept"],
            exercise_ids=[exercise.exercise_id for exercise in selected_exercises],
            review_id=final_state["review"].review_id if final_state["review"] else None,
        )
        exercise_concept_map = self.knowledge_graph_repository.get_concept_ids_by_exercise(
            [exercise.exercise_id for exercise in selected_exercises]
        )

        return RecommendationResponse(
            student_id=final_state["student_id"],
            current_exercise_id=final_state["exercise_id"],
            anchor_concept=final_state["anchor_concept"],
            assigned_path=final_state["assigned_path"],
            focus_concept_id=final_state["target_concept"],
            critical_errors=final_state["critical_errors"],
            framework=final_state["framework"],
            graph_summary=RecommendationGraphSummary.model_validate(
                final_state["graph_summary"]
            ),
            reasoning=final_state["reasoning"],
            roadmap_summary=final_state["roadmap_summary"],
            roadmap=[
                RecommendationRoadmapStep(
                    step=index,
                    exercise=RecommendationExercise(
                        concept_ids=exercise_concept_map.get(exercise.exercise_id, []),
                        directive=final_state["roadmap_directives"][index - 1],
                        **exercise.model_dump(),
                    ),
                )
                for index, (exercise, candidate) in enumerate(
                    zip(selected_exercises, final_state["retrieved_candidates"][: len(selected_exercises)]),
                    start=1,
                )
            ],
        )

    def _build_workflow(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("review_context_loader", self._review_context_loader)
        workflow.add_node("query_planner", self._query_planner)
        workflow.add_node("path_selector", self._path_selector)
        workflow.add_node("target_concept_selector", self._target_concept_selector)
        workflow.add_node("candidate_retriever", self._candidate_retriever)
        workflow.add_node("roadmap_builder", self._roadmap_builder)
        workflow.add_node("explanation_builder", self._explanation_builder)
        workflow.set_entry_point("review_context_loader")
        workflow.add_edge("review_context_loader", "query_planner")
        workflow.add_edge("query_planner", "path_selector")
        workflow.add_edge("path_selector", "target_concept_selector")
        workflow.add_edge("target_concept_selector", "candidate_retriever")
        workflow.add_edge("candidate_retriever", "roadmap_builder")
        workflow.add_edge("roadmap_builder", "explanation_builder")
        workflow.set_finish_point("explanation_builder")
        return workflow.compile()

    def _review_context_loader(self, state: RecommendationState) -> RecommendationState:
        context = self.knowledge_graph_repository.get_recommendation_context(
            student_id=state["student_id"],
            exercise_id=state["exercise_id"],
        )
        review = context["review"]
        critical_errors = sum(1 for item in review.review_items if item.type == "Error")

        new_state = dict(state)
        new_state["anchor_concept"] = context["current_concept"]
        new_state["anchor_concept_weight"] = context["current_concept_weight"]
        new_state["current_concept"] = context["current_concept"]
        new_state["review"] = review
        new_state["review_history"] = context["review_history"]
        new_state["student_profile"] = context["student_profile"]
        new_state["mastered_concepts"] = context["mastered_concepts"]
        new_state["attempted_exercise_ids"] = context["attempted_exercise_ids"]
        new_state["critical_errors"] = critical_errors
        new_state["latest_review_improvement_signal"] = context[
            "latest_review_improvement_signal"
        ]
        new_state["latest_review_severity_change"] = context[
            "latest_review_severity_change"
        ]
        new_state["latest_submission_improvement_ratio"] = context[
            "latest_submission_improvement_ratio"
        ]
        new_state["latest_submission_regression_ratio"] = context[
            "latest_submission_regression_ratio"
        ]
        return cast(RecommendationState, new_state)

    def _query_planner(self, state: RecommendationState) -> RecommendationState:
        fallback_query_plan_id = self._fallback_query_plan_id(state)
        fallback_plan = self.QUERY_PLANS[fallback_query_plan_id]

        planned_query_plan_id = fallback_query_plan_id
        planned_start_entity = fallback_plan["start_entity"]
        planned_assigned_path = cast(AssignedPath, fallback_plan["assigned_path"])
        planned_target_concept_hint = state["anchor_concept"]
        planner_rationale = (
            "Planner fallback selected the safest fixed plan from current review, "
            "trend, and graph signals."
        )
        planner_confidence = 0.5

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a graph query planner for CS1 exercise recommendation. "
                            "Choose one fixed query_plan_id from the allowed list only. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_planner_prompt(state)},
                ],
                temperature=0.1,
                max_tokens=min(self.max_tokens, 900),
            )
            model_text = response.choices[0].message.content
            parsed = safe_parse_json_response(model_text)
            candidate_query_plan_id = str(parsed.get("query_plan_id", "")).strip()
            if candidate_query_plan_id in self.QUERY_PLANS:
                selected_plan = self.QUERY_PLANS[candidate_query_plan_id]
                planned_query_plan_id = candidate_query_plan_id
                planned_start_entity = str(parsed.get("start_entity") or selected_plan["start_entity"])
                planned_assigned_path = cast(
                    AssignedPath,
                    parsed.get("assigned_path") or selected_plan["assigned_path"],
                )
                planned_target_concept_hint = (
                    str(parsed.get("target_concept_hint") or state["anchor_concept"]).strip()
                    or state["anchor_concept"]
                )
                planner_rationale = (
                    str(parsed.get("rationale", "")).strip() or planner_rationale
                )
                try:
                    planner_confidence = max(
                        0.0,
                        min(1.0, float(parsed.get("confidence", planner_confidence))),
                    )
                except (TypeError, ValueError):
                    planner_confidence = 0.5
        except Exception:
            pass

        new_state = dict(state)
        new_state["planner_query_plan_id"] = planned_query_plan_id
        new_state["planner_start_entity"] = planned_start_entity
        new_state["planner_confidence"] = planner_confidence
        new_state["planner_rationale"] = planner_rationale
        new_state["planner_target_concept_hint"] = planned_target_concept_hint
        new_state["assigned_path"] = planned_assigned_path
        return cast(RecommendationState, new_state)

    def _path_selector(self, state: RecommendationState) -> RecommendationState:
        review = state["review"]
        profile = state["student_profile"]
        if review is None or profile is None:
            raise ValueError("Recommendation requires review and student profile context.")

        scorecard_average = self._scorecard_average(review.scorecard.model_dump())
        error_pressure = min(1.0, state["critical_errors"] / 3.0)
        reinforce_score = min(
            1.0,
            0.35 * error_pressure
            + 0.20 * (1.0 - scorecard_average)
            + 0.20 * state["latest_submission_regression_ratio"]
            + 0.15 * max(-state["latest_review_severity_change"], 0.0)
            + 0.10 * max(0.0, 0.6 - profile.debugging_independence),
        )
        improve_score = min(
            1.0,
            0.30 * state["latest_review_improvement_signal"]
            + 0.25 * state["latest_submission_improvement_ratio"]
            + 0.20 * min(1.0, state["critical_errors"] / 2.0)
            + 0.15 * (1.0 - abs(scorecard_average - 0.6))
            + 0.10 * (1.0 - max(profile.concept_mastery - 0.7, 0.0)),
        )
        next_concept_score = min(
            1.0,
            0.30 * scorecard_average
            + 0.25 * state["latest_review_improvement_signal"]
            + 0.20 * state["latest_submission_improvement_ratio"]
            + 0.15 * profile.concept_mastery
            + 0.10 * profile.learning_velocity
            - 0.20 * error_pressure,
        )

        scores = {
            "REINFORCE": reinforce_score,
            "IMPROVE": improve_score,
            "NEXT_CONCEPT": max(0.0, next_concept_score),
        }
        assigned_path = cast(AssignedPath, max(scores, key=scores.get))

        planned_path = state["assigned_path"]
        if state["planner_confidence"] >= 0.6 and planned_path in scores:
            planned_score = scores[planned_path]
            best_score = scores[assigned_path]
            if planned_score + 0.15 >= best_score:
                assigned_path = planned_path

        risk_level = "medium"
        if reinforce_score >= 0.55:
            risk_level = "high"
        elif next_concept_score >= 0.55 and error_pressure < 0.2:
            risk_level = "low"

        readiness_level = "developing"
        if next_concept_score >= 0.6:
            readiness_level = "ready"
        elif reinforce_score >= 0.55:
            readiness_level = "emerging"

        new_state = dict(state)
        new_state["assigned_path"] = assigned_path
        new_state["framework"] = RecommendationScoringFramework(
            risk_level=cast(Any, risk_level),
            readiness_level=cast(Any, readiness_level),
            explanation=(
                "Risk level reflects how cautious the roadmap should be based on current errors and recent trend. "
                "Readiness level reflects whether the student should reinforce, improve, or move to a next concept."
            ),
        )
        return cast(RecommendationState, new_state)

    def _target_concept_selector(self, state: RecommendationState) -> RecommendationState:
        assigned_path = state["assigned_path"]
        target_concept = state["planner_target_concept_hint"] or state["anchor_concept"]
        target_candidates: list[dict[str, Any]] = []

        if assigned_path == "NEXT_CONCEPT":
            target_candidates = self.knowledge_graph_repository.get_next_concept_candidates(
                current_concept=state["anchor_concept"],
                attempted_exercise_ids=state["attempted_exercise_ids"],
                mastered_concepts=state["mastered_concepts"],
            )
            if target_candidates:
                profile = state["student_profile"]
                readiness = (
                    (
                        profile.concept_mastery
                        + profile.concept_transfer
                        + profile.learning_velocity
                    )
                    / 3.0
                    if profile is not None
                    else 0.5
                )
                for candidate in target_candidates:
                    candidate["score"] = (
                        0.50 * candidate["prerequisite_strength"]
                        + 0.30 * candidate["best_path_weight"]
                        + 0.20 * readiness
                    )
                target_candidates.sort(key=lambda item: item["score"], reverse=True)
                target_concept = target_candidates[0]["concept_id"]
        elif state["planner_target_concept_hint"]:
            target_concept = state["planner_target_concept_hint"]

        new_state = dict(state)
        new_state["target_concept"] = target_concept
        new_state["target_concept_candidates"] = target_candidates
        return cast(RecommendationState, new_state)

    def _candidate_retriever(self, state: RecommendationState) -> RecommendationState:
        candidates = self.knowledge_graph_repository.retrieve_candidates(
            student_id=state["student_id"],
            current_exercise_id=state["exercise_id"],
            current_concept=state["anchor_concept"],
            target_concept=state["target_concept"],
            assigned_path=state["assigned_path"],
            attempted_exercise_ids=state["attempted_exercise_ids"],
            limit=10 if state["planner_query_plan_id"] == "full_progression_plan" else 8,
        )
        ranked_candidates = self._rank_candidates(state, candidates)

        new_state = dict(state)
        new_state["retrieved_candidates"] = ranked_candidates
        return cast(RecommendationState, new_state)

    def _roadmap_builder(self, state: RecommendationState) -> RecommendationState:
        candidates = state["retrieved_candidates"]
        if not candidates:
            raise ValueError("Neo4j did not return any recommendation roadmap candidates.")

        selected_candidates: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for candidate in candidates:
            exercise_id = candidate["exercise"].exercise_id
            if exercise_id in seen_ids:
                continue
            selected_candidates.append(candidate)
            seen_ids.add(exercise_id)
            if len(selected_candidates) == 3:
                break

        if not selected_candidates:
            raise ValueError("No unique exercise candidates found for roadmap.")

        best_candidate = selected_candidates[0]
        graph_summary = {
            "current_concept_weight": state["anchor_concept_weight"],
            "best_path_weight": best_candidate["path_weight"],
            "best_related_exercise_weight": best_candidate["related_weight"],
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
        new_state["retrieved_candidates"] = selected_candidates
        new_state["selected_exercises"] = [
            candidate["exercise"] for candidate in selected_candidates
        ]
        new_state["graph_summary"] = graph_summary
        return cast(RecommendationState, new_state)

    def _explanation_builder(self, state: RecommendationState) -> RecommendationState:
        exercises = state["selected_exercises"]
        if not exercises:
            raise ValueError("Explanation builder requires selected exercises.")

        reasoning = self._fallback_reasoning(state)
        roadmap_summary = self._fallback_roadmap_summary(state)
        directives = self._fallback_directives(state)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a CS1 recommendation explainer. "
                            "Do not change the selected path or exercises. "
                            "Explain the roadmap for the student in simple educational language. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": self._build_explainer_prompt(state)},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            model_text = response.choices[0].message.content
            parsed = safe_parse_json_response(model_text)
            reasoning = str(parsed.get("reasoning", "")).strip() or reasoning
            roadmap_summary = (
                str(parsed.get("roadmap_summary", "")).strip() or roadmap_summary
            )
            parsed_directives = parsed.get("directives") or []
            if isinstance(parsed_directives, list):
                cleaned = [str(item).strip() for item in parsed_directives if str(item).strip()]
                if len(cleaned) >= len(exercises):
                    directives = cleaned[: len(exercises)]
        except Exception:
            pass

        new_state = dict(state)
        new_state["reasoning"] = reasoning
        new_state["roadmap_summary"] = roadmap_summary
        new_state["roadmap_directives"] = directives
        return cast(RecommendationState, new_state)

    def _rank_candidates(
        self,
        state: RecommendationState,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        profile = state["student_profile"]
        if profile is None:
            raise ValueError("Recommendation requires a stored student profile.")

        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            graph_score = self._graph_candidate_score(state["assigned_path"], candidate)
            graph_score = self._apply_query_plan_bias(state, candidate, graph_score)
            profile_adjustment = self._profile_candidate_adjustment(
                state["assigned_path"], candidate, profile
            )
            final_score = max(
                0.0,
                min(1.0, 0.75 * graph_score + 0.25 * profile_adjustment),
            )
            enriched = dict(candidate)
            enriched["graph_score"] = graph_score
            enriched["profile_adjustment"] = profile_adjustment
            enriched["final_score"] = final_score
            enriched["assigned_path"] = (
                "NEXT_CONCEPT"
                if state["assigned_path"] == "NEXT_CONCEPT" and candidate["difficulty_gap"] > 0.2
                else state["assigned_path"]
            )
            ranked.append(enriched)

        ranked.sort(
            key=lambda item: (
                item["final_score"],
                item["path_weight"],
                item["related_weight"],
                item["progression_score"],
            ),
            reverse=True,
        )
        return ranked

    def _apply_query_plan_bias(
        self,
        state: RecommendationState,
        candidate: dict[str, Any],
        graph_score: float,
    ) -> float:
        plan_id = state["planner_query_plan_id"]
        adjusted = graph_score
        if plan_id == "review_reinforce_plan":
            adjusted += 0.10 * candidate["similarity_score"] + 0.05 * candidate["related_weight"]
        elif plan_id == "review_improve_plan":
            adjusted += 0.08 * candidate["progression_score"] + 0.05 * candidate["related_weight"]
        elif plan_id == "concept_next_concept_plan":
            adjusted += 0.10 * candidate["path_weight"] + 0.05 * max(candidate["difficulty_gap"], 0.0)
        elif plan_id == "submission_progress_plan":
            adjusted += 0.08 * state["latest_submission_improvement_ratio"] + 0.05 * candidate["progression_score"]
        elif plan_id == "exercise_related_plan":
            adjusted += 0.12 * candidate["related_weight"] + 0.06 * candidate["similarity_score"]
        elif plan_id == "full_progression_plan":
            adjusted += 0.05 * state["latest_review_improvement_signal"] + 0.05 * state["latest_submission_improvement_ratio"]
        return max(0.0, min(1.0, adjusted))

    def _graph_candidate_score(
        self, assigned_path: AssignedPath, candidate: dict[str, Any]
    ) -> float:
        path_fit = candidate["path_weight"]
        concept_fit = candidate["tests_weight"]
        related_fit = candidate["related_weight"]
        progression_fit = candidate["progression_score"]
        similarity_fit = candidate["similarity_score"]
        easier_fit = max(0.0, 1.0 - max(candidate["difficulty_gap"], 0.0))
        moderate_fit = max(0.0, 1.0 - abs(candidate["difficulty_gap"] - 0.3))
        next_step_fit = max(0.0, 1.0 - abs(candidate["difficulty_gap"] - 0.5))

        if assigned_path == "REINFORCE":
            return min(
                1.0,
                0.35 * path_fit
                + 0.25 * concept_fit
                + 0.20 * related_fit
                + 0.15 * similarity_fit
                + 0.05 * easier_fit,
            )
        if assigned_path == "NEXT_CONCEPT":
            return min(
                1.0,
                0.35 * path_fit
                + 0.25 * concept_fit
                + 0.20 * progression_fit
                + 0.10 * next_step_fit
                + 0.10 * max(candidate["related_weight"], 0.2),
            )
        return min(
            1.0,
            0.30 * path_fit
            + 0.25 * concept_fit
            + 0.20 * progression_fit
            + 0.15 * related_fit
            + 0.10 * moderate_fit,
        )

    def _profile_candidate_adjustment(
        self,
        assigned_path: AssignedPath,
        candidate: dict[str, Any],
        profile,
    ) -> float:
        if assigned_path == "REINFORCE":
            return min(
                1.0,
                0.40 * (1.0 - profile.debugging_independence)
                + 0.30 * (1.0 - profile.implementation_consistency)
                + 0.30 * max(0.0, 1.0 - max(candidate["difficulty_gap"], 0.0)),
            )
        if assigned_path == "NEXT_CONCEPT":
            return min(
                1.0,
                0.40 * profile.concept_mastery
                + 0.30 * profile.concept_transfer
                + 0.30 * profile.learning_velocity,
            )
        return min(
            1.0,
            0.35 * profile.implementation_consistency
            + 0.35 * profile.debugging_independence
            + 0.30 * profile.concept_transfer,
        )

    @staticmethod
    def _scorecard_average(scorecard: dict) -> float:
        scores = []
        for item in scorecard.values():
            raw_score = item.get("score")
            if raw_score is None:
                continue
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                continue
            scores.append(max(0.0, min(1.0, (score - 1.0) / 4.0)))
        return sum(scores) / len(scores) if scores else 0.0

    def _fallback_query_plan_id(self, state: RecommendationState) -> str:
        if state["critical_errors"] > 0 and state["latest_review_improvement_signal"] < 0.3:
            return "review_reinforce_plan"
        if state["latest_submission_regression_ratio"] > 0.2:
            return "submission_progress_plan"
        if state["latest_review_improvement_signal"] >= 0.45 and state["latest_submission_improvement_ratio"] >= 0.35:
            return "concept_next_concept_plan"
        if state["anchor_concept_weight"] >= 0.8:
            return "exercise_related_plan"
        return "review_improve_plan"

    def _fallback_reasoning(self, state: RecommendationState) -> str:
        if state["assigned_path"] == "REINFORCE":
            return (
                "The student still has important errors on the current concept, so the roadmap starts with "
                "the strongest similar practice before broadening the task."
            )
        if state["assigned_path"] == "NEXT_CONCEPT":
            return (
                "The student shows enough stability on the current concept, so the roadmap uses the strongest "
                "next-step concept and supporting exercises to move forward gradually."
            )
        return (
            "The student is improving but is not fully stable yet, so the roadmap keeps the same concept and "
            "uses the strongest nearby exercises to improve implementation quality step by step."
        )

    def _fallback_roadmap_summary(self, state: RecommendationState) -> str:
        count = len(state["selected_exercises"])
        if state["assigned_path"] == "REINFORCE":
            return (
                f"Start with {count} exercise(s) that strongly reinforce {state['target_concept']} before the student advances."
            )
        if state["assigned_path"] == "NEXT_CONCEPT":
            return (
                f"Use {count} exercise(s) to transition from {state['anchor_concept']} into {state['target_concept']} with gradual progression."
            )
        return (
            f"Use {count} exercise(s) to improve {state['target_concept']} through nearby practice and broader transfer."
        )

    def _fallback_directives(self, state: RecommendationState) -> list[str]:
        directives: list[str] = []
        for index, exercise in enumerate(state["selected_exercises"], start=1):
            if state["assigned_path"] == "REINFORCE":
                directive = (
                    f"Practice {exercise.title} to rebuild confidence in {state['target_concept']} with a similar exercise shape."
                )
            elif state["assigned_path"] == "NEXT_CONCEPT":
                directive = (
                    f"Use {exercise.title} to move from {state['anchor_concept']} toward {state['target_concept']} with one clear next step."
                )
            else:
                directive = (
                    f"Solve {exercise.title} to improve implementation quality in {state['target_concept']} before moving further."
                )
            directives.append(f"Step {index}: {directive}")
        return directives

    def _build_explainer_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        if review is None:
            raise ValueError("Recommendation explanation requires review context.")

        return f"""
Student ID: {state['student_id']}
Current exercise id: {state['exercise_id']}
Anchor concept: {state['anchor_concept']}
Assigned path: {state['assigned_path']}
Target concept: {state['target_concept']}

Latest review summary:
{review.summary}

Important review items:
{[item.model_dump() for item in review.review_items[:3]]}

Framework:
{state['framework'].model_dump()}

Graph summary:
{state['graph_summary']}

Selected exercises:
{[
    {
        "exercise_id": candidate["exercise"].exercise_id,
        "title": candidate["exercise"].title,
        "path_weight": candidate["path_weight"],
        "tests_weight": candidate["tests_weight"],
        "related_weight": candidate["related_weight"],
        "progression_score": candidate["progression_score"],
        "similarity_score": candidate["similarity_score"],
    }
    for candidate in state["retrieved_candidates"]
]}

Task:
1. Explain why this roadmap fits the student now.
2. Summarize the roadmap in one short paragraph.
3. Write one directive sentence for each selected exercise.

Return JSON only:
{{
  "reasoning": "string",
  "roadmap_summary": "string",
  "directives": ["string", "string", "string"]
}}
"""

    def _build_planner_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        profile = state["student_profile"]
        if review is None or profile is None:
            raise ValueError("Recommendation planner requires review and profile context.")

        scorecard = review.scorecard.model_dump()
        top_review_items = [item.model_dump() for item in review.review_items[:3]]

        return f"""
Allowed query plans:
- review_reinforce_plan
- review_improve_plan
- concept_next_concept_plan
- submission_progress_plan
- exercise_related_plan
- full_progression_plan

Allowed start entities:
- Review
- Submission
- Exercise
- Concept
- Student

Current request:
- student_id: {state['student_id']}
- exercise_id: {state['exercise_id']}

Latest review:
- summary: {review.summary}
- current_concept: {state['anchor_concept']}
- critical_errors: {state['critical_errors']}
- top_items: {top_review_items}
- scorecard_summary: {{
    "logic_traceability": {scorecard.get("logic_traceability", {}).get("score", 0)},
    "generalization_score": {scorecard.get("generalization_score", {}).get("score", 0)},
    "debugging_readiness": {scorecard.get("debugging_readiness", {}).get("score", 0)}
  }}

Review trend:
- latest_review_improvement_signal: {state['latest_review_improvement_signal']}
- latest_review_severity_change: {state['latest_review_severity_change']}

Submission trend:
- latest_submission_improvement_ratio: {state['latest_submission_improvement_ratio']}
- latest_submission_regression_ratio: {state['latest_submission_regression_ratio']}

Student profile:
- concept_mastery: {profile.concept_mastery}
- implementation_consistency: {profile.implementation_consistency}
- debugging_independence: {profile.debugging_independence}
- efficiency_awareness: {profile.efficiency_awareness}
- concept_transfer: {profile.concept_transfer}
- learning_velocity: {profile.learning_velocity}

Exercise graph summary:
- anchor_concept_weight: {state['anchor_concept_weight']}
- review_history_count: {len(state['review_history'])}
- attempted_exercise_count: {len(state['attempted_exercise_ids'])}

Choose the best query plan and start entity for recommending the next exercise roadmap.
Return JSON only:
{{
  "start_entity": "Review",
  "query_plan_id": "review_improve_plan",
  "assigned_path": "IMPROVE",
  "target_concept_hint": "{state['anchor_concept']}",
  "confidence": 0.84,
  "rationale": "short grounded reason"
}}
"""
