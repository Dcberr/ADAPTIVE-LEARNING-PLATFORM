import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from code_review_ai.api.knowledge_graph_route import (
    batch_patch_exercise_relations,
    patch_exercise_relations,
)
from code_review_ai.api.knowledge_graph_schema import (
    BatchPatchExerciseRelationsRequest,
    PatchExerciseRelationsRequest,
)
from code_review_ai.models.exercise_record import ExerciseRecord


class KnowledgeGraphRouteExerciseRelationTests(unittest.IsolatedAsyncioTestCase):
    async def test_batch_patch_exercise_relations_adds_concept_slugs_and_replaces_related_exercises(self):
        repository = MagicMock()
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="three-sum",
            title="Three Sum",
            description="Add three numbers",
            content="Read and print the total",
            difficulty="medium",
            concept_slugs=["arrays", "loops"],
        )
        repository.get_exercises_by_ids.return_value = {"exercise-1": main_exercise}
        repository.get_exercises_by_slugs.return_value = {
            "three-sum": [related_exercise]
        }
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [
                SimpleNamespace(concept_id="concept-arrays", slug="arrays")
            ],
            "math": [SimpleNamespace(concept_id="concept-math", slug="math")],
        }

        scoring_service = MagicMock()
        scoring_service.evaluate.return_value = (
            {
                "concept-arrays": 0.7,
                "concept-math": 1.0,
            },
            {
                "concept-arrays": [{"path": "IMPROVE", "weight": 0.7}],
                "concept-math": [{"path": "REINFORCE", "weight": 1.0}],
            },
            {
                "exercise-2": {
                    "weight": 0.7,
                    "relation_type": "NEXT_STEP",
                    "difficulty_gap": 1.0,
                    "progression_score": 0.7,
                    "similarity_score": 0.7,
                }
            },
        )

        response = await batch_patch_exercise_relations(
            request=BatchPatchExerciseRelationsRequest(
                exercises=[
                    {
                        "exercise_id": "exercise-1",
                        "concept_slugs": ["math"],
                        "related_exercise_slugs": ["three-sum"],
                    }
                ]
            ),
            repository=repository,
            exercise_relation_scoring_service=scoring_service,
        )

        self.assertEqual(response.exercises[0].concept_slugs, ["arrays", "math"])
        repository.upsert_exercises.assert_called_once()
        repository.replace_exercise_concepts_batch.assert_called_once_with(
            [
                {
                    "exercise_id": "exercise-1",
                    "concepts": [
                        (
                            repository.get_concepts_by_slugs.return_value["arrays"][0],
                            0.7,
                            [{"path": "IMPROVE", "weight": 0.7}],
                        ),
                        (
                            repository.get_concepts_by_slugs.return_value["math"][0],
                            1.0,
                            [{"path": "REINFORCE", "weight": 1.0}],
                        ),
                    ],
                }
            ]
        )
        repository.replace_exercise_related_exercises_batch.assert_called_once_with(
            [
                {
                    "exercise_id": "exercise-1",
                    "related_exercises": [
                        (
                            related_exercise,
                            {
                                "weight": 0.7,
                                "relation_type": "NEXT_STEP",
                                "difficulty_gap": 1.0,
                                "progression_score": 0.7,
                                "similarity_score": 0.7,
                            },
                        )
                    ],
                }
            ]
        )
        scoring_service.evaluate.assert_called_once_with(
            main_exercise=response.exercises[0],
            concepts=[
                repository.get_concepts_by_slugs.return_value["arrays"][0],
                repository.get_concepts_by_slugs.return_value["math"][0],
            ],
            related_exercises=[related_exercise],
            main_concept_slugs=["arrays", "math"],
            related_concept_slugs_by_exercise={"exercise-2": ["arrays", "loops"]},
        )

    async def test_batch_patch_exercise_relations_supports_related_exercise_slugs(self):
        repository = MagicMock()
        main_exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="similar-two-sum",
            title="Similar Two Sum",
            description="Add two numbers in a similar way",
            content="Read and print the sum again",
            difficulty="easy",
            concept_slugs=["arrays"],
        )
        repository.get_exercises_by_ids.side_effect = [
            {"exercise-1": main_exercise},
            {},
        ]
        repository.get_exercises_by_slugs.return_value = {
            "similar-two-sum": [related_exercise]
        }
        repository.get_concepts_by_slugs.return_value = {
            "arrays": [SimpleNamespace(concept_id="concept-arrays", slug="arrays")]
        }

        scoring_service = MagicMock()
        scoring_service.evaluate.return_value = (
            {},
            {},
            {
                "exercise-2": {
                    "weight": 1.0,
                    "relation_type": "SIMILAR_PRACTICE",
                    "difficulty_gap": 0.0,
                    "progression_score": 0.7,
                    "similarity_score": 1.0,
                }
            },
        )

        response = await batch_patch_exercise_relations(
            request=BatchPatchExerciseRelationsRequest(
                exercises=[
                    {
                        "exercise_id": "exercise-1",
                        "related_exercise_slugs": ["similar-two-sum"],
                    }
                ]
            ),
            repository=repository,
            exercise_relation_scoring_service=scoring_service,
        )

        self.assertEqual(response.exercises, [main_exercise])
        repository.upsert_exercises.assert_not_called()
        repository.replace_exercise_concepts_batch.assert_not_called()
        repository.replace_exercise_related_exercises_batch.assert_called_once_with(
            [
                {
                    "exercise_id": "exercise-1",
                    "related_exercises": [
                        (
                            related_exercise,
                            {
                                "weight": 1.0,
                                "relation_type": "SIMILAR_PRACTICE",
                                "difficulty_gap": 0.0,
                                "progression_score": 0.7,
                                "similarity_score": 1.0,
                            },
                        )
                    ],
                }
            ]
        )

    async def test_patch_exercise_relations_forwards_concept_and_related_exercise_slugs(self):
        repository = MagicMock()
        scoring_service = MagicMock()
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            concept_slugs=["arrays"],
        )

        with patch(
            "code_review_ai.api.knowledge_graph_route.batch_patch_exercise_relations"
        ) as batch_patch:
            batch_patch.return_value = SimpleNamespace(exercises=[exercise])
            response = await patch_exercise_relations(
                exercise_id="exercise-1",
                request=PatchExerciseRelationsRequest(
                    concept_slugs=["math"],
                    related_exercise_slugs=["similar-two-sum"],
                ),
                repository=repository,
                exercise_relation_scoring_service=scoring_service,
            )

        self.assertEqual(response.exercise, exercise)
        forwarded_request = batch_patch.call_args.kwargs["request"]
        self.assertEqual(
            forwarded_request.model_dump(),
            {
                "exercises": [
                    {
                        "exercise_id": "exercise-1",
                        "concept_slugs": ["math"],
                        "related_exercise_slugs": ["similar-two-sum"],
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
