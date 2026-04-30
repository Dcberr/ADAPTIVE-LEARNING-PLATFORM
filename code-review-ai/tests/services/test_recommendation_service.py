import unittest
from unittest.mock import MagicMock, call
from unittest.mock import patch

from code_review_ai.config import FireworksStageConfig
from code_review_ai.api.review_code_schema import (
    LineContext,
    ReviewItem,
    ReviewResponse,
    ScoreCard,
    ScoreCardItem,
)
from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.review_record import ReviewRecord
from code_review_ai.models.submission_record import SubmissionRecord
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
    path_relation_types: list[str] | None = None,
) -> dict:
    return {
        "target_concept": "loops",
        "concept_name": "Loops",
        "concept_description": "Loop practice",
        "recommended_weight": recommended_weight,
        "tests_weight": tests_weight,
        "related_weight": related_weight,
        "relation_type": "REINFORCE",
        "difficulty_gap": difficulty_gap,
        "progression_score": progression_score,
        "similarity_score": similarity_score,
        "root_connection_mode": root_connection_mode,
        "root_connection_weight": (
            related_weight if root_connection_weight is None else root_connection_weight
        ),
        "root_hop_count": root_hop_count,
        "path_relation_types": path_relation_types or ["REINFORCE"],
        "vector_similarity": vector_similarity,
        "retrieval_sources": retrieval_sources or ["graph"],
        "exercise": _exercise(exercise_id),
    }


def _state() -> dict:
    review = ReviewResponse(
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
        "base_context": {
            "exercise": _exercise("exercise-current"),
            "tested_concepts": [{"concept_id": "loops"}],
            "recommended_concepts": [{"concept_id": "iteration", "weight": 0.8}],
        },
        "focus_concept_id": "loops",
        "focus_concept_weight": 0.7,
        "review": review,
        "review_record": ReviewRecord(
            review_id="review-1",
            student_id="student-1",
            exercise_id="exercise-current",
            submission_id="submission-1",
            current_concept="loops",
            created_at="2026-04-30T10:00:00Z",
            summary=review.summary,
            detail=review.detail,
        ),
        "review_history": [],
        "submission_record": SubmissionRecord(
            submission_id="submission-1",
            student_id="student-1",
            exercise_id="exercise-current",
            code="for i in range(n+1):\n    print(i)\n",
            testcase_outputs=[
                {"expect": "1", "output": "1"},
                {"expect": "2", "output": "2"},
                {"expect": "3", "output": "0"},
            ],
            created_at="2026-04-30T09:55:00Z",
        ),
        "submission_history": [],
        "attempted_exercise_ids": ["done-1", "done-2"],
        "retrieved_candidates": [],
        "rerank_query": {},
        "rerank_overview": "",
        "reranked_candidates": [],
    }


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self):
        self.neo4j_repository = MagicMock()
        self.exercise_vector_service = MagicMock()
        self.service = RecommendationService(
            neo4j_repository=self.neo4j_repository,
            exercise_vector_service=self.exercise_vector_service,
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
        )

    def test_candidate_retriever_splits_graph_and_vector_limits_from_context(self):
        state = _state()
        self.exercise_vector_service.is_enabled = True
        self.exercise_vector_service.search_exercises.return_value = [
            MagicMock(exercise_id="exercise-vector", score=0.91),
        ]
        self.neo4j_repository.retrieve_candidates.side_effect = [
            [_candidate("exercise-graph", recommended_weight=0.8, tests_weight=0.6, related_weight=0.5, progression_score=0.4, similarity_score=0.7, difficulty_gap=0.1)],
            [_candidate("exercise-vector", recommended_weight=0.6, tests_weight=0.7, related_weight=0.34, progression_score=0.5, similarity_score=0.6, difficulty_gap=0.2, root_connection_mode="indirect", root_connection_weight=0.34, root_hop_count=2, path_relation_types=["REINFORCE", "NEXT_STEP"])],
        ]

        new_state = self.service._candidate_retriever(state)

        self.assertEqual(len(new_state["retrieved_candidates"]), 2)
        vector_candidate = next(
            candidate
            for candidate in new_state["retrieved_candidates"]
            if candidate["exercise"].exercise_id == "exercise-vector"
        )
        self.assertEqual(vector_candidate["root_connection_mode"], "indirect")
        self.assertEqual(vector_candidate["root_hop_count"], 2)
        self.assertEqual(
            vector_candidate["path_relation_types"], ["REINFORCE", "NEXT_STEP"]
        )
        self.exercise_vector_service.search_exercises.assert_called_once()
        self.neo4j_repository.retrieve_candidates.assert_has_calls(
            [
                call(
                    student_id="student-1",
                    current_exercise_id="exercise-current",
                    current_concept="loops",
                    target_concept="loops",
                    attempted_exercise_ids=["done-1", "done-2"],
                    limit=6,
                    allow_indirect_paths=False,
                ),
                call(
                    student_id="student-1",
                    current_exercise_id="exercise-current",
                    current_concept="loops",
                    target_concept="loops",
                    attempted_exercise_ids=["done-1", "done-2"],
                    candidate_exercise_ids=["exercise-vector"],
                    limit=6,
                    allow_indirect_paths=True,
                ),
            ]
        )

    def test_candidate_retriever_filters_attempted_vector_hits_before_enrichment(self):
        state = _state()
        self.exercise_vector_service.is_enabled = True
        self.exercise_vector_service.search_exercises.return_value = [
            MagicMock(exercise_id="done-1", score=0.99),
            MagicMock(exercise_id="exercise-current", score=0.93),
            MagicMock(exercise_id="exercise-vector", score=0.91),
        ]
        self.neo4j_repository.retrieve_candidates.side_effect = [
            [],
            [
                _candidate(
                    "exercise-vector",
                    recommended_weight=0.6,
                    tests_weight=0.7,
                    related_weight=0.34,
                    progression_score=0.5,
                    similarity_score=0.6,
                    difficulty_gap=0.2,
                    root_connection_mode="indirect",
                    root_connection_weight=0.34,
                    root_hop_count=2,
                    path_relation_types=["REINFORCE", "NEXT_STEP"],
                )
            ],
        ]

        self.service._candidate_retriever(state)

        self.neo4j_repository.retrieve_candidates.assert_has_calls(
            [
                call(
                    student_id="student-1",
                    current_exercise_id="exercise-current",
                    current_concept="loops",
                    target_concept="loops",
                    attempted_exercise_ids=["done-1", "done-2"],
                    limit=6,
                    allow_indirect_paths=False,
                ),
                call(
                    student_id="student-1",
                    current_exercise_id="exercise-current",
                    current_concept="loops",
                    target_concept="loops",
                    attempted_exercise_ids=["done-1", "done-2"],
                    candidate_exercise_ids=["exercise-vector"],
                    limit=6,
                    allow_indirect_paths=True,
                ),
            ]
        )

    @patch("code_review_ai.services.recommendation_service.create_chat_completion_with_retry")
    def test_rerank_context_builder_uses_base_context(self, create_completion):
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
        create_completion.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"goal_query":"Rank exercises that reinforce loop control.","need_review_history":false,"review_history_limit":0,"need_submission_history":false,"submission_history_limit":0}'
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"goal_query":"Prioritize next exercises that reinforce loop control.","student_overview":"The student is still shaky on loop boundaries and needs nearby practice.","query_facets":["loop boundaries","nearby practice"]}'
                        )
                    )
                ]
            ),
        ]

        new_state = self.service._rerank_context_builder(state)

        self.assertEqual(new_state["rerank_query"]["focus_concept_id"], "loops")
        self.assertEqual(
            new_state["rerank_query"]["goal_query"],
            "Prioritize next exercises that reinforce loop control.",
        )
        self.assertEqual(
            new_state["rerank_query"]["current_exercise"]["title"],
            "Exercise exercise-current",
        )
        self.assertEqual(
            new_state["review_history"],
            [],
        )
        self.assertEqual(
            new_state["submission_history"],
            [],
        )
        self.assertEqual(
            new_state["rerank_query"]["query_facets"],
            ["loop boundaries", "nearby practice"],
        )
        self.assertEqual(
            new_state["rerank_overview"],
            "The student is still shaky on loop boundaries and needs nearby practice.",
        )

    @patch("code_review_ai.services.recommendation_service.create_chat_completion_with_retry")
    def test_rerank_context_builder_can_expand_review_and_submission_history(
        self, create_completion
    ):
        state = _state()
        review_history = [
            ReviewRecord(
                review_id="review-0",
                student_id="student-1",
                exercise_id="exercise-prev",
                submission_id="submission-0",
                current_concept="loops",
                created_at="2026-04-29T10:00:00Z",
                summary="Still missing loop termination.",
                detail="The student kept the off-by-one bug.",
            )
        ]
        submission_history = [
            SubmissionRecord(
                submission_id="submission-0",
                student_id="student-1",
                exercise_id="exercise-prev",
                code="while i <= n:\n    print(i)\n",
                testcase_outputs=[
                    {"expect": "1", "output": "1"},
                    {"expect": "2", "output": "0"},
                    {"expect": "3", "output": "0"},
                ],
                created_at="2026-04-29T09:55:00Z",
            )
        ]
        self.neo4j_repository.fetch_review_trend_context.return_value = {
            "review_history": review_history,
        }
        self.neo4j_repository.fetch_submission_history_context.return_value = {
            "submission_history": submission_history,
        }
        create_completion.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"goal_query":"Find the next exercise for loop control improvement.","need_review_history":true,"review_history_limit":1,"need_submission_history":true,"submission_history_limit":1}'
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content='{"goal_query":"Find the next exercise for loop control improvement.","student_overview":"The student repeats loop termination mistakes across recent attempts, so the next exercise should stay close to the current concept.","query_facets":["loop termination","same-concept reinforcement"]}'
                        )
                    )
                ]
            ),
        ]

        new_state = self.service._rerank_context_builder(state)

        self.neo4j_repository.fetch_review_trend_context.assert_called_once_with(
            review_id="review-1",
            student_id="student-1",
            history_limit=1,
        )
        self.neo4j_repository.fetch_submission_history_context.assert_called_once_with(
            submission_id="submission-1",
            history_limit=1,
        )
        self.assertEqual(new_state["review_history"], review_history)
        self.assertEqual(new_state["submission_history"], submission_history)
        self.assertEqual(new_state["rerank_query"]["query_facets"], ["loop termination", "same-concept reinforcement"])
        self.assertIn("repeats loop termination mistakes", new_state["rerank_overview"])

    def test_summarize_submission_history_compares_previous_with_current(self):
        state = _state()

        summary = self.service._summarize_submission_history(
            current_submission=state["submission_record"],
            submission_history=[
                SubmissionRecord(
                    submission_id="submission-0",
                    student_id="student-1",
                    exercise_id="exercise-current",
                    code="while i <= n:\n    print(i)\n",
                    testcase_outputs=[
                        {"expect": "1", "output": "1"},
                        {"expect": "2", "output": "0"},
                        {"expect": "3", "output": "0"},
                    ],
                    created_at="2026-04-29T09:55:00Z",
                )
            ],
        )

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["submission_id"], "submission-0")
        self.assertEqual(summary[0]["comparison_to_current"]["previous_pass_count"], 1)
        self.assertEqual(summary[0]["comparison_to_current"]["current_pass_count"], 2)
        self.assertEqual(summary[0]["comparison_to_current"]["pass_count_delta"], 1)
        self.assertAlmostEqual(
            summary[0]["comparison_to_current"]["improvement_ratio"],
            0.4166666667,
            places=6,
        )

    def test_candidate_ranker_uses_context_and_selects_top_three(self):
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
            ),
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
                path_relation_types=["REINFORCE", "NEXT_STEP"],
            ),
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
                path_relation_types=[],
            ),
        ]

        new_state = self.service._candidate_ranker(state)

        self.assertEqual(len(new_state["reranked_candidates"]), 4)
        self.assertEqual(
            [candidate["exercise"].exercise_id for candidate in new_state["reranked_candidates"][:3]],
            ["exercise-2", "exercise-3", "exercise-1"],
        )

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
                path_relation_types=[],
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
        self.assertIn('"focus_concept_id":"loops"', rerank_documents.call_args.kwargs["query"])


if __name__ == "__main__":
    unittest.main()
