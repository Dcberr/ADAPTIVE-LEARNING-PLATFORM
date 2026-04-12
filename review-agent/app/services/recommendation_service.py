from __future__ import annotations

from typing import Any, cast

from langgraph.graph import StateGraph
from openai import OpenAI

from app.api.recommendation_schema import (
    RecommendationExercise,
    RecommendationRequest,
    RecommendationRoadmapStep,
    RecommendationResponse,
)
from app.models.knowledge_graph import AssignedPath
from app.models.recommendation_framework import RecommendationScoringFramework
from app.models.recommendation_state import RecommendationState
from app.services.knowledge_graph_repository import KnowledgeGraphRepository
from app.utils.parse_json_response import safe_parse_json_response


class RecommendationService:
    """LangGraph recommendation flow using Neo4j GraphRAG and stored review context."""

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
            "current_concept": "",
            "review": None,
            "review_history": [],
            "student_profile": None,
            "mastered_concepts": [],
            "attempted_exercise_ids": [],
            "critical_errors": 0,
            "assigned_path": "IMPROVE",
            "target_concept": "",
            "reasoning": "",
            "framework": RecommendationScoringFramework(
                foundation_risk=0,
                efficiency_gap=0,
                progression_readiness=0,
                support_need=0,
                explanation="",
            ),
            "retrieved_candidates": [],
            "selected_exercises": [],
            "roadmap_directives": [],
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

        return RecommendationResponse(
            student_id=final_state["student_id"],
            assigned_path=final_state["assigned_path"],
            target_concept=final_state["target_concept"],
            critical_errors=final_state["critical_errors"],
            framework=final_state["framework"],
            reasoning=final_state["reasoning"],
            roadmap_summary=self._build_roadmap_summary(final_state),
            roadmap=[
                RecommendationRoadmapStep(
                    step=index,
                    focus=self._build_step_focus(
                        final_state["assigned_path"],
                        final_state["target_concept"],
                        index,
                    ),
                    exercise=RecommendationExercise(
                        path=final_state["assigned_path"],
                        target_concept=final_state["target_concept"],
                        directive=final_state["roadmap_directives"][index - 1],
                        **exercise.model_dump(),
                    ),
                )
                for index, exercise in enumerate(selected_exercises, start=1)
            ],
        )

    def _build_roadmap_summary(self, state: RecommendationState) -> str:
        exercise_count = len(state["selected_exercises"])
        if state["assigned_path"] == "REINFORCE":
            return (
                f"This roadmap gives {exercise_count} reinforcing exercise(s) to rebuild the core idea in "
                f"{state['target_concept']} before the student advances."
            )
        if state["assigned_path"] == "NEXT_CONCEPT":
            return (
                f"This roadmap uses {exercise_count} exercise(s) to transition the student into "
                f"{state['target_concept']} with gradually increasing complexity."
            )
        return (
            f"This roadmap uses {exercise_count} exercise(s) to improve implementation quality in "
            f"{state['target_concept']} while keeping the student on the same conceptual track."
        )

    def _build_workflow(self):
        workflow = StateGraph(RecommendationState)
        workflow.add_node("review_context_loader", self._review_context_loader)
        workflow.add_node("profile_scorer", self._profile_scorer)
        workflow.add_node("graph_rag_retriever", self._graph_rag_retriever)
        workflow.add_node("recommendation_reasoner", self._recommendation_reasoner)
        workflow.add_node("directive_builder", self._directive_builder)
        workflow.set_entry_point("review_context_loader")
        workflow.add_edge("review_context_loader", "profile_scorer")
        workflow.add_edge("profile_scorer", "graph_rag_retriever")
        workflow.add_edge("graph_rag_retriever", "recommendation_reasoner")
        workflow.add_edge("recommendation_reasoner", "directive_builder")
        workflow.set_finish_point("directive_builder")
        return workflow.compile()

    def _review_context_loader(self, state: RecommendationState) -> RecommendationState:
        context = self.knowledge_graph_repository.get_recommendation_context(
            student_id=state["student_id"],
            exercise_id=state["exercise_id"],
        )
        new_state = dict(state)
        new_state["current_concept"] = context["current_concept"]
        new_state["review"] = context["review"]
        new_state["review_history"] = context["review_history"]
        new_state["student_profile"] = context["student_profile"]
        new_state["mastered_concepts"] = context["mastered_concepts"]
        new_state["attempted_exercise_ids"] = context["attempted_exercise_ids"]
        return cast(RecommendationState, new_state)

    def _profile_scorer(self, state: RecommendationState) -> RecommendationState:
        def normalize_scorecard(score: float) -> float:
            return max(0.0, min(1.0, (score - 1.0) / 4.0))

        review = state["review"]
        if review is None:
            raise ValueError("Recommendation requires a stored review context.")

        profile = state["student_profile"]
        if profile is None:
            raise ValueError("Recommendation requires a stored student profile.")
        error_count = sum(1 for item in review.review_items if item.type == "Error")
        warning_count = sum(1 for item in review.review_items if item.type == "Warning")

        scorecard_values = review.scorecard.model_dump()
        logic_scores = [
            normalize_scorecard(scorecard_values["logic_traceability"]["score"]),
            normalize_scorecard(scorecard_values["generalization_score"]["score"]),
            normalize_scorecard(scorecard_values["control_flow_understanding"]["score"]),
            normalize_scorecard(scorecard_values["edge_case_awareness"]["score"]),
        ]
        efficiency_scores = [
            normalize_scorecard(scorecard_values["construct_appropriateness"]["score"]),
            normalize_scorecard(scorecard_values["generalization_score"]["score"]),
            profile.efficiency_awareness,
        ]
        progression_scores = [
            profile.concept_mastery,
            profile.concept_transfer,
            profile.learning_velocity,
            normalize_scorecard(scorecard_values["self_correction_path"]["score"]),
            normalize_scorecard(scorecard_values["debugging_readiness"]["score"]),
        ]

        foundation_risk = min(
            100.0,
            round(
                (1 - profile.concept_mastery) * 60
                + (1 - profile.debugging_independence) * 40
                + (1 - sum(logic_scores) / len(logic_scores)) * 50
                + error_count * 10,
                2,
            ),
        )
        efficiency_gap = min(
            100.0,
            round(
                (1 - sum(efficiency_scores) / len(efficiency_scores)) * 75
                + warning_count * 6,
                2,
            ),
        )
        progression_readiness = max(
            0.0,
            min(
                100.0,
                round(sum(progression_scores) / len(progression_scores) * 100, 2),
            ),
        )
        support_need = min(
            100.0,
            round(
                foundation_risk * 0.45
                + efficiency_gap * 0.2
                + (100 - progression_readiness) * 0.35,
                2,
            ),
        )

        framework = RecommendationScoringFramework(
            foundation_risk=foundation_risk,
            efficiency_gap=efficiency_gap,
            progression_readiness=progression_readiness,
            support_need=support_need,
            explanation=(
                "Framework combines stored review-agent output with student profile scoring. "
                "Foundation risk emphasizes logic failures and debugging weakness, efficiency gap highlights "
                "solution-quality concerns, progression readiness reflects mastery and transfer, and support need "
                "summarizes how much scaffolding the next exercise should provide."
            ),
        )

        new_state = dict(state)
        new_state["critical_errors"] = error_count
        new_state["framework"] = framework
        return cast(RecommendationState, new_state)

    def _graph_rag_retriever(self, state: RecommendationState) -> RecommendationState:
        all_candidates: list[dict[str, Any]] = []
        for path in ("REINFORCE", "IMPROVE", "NEXT_CONCEPT"):
            all_candidates.extend(
                self.knowledge_graph_repository.retrieve_candidates(
                    student_id=state["student_id"],
                    current_concept=state["current_concept"],
                    assigned_path=cast(AssignedPath, path),
                    mastered_concepts=state["mastered_concepts"],
                    attempted_exercise_ids=state["attempted_exercise_ids"],
                    limit=3,
                )
            )

        new_state = dict(state)
        new_state["retrieved_candidates"] = all_candidates
        return cast(RecommendationState, new_state)

    def _recommendation_reasoner(self, state: RecommendationState) -> RecommendationState:
        prompt = self._build_reasoner_prompt(state)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a recommendation reasoner for CS1 education. "
                            "Choose exactly one path from REINFORCE, IMPROVE, NEXT_CONCEPT. "
                            "Build a roadmap with multiple exercises. Use the stored review, review history, "
                            "scoring framework, student profile, and Neo4j graph candidates. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            model_text = response.choices[0].message.content
            parsed = safe_parse_json_response(model_text)
            assigned_path = cast(
                AssignedPath,
                parsed.get("assigned_path") or self._fallback_path(state),
            )
            target_concept = parsed.get("target_concept") or state["current_concept"]
            selected_exercise_ids = parsed.get("exercise_ids") or []
            reasoning = parsed.get("reasoning", "").strip() or self._fallback_reasoning(
                state, assigned_path
            )
        except Exception:
            assigned_path = self._fallback_path(state)
            target_concept = state["current_concept"]
            selected_exercise_ids = []
            reasoning = self._fallback_reasoning(state, assigned_path)

        selected_candidates = self._select_candidates(
            state["retrieved_candidates"],
            assigned_path,
            target_concept,
            selected_exercise_ids,
        )

        new_state = dict(state)
        new_state["assigned_path"] = assigned_path
        new_state["target_concept"] = selected_candidates[0]["target_concept"]
        new_state["selected_exercises"] = [
            candidate["exercise"] for candidate in selected_candidates
        ]
        new_state["reasoning"] = reasoning
        return cast(RecommendationState, new_state)

    def _directive_builder(self, state: RecommendationState) -> RecommendationState:
        exercises = state["selected_exercises"]
        if not exercises:
            raise ValueError("Directive builder requires selected exercises.")

        framework = state["framework"]
        new_state = dict(state)
        directives: list[str] = []
        for index, exercise in enumerate(exercises, start=1):
            if state["assigned_path"] == "REINFORCE":
                directives.append(
                    f"Step {index}: work on {exercise.title} to rebuild confidence in {state['target_concept']}. "
                    f"This step supports the student while foundation risk is {framework.foundation_risk:.1f}."
                )
            elif state["assigned_path"] == "NEXT_CONCEPT":
                directives.append(
                    f"Step {index}: use {exercise.title} to move deeper into {state['target_concept']}. "
                    f"This step extends the student's readiness score of {framework.progression_readiness:.1f}."
                )
            else:
                directives.append(
                    f"Step {index}: solve {exercise.title} to improve implementation quality in {state['target_concept']}. "
                    f"This step targets the efficiency gap score of {framework.efficiency_gap:.1f}."
                )
        new_state["roadmap_directives"] = directives
        return cast(RecommendationState, new_state)

    def _build_reasoner_prompt(self, state: RecommendationState) -> str:
        review = state["review"]
        if review is None:
            raise ValueError("Recommendation reasoner requires a stored review context.")

        candidates = [
            {
                "target_concept": item["target_concept"],
                "concept_name": item["concept_name"],
                "exercise_id": item["exercise"].exercise_id,
                "title": item["exercise"].title,
                "difficulty": item["exercise"].difficulty,
                "description": item["exercise"].description,
            }
            for item in state["retrieved_candidates"]
        ]
        return f"""
Student ID: {state['student_id']}
Current concept: {state['current_concept']}

Latest stored review summary:
{review.summary}

Latest stored review items:
{[item.model_dump() for item in review.review_items]}

Latest stored scorecard:
{review.scorecard.model_dump()}

Recent linked reviews for this student:
{[record.model_dump() for record in state['review_history']]}

Student profile scoring:
{state['student_profile'].model_dump()}

Recommendation scoring framework:
{state['framework'].model_dump()}

GraphRAG candidates from Neo4j:
{candidates}

Task:
1. Choose exactly one assigned_path from REINFORCE, IMPROVE, NEXT_CONCEPT.
2. Choose one target_concept.
3. Choose 2 or 3 exercise_ids from the provided candidates to form a learning roadmap.
4. Order them from simpler to more demanding.
5. Use the linked review history when deciding whether the student is improving, stuck, or ready to progress.
6. Give a concise reasoning paragraph.

Return JSON only:
{{
  "assigned_path": "REINFORCE",
  "target_concept": "Loops",
  "exercise_ids": ["loops_001", "loops_002", "loops_003"],
  "reasoning": "short grounded explanation"
}}
"""

    def _fallback_path(self, state: RecommendationState) -> AssignedPath:
        framework = state["framework"]
        if framework.foundation_risk >= 55 or state["critical_errors"] > 0:
            return "REINFORCE"
        if framework.progression_readiness >= 80 and framework.foundation_risk < 35:
            return "NEXT_CONCEPT"
        return "IMPROVE"

    def _fallback_reasoning(
        self, state: RecommendationState, assigned_path: AssignedPath
    ) -> str:
        framework = state["framework"]
        review_history_count = len(state["review_history"])
        if assigned_path == "REINFORCE":
            return (
                f"Assigned REINFORCE because foundation risk is {framework.foundation_risk:.1f} "
                f"with {state['critical_errors']} critical error(s). Review history count considered: {review_history_count}."
            )
        if assigned_path == "NEXT_CONCEPT":
            return (
                f"Assigned NEXT_CONCEPT because progression readiness is {framework.progression_readiness:.1f} "
                f"and foundation risk is controlled at {framework.foundation_risk:.1f}."
            )
        return (
            f"Assigned IMPROVE because efficiency gap is {framework.efficiency_gap:.1f} "
            f"while the student has enough foundation to stay on the current concept."
        )

    def _select_candidates(
        self,
        candidates: list[dict[str, Any]],
        assigned_path: AssignedPath,
        target_concept: str,
        selected_exercise_ids: list[str],
    ) -> list[dict[str, Any]]:
        filtered = [
            candidate
            for candidate in candidates
            if candidate["target_concept"] == target_concept
        ]
        chosen: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        if selected_exercise_ids:
            for exercise_id in selected_exercise_ids:
                for candidate in filtered:
                    if (
                        candidate["exercise"].exercise_id == exercise_id
                        and exercise_id not in seen_ids
                    ):
                        chosen.append(candidate)
                        seen_ids.add(exercise_id)
                        break
        if chosen:
            return chosen[:3]
        if filtered:
            return filtered[:3]

        path_candidates = []
        for candidate in candidates:
            if assigned_path == "NEXT_CONCEPT" and candidate["target_concept"] != target_concept:
                path_candidates.append(candidate)
            elif assigned_path != "NEXT_CONCEPT" and candidate["target_concept"] == target_concept:
                path_candidates.append(candidate)
        if path_candidates:
            return path_candidates[:3]
        if candidates:
            return candidates[:3]
        raise ValueError("Neo4j did not return any recommendation roadmap candidates.")

    def _build_step_focus(
        self, assigned_path: AssignedPath, target_concept: str, step: int
    ) -> str:
        if assigned_path == "REINFORCE":
            focuses = [
                f"Rebuild the basics of {target_concept}",
                f"Practice stable use of {target_concept}",
                f"Consolidate confidence in {target_concept}",
            ]
        elif assigned_path == "NEXT_CONCEPT":
            focuses = [
                f"Enter the next concept: {target_concept}",
                f"Apply {target_concept} in a larger task",
                f"Strengthen transfer within {target_concept}",
            ]
        else:
            focuses = [
                f"Improve implementation quality in {target_concept}",
                f"Reduce inefficiency in {target_concept}",
                f"Refine strategy for {target_concept}",
            ]
        index = min(step - 1, len(focuses) - 1)
        return focuses[index]
