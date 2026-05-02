import unittest
from unittest.mock import MagicMock, call
from unittest.mock import patch

from code_review_ai.config import FireworksStageConfig
from code_review_ai.api.recommendation_schema import (
    RecommendationRequest,
    RecommendationReviewRequest,
    RecommendationSubmissionRequest,
)
from code_review_ai.api.review_code_schema import (
    LineContext,
    ReviewItem,
    ScoreCard,
    ScoreCardItem,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.services.recommendation_service import RecommendationService


def _exercise(exercise_id: str, difficulty: str = "easy") -> ExerciseRecord:
    return ExerciseRecord(
        exercise_id=exercise_id,
        slug=exercise_id,
        title=f"Exercise {exercise_id}",
        description=f"Description for {exercise_id}",
        content=f"Content for {exercise_id}",
        difficulty=difficulty,
        concept_slugs=["loops"],
    )


def _candidate(
    exercise_id: str,
    *,
    recommended_weight: float,
    tests_weight: float,
    related_weight: float,
    progression_score: float,
    similarity_score: float,
    difficulty_gap: float,
    vector_similarity: float = 0.0,
    retrieval_sources: list[str] | None = None,
    root_connection_mode: str = "direct",
    root_connection_weight: float | None = None,
    root_hop_count: int = 1,
) -> dict:
    return {
        "target_concept": "loops",
        "concept_name": "Loops",
        "concept_description": "Loop practice",
        "recommended_weight": recommended_weight,
        "tests_weight": tests_weight,
        "related_weight": related_weight,
        "difficulty_gap": difficulty_gap,
        "progression_score": progression_score,
        "similarity_score": similarity_score,
        "root_connection_mode": root_connection_mode,
        "root_connection_weight": (
            related_weight if root_connection_weight is None else root_connection_weight
        ),
        "root_hop_count": root_hop_count,
        "vector_similarity": vector_similarity,
        "retrieval_sources": retrieval_sources or ["graph"],
        "exercise": _exercise(exercise_id),
    }


def _state() -> dict:
    review = RecommendationReviewRequest(
        review_id="review-1",
        summary="Needs stronger loop boundary handling.",
        detail="The student still misses exit conditions and repeats off-by-one mistakes.",
        review_items=[
            ReviewItem(
                line=LineContext(start=3, end=4),
                column=None,
                code_snippet="for i in range(n+1):",
                type="Error",
                issue="Off-by-one loop bound.",
                fix_suggestion="Use range(n) for zero-indexed iteration.",
            )
        ],
        scorecard=ScoreCard(
            problem_solving_creativity=ScoreCardItem(score=3, label="ok", explanation=""),
            logic_traceability=ScoreCardItem(score=2, label="weak", explanation=""),
            generalization_score=ScoreCardItem(score=3, label="ok", explanation=""),
            construct_appropriateness=ScoreCardItem(score=3, label="ok", explanation=""),
            self_correction_path=ScoreCardItem(score=2, label="weak", explanation=""),
            variable_understanding=ScoreCardItem(score=3, label="ok", explanation=""),
            control_flow_understanding=ScoreCardItem(score=2, label="weak", explanation=""),
            input_output_awareness=ScoreCardItem(score=3, label="ok", explanation=""),
            edge_case_awareness=ScoreCardItem(score=2, label="weak", explanation=""),
            debugging_readiness=ScoreCardItem(score=3, label="ok", explanation=""),
        ),
    )
    return {
        "student_id": "student-1",
        "exercise_id": "exercise-current",
        "exercise": _exercise("exercise-current"),
        "focus_concept_ids": ["loops"],
        "review": review,
        "submission": RecommendationSubmissionRequest(
            submission_id="submission-1",
            code="for i in range(n+1):\n    print(i)\n",
            testcases=[
                {"input": "1", "expect": "1", "output": "1"},
                {"input": "2", "expect": "2", "output": "2"},
                {"input": "3", "expect": "3", "output": "0"},
            ],
            created_at="2026-04-30T09:55:00Z",
        ),
        "attempted_exercise_ids": ["done-1", "done-2"],
        "retrieved_candidates": [],
        "rerank_query": {},
        "rerank_overview": "",
        "reranked_candidates": [],
        "roadmap_summary": "",
        "roadmap_steps": [],
    }


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self):
        self.neo4j_repository = MagicMock()
        self.exercise_vector_service = MagicMock()
        self.exercise_relation_scoring_service = MagicMock()
        self.exercise_relation_scoring_service.DEFAULT_RELATION_METADATA = {
            "weight": 0.7,
            "difficulty_gap": 0.0,
            "progression_score": 0.7,
            "similarity_score": 0.7,
        }
        self.exercise_relation_scoring_service.evaluate.return_value = (
            {},
            {},
            {},
        )
        self.service = RecommendationService(
            neo4j_repository=self.neo4j_repository,
            exercise_vector_service=self.exercise_vector_service,
            exercise_relation_scoring_service=self.exercise_relation_scoring_service,
            client=MagicMock(),
            fireworks_api_key="test-key",
            fireworks_base_url="https://api.fireworks.ai/inference/v1",
            rerank_context_builder_stage_config=FireworksStageConfig(
                model_name="fireworks/deepseek-v3p2",
                temperature=0.1,
                max_tokens=1200,
            ),
            reranker_stage_config=FireworksStageConfig(
                model_name="accounts/fireworks/models/qwen3-reranker-8b",
                temperature=0.0,
                max_tokens=0,
            ),
            roadmap_builder_stage_config=FireworksStageConfig(
                model_name="fireworks/deepseek-v3p2",
                temperature=0.2,
                max_tokens=1800,
            ),
        )

    def test_candidate_retriever_splits_graph_and_vector_limits_from_context(self):
        state = _state()
        self.exercise_vector_service.is_enabled = True
        self.exercise_vector_service.search_exercises.return_value = [
            MagicMock(
                exercise_id="exercise-vector",
                score=0.91,
                payload={
                    "exercise_id": "exercise-vector",
                    "slug": "exercise-vector",
                    "title": "Exercise exercise-vector",
                    "description": "Description for exercise-vector",
                    "difficulty": "medium",
                    "concept_slugs": ["loops"],
                },
            ),
        ]
        self.neo4j_repository.retrieve_candidates.return_value = [
            _candidate(
                "exercise-graph",
                recommended_weight=0.8,
                tests_weight=0.6,
                related_weight=0.5,
                progression_score=0.4,
                similarity_score=0.7,
                difficulty_gap=0.1,
            )
        ]
        self.exercise_relation_scoring_service.evaluate.return_value = (
            {},
            {},
            {
                "exercise-vector": {
                    "weight": 0.7,
                    "difficulty_gap": 0.2,
                    "progression_score": 0.5,
                    "similarity_score": 0.6,
                }
            },
        )

        new_state = self.service._candidate_retriever(state)

        self.assertEqual(len(new_state["retrieved_candidates"]), 2)
        vector_candidate = next(
            candidate
            for candidate in new_state["retrieved_candidates"]
            if candidate["exercise"].exercise_id == "exercise-vector"
        )
        self.assertEqual(vector_candidate["root_connection_mode"], "vector")
        self.assertEqual(vector_candidate["root_hop_count"], 0)
        self.assertEqual(vector_candidate["vector_similarity"], 0.91)
        self.exercise_vector_service.search_exercises.assert_called_once()
        self.neo4j_repository.retrieve_candidates.assert_called_once_with(
            current_exercise_id="exercise-current",
            target_concept_ids=["loops"],
            attempted_exercise_ids=["done-1", "done-2"],
            limit=20,
        )

    def test_candidate_retriever_filters_attempted_vector_hits_before_enrichment(self):
        state = _state()
        self.exercise_vector_service.is_enabled = True
        self.exercise_vector_service.search_exercises.return_value = [
            MagicMock(exercise_id="done-1", score=0.99),
            MagicMock(exercise_id="exercise-current", score=0.93),
            MagicMock(
                exercise_id="exercise-vector",
                score=0.91,
                payload={
                    "exercise_id": "exercise-vector",
                    "slug": "exercise-vector",
                    "title": "Exercise exercise-vector",
                    "description": "Description for exercise-vector",
                    "difficulty": "medium",
                    "concept_slugs": ["loops"],
                },
            ),
        ]
        self.neo4j_repository.retrieve_candidates.return_value = []

        self.service._candidate_retriever(state)

        self.neo4j_repository.retrieve_candidates.assert_called_once_with(
            current_exercise_id="exercise-current",
            target_concept_ids=["loops"],
            attempted_exercise_ids=["done-1", "done-2"],
            limit=20,
        )

    def test_candidate_retriever_raises_when_vector_loading_fails(self):
        state = _state()
        self.exercise_vector_service.is_enabled = True
        self.exercise_vector_service.search_exercises.side_effect = RuntimeError(
            "vector db unavailable"
        )
        self.neo4j_repository.retrieve_candidates.return_value = []

        with self.assertRaises(RuntimeError):
            self.service._candidate_retriever(state)

    def test_candidate_retriever_recalculates_non_direct_graph_candidates(self):
        state = _state()
        self.exercise_vector_service.is_enabled = False
        self.neo4j_repository.retrieve_candidates.return_value = [
            _candidate(
                "exercise-direct",
                recommended_weight=0.8,
                tests_weight=0.7,
                related_weight=1.0,
                progression_score=0.8,
                similarity_score=0.75,
                difficulty_gap=0.1,
                root_connection_mode="direct",
                root_connection_weight=1.0,
                root_hop_count=1,
            ),
            _candidate(
                "exercise-non-direct",
                recommended_weight=0.6,
                tests_weight=0.65,
                related_weight=0.31,
                progression_score=0.0,
                similarity_score=0.0,
                difficulty_gap=0.0,
                root_connection_mode="non-direct",
                root_connection_weight=0.31,
                root_hop_count=2,
            ),
        ]
        self.exercise_relation_scoring_service.evaluate.return_value = (
            {},
            {},
            {
                "exercise-non-direct": {
                    "weight": 0.7,
                    "difficulty_gap": 0.2,
                    "progression_score": 0.5,
                    "similarity_score": 0.6,
                }
            },
        )

        new_state = self.service._candidate_retriever(state)

        non_direct_candidate = next(
            candidate
            for candidate in new_state["retrieved_candidates"]
            if candidate["exercise"].exercise_id == "exercise-non-direct"
        )
        self.assertEqual(non_direct_candidate["root_connection_mode"], "non-direct")
        self.assertEqual(non_direct_candidate["root_connection_weight"], 0.31)
        self.assertEqual(non_direct_candidate["root_hop_count"], 2)
        self.assertEqual(non_direct_candidate["related_weight"], 0.7)
        self.assertEqual(non_direct_candidate["difficulty_gap"], 0.2)
        self.assertEqual(non_direct_candidate["progression_score"], 0.5)
        self.assertEqual(non_direct_candidate["similarity_score"], 0.6)

    def test_rerank_context_builder_uses_request_context(self):
        state = _state()
        state["retrieved_candidates"] = [
            _candidate(
                "exercise-1",
                recommended_weight=0.7,
                tests_weight=0.6,
                related_weight=0.5,
                progression_score=0.5,
                similarity_score=0.6,
                difficulty_gap=0.1,
            )
        ]

        new_state = self.service._rerank_context_builder(state)

        self.assertEqual(new_state["rerank_query"]["focus_concept_ids"], ["loops"])
        self.assertEqual(
            new_state["rerank_query"]["goal_query"],
            "Rank the best next exercises for the student's current concept.",
        )
        self.assertEqual(
            new_state["rerank_query"]["current_exercise"]["title"],
            "Exercise exercise-current",
        )
        self.assertNotIn("query_facets", new_state["rerank_query"])
        self.assertIn(
            "should stay focused on concepts loops",
            new_state["rerank_overview"],
        )

    def test_rerank_context_builder_uses_current_request_review_and_submission(self):
        state = _state()

        new_state = self.service._rerank_context_builder(state)

        self.assertEqual(
            new_state["rerank_query"]["latest_review"]["summary"],
            "Needs stronger loop boundary handling.",
        )
        self.assertIn("latest review highlights", new_state["rerank_overview"])

    def test_candidate_ranker_uses_context_and_reranks_all_candidates(self):
        state = _state()
        state["retrieved_candidates"] = [
            _candidate(
                "exercise-1",
                recommended_weight=0.75,
                tests_weight=0.55,
                related_weight=0.50,
                progression_score=0.70,
                similarity_score=0.65,
                difficulty_gap=0.20,
                vector_similarity=0.20,
                retrieval_sources=["graph"],
            ),
            _candidate(
                "exercise-2",
                recommended_weight=0.88,
                tests_weight=0.80,
                related_weight=0.60,
                progression_score=0.86,
                similarity_score=0.58,
                difficulty_gap=0.35,
                vector_similarity=0.72,
                retrieval_sources=["graph", "vector"],
            )
            | {"exercise": _exercise("exercise-2", difficulty="medium")},
            _candidate(
                "exercise-3",
                recommended_weight=0.69,
                tests_weight=0.61,
                related_weight=0.44,
                progression_score=0.74,
                similarity_score=0.62,
                difficulty_gap=0.28,
                vector_similarity=0.45,
                retrieval_sources=["vector"],
                root_connection_mode="indirect",
                root_connection_weight=0.44,
                root_hop_count=2,
            )
            | {"exercise": _exercise("exercise-3", difficulty="hard")},
            _candidate(
                "exercise-4",
                recommended_weight=0.42,
                tests_weight=0.35,
                related_weight=0.30,
                progression_score=0.40,
                similarity_score=0.55,
                difficulty_gap=0.15,
                vector_similarity=0.10,
                retrieval_sources=["graph"],
                root_connection_mode="fallback",
                root_connection_weight=0.0,
                root_hop_count=0,
            )
            | {"exercise": _exercise("exercise-4", difficulty="medium")},
        ]

        new_state = self.service._candidate_ranker(state)

        self.assertEqual(len(new_state["reranked_candidates"]), 4)
        self.assertEqual(
            {
                candidate["exercise"].difficulty
                for candidate in new_state["reranked_candidates"]
            },
            {"easy", "medium", "hard"},
        )
        self.assertEqual(
            new_state["reranked_candidates"][0]["exercise"].exercise_id,
            "exercise-2",
        )
        self.assertEqual(
            {
                candidate["exercise"].exercise_id
                for candidate in new_state["reranked_candidates"]
            },
            {"exercise-1", "exercise-2", "exercise-3", "exercise-4"},
        )

    def test_generate_recommendation_builds_multi_exercise_roadmap(self):
        request_state = _state()
        self.neo4j_repository.get_concept_ids_by_exercise.return_value = {
            "exercise-easy": ["loops"],
            "exercise-medium": ["loops", "arrays"],
            "exercise-hard": ["loops"],
        }
        self.service.workflow = MagicMock()
        self.service.workflow.invoke.return_value = {
            **request_state,
            "reranked_candidates": [
                _candidate(
                    "exercise-easy",
                    recommended_weight=0.82,
                    tests_weight=0.70,
                    related_weight=0.66,
                    progression_score=0.61,
                    similarity_score=0.64,
                    difficulty_gap=0.10,
                ),
                _candidate(
                    "exercise-medium",
                    recommended_weight=0.78,
                    tests_weight=0.68,
                    related_weight=0.55,
                    progression_score=0.70,
                    similarity_score=0.66,
                    difficulty_gap=0.20,
                )
                | {"exercise": _exercise("exercise-medium", difficulty="medium")},
                _candidate(
                    "exercise-hard",
                    recommended_weight=0.66,
                    tests_weight=0.60,
                    related_weight=0.40,
                    progression_score=0.52,
                    similarity_score=0.58,
                    difficulty_gap=0.25,
                    root_connection_mode="indirect",
                    root_connection_weight=0.40,
                    root_hop_count=2,
                )
                | {"exercise": _exercise("exercise-hard", difficulty="hard")},
            ],
            "roadmap_summary": "This roadmap strengthens loop control first, then expands to broader follow-up practice.",
            "roadmap_steps": [
                {
                    "step": 1,
                    "summary": "Start with close loop practice to reduce repeated boundary mistakes.",
                    "target_concepts": ["loops"],
                    "exercises": [
                        {
                            "exercise_id": "exercise-easy",
                            "priority": 1,
                            "reason": "A simpler reinforcement step for the same loop pattern.",
                        },
                        {
                            "exercise_id": "exercise-medium",
                            "priority": 2,
                            "reason": "A slightly broader follow-up once the core mistake is steadier.",
                        },
                    ],
                },
                {
                    "step": 2,
                    "summary": "Finish with a harder exercise that stretches edge-case control.",
                    "target_concepts": ["loops"],
                    "exercises": [
                        {
                            "exercise_id": "exercise-hard",
                            "priority": 1,
                            "reason": "A stretch problem for stronger loop control.",
                        }
                    ],
                },
            ],
        }

        response = self.service.generate_recommendation(
            RecommendationRequest(
                student_id="student-1",
                exercise=request_state["exercise"],
                review=request_state["review"],
                submission=request_state["submission"],
                focus_concept_ids=["loops"],
                attempted_exercise_ids=["done-1", "done-2"],
            )
        )

        self.assertEqual(response.focus_concept_ids, ["loops"])
        self.assertIn("strengthens loop control", response.summary)
        self.assertEqual(
            [item.exercise.exercise_id for item in response.roadmap[0].exercises],
            ["exercise-easy", "exercise-medium"],
        )
        self.assertEqual(
            response.roadmap[0].exercises[0].priority,
            1,
        )
        self.assertEqual(
            response.roadmap[0].exercises[0].reason,
            "A simpler reinforcement step for the same loop pattern.",
        )
        self.assertEqual(response.roadmap[1].exercises[0].exercise.exercise_id, "exercise-hard")

    @patch("code_review_ai.services.recommendation_service.rerank_documents_with_retry")
    def test_rerank_stage_uses_fireworks_reranker(self, rerank_documents):
        state = _state()
        state["retrieved_candidates"] = [
            _candidate(
                "exercise-1",
                recommended_weight=0.80,
                tests_weight=0.75,
                related_weight=0.65,
                progression_score=0.70,
                similarity_score=0.72,
                difficulty_gap=0.10,
                vector_similarity=0.20,
                retrieval_sources=["graph"],
            ),
            _candidate(
                "exercise-2",
                recommended_weight=0.60,
                tests_weight=0.55,
                related_weight=0.40,
                progression_score=0.52,
                similarity_score=0.50,
                difficulty_gap=0.18,
                vector_similarity=0.88,
                retrieval_sources=["vector"],
                root_connection_mode="fallback",
                root_connection_weight=0.0,
                root_hop_count=0,
            ),
        ]
        state["rerank_query"] = self.service._build_rerank_query(state)
        state["rerank_overview"] = "Loop boundary issues still need reinforcement."
        rerank_documents.return_value = {
            "data": [
                {"index": 1, "relevance_score": 0.98},
                {"index": 0, "relevance_score": 0.40},
            ]
        }

        reranked = self.service._rerank_candidates(state)

        self.assertEqual(reranked[0]["exercise"].exercise_id, "exercise-2")
        self.assertEqual(reranked[0]["rerank_score"], 0.98)
        rerank_documents.assert_called_once()
        self.assertIn('"focus_concept_ids":["loops"]', rerank_documents.call_args.kwargs["query"])


if __name__ == "__main__":
    unittest.main()
