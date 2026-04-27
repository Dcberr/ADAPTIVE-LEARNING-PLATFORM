import unittest
from unittest.mock import MagicMock

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord
from code_review_ai.repositories.knowledge_graph_repository import (
    KnowledgeGraphRepository,
)


class KnowledgeGraphRepositoryExerciseBatchTests(unittest.TestCase):
    def test_upsert_exercises_uses_single_unwind_query(self):
        session = MagicMock()
        session.__enter__.return_value = session
        session.__exit__.return_value = None
        driver = MagicMock()
        driver.session.return_value = session

        repository = KnowledgeGraphRepository(driver=driver)
        exercises = [
            ExerciseRecord(
                exercise_id="exercise-1",
                slug="two-sum",
                title="Two Sum",
                description="Add two numbers",
                content="Read and print the sum",
                difficulty="easy",
                tags=["math"],
            ),
            ExerciseRecord(
                exercise_id="exercise-2",
                slug="three-sum",
                title="Three Sum",
                description="Add three numbers",
                content="Read and print the total",
                difficulty="easy",
                tags=["math", "loops"],
            ),
        ]

        result = repository.upsert_exercises(exercises)

        self.assertEqual(result, exercises)
        driver.session.assert_called_once()
        session.run.assert_called_once()
        query = session.run.call_args.args[0]
        params = session.run.call_args.kwargs
        self.assertIn("UNWIND $rows AS row", query)
        self.assertEqual(
            params["rows"],
            [
                {
                    "exercise_id": "exercise-1",
                    "slug": "two-sum",
                    "title": "Two Sum",
                    "description": "Add two numbers",
                    "content": "Read and print the sum",
                    "difficulty": "easy",
                    "tags": ["math"],
                },
                {
                    "exercise_id": "exercise-2",
                    "slug": "three-sum",
                    "title": "Three Sum",
                    "description": "Add three numbers",
                    "content": "Read and print the total",
                    "difficulty": "easy",
                    "tags": ["math", "loops"],
                },
            ],
        )

    def test_upsert_exercise_delegates_to_batch_upsert(self):
        repository = KnowledgeGraphRepository(driver=MagicMock())
        exercise = ExerciseRecord(
            exercise_id="exercise-1",
            slug="two-sum",
            title="Two Sum",
            description="Add two numbers",
            content="Read and print the sum",
            difficulty="easy",
            tags=["math"],
        )
        repository.upsert_exercises = MagicMock(return_value=[exercise])

        result = repository.upsert_exercise(exercise)

        self.assertEqual(result, exercise)
        repository.upsert_exercises.assert_called_once_with([exercise])

    def test_replace_exercise_concepts_batch_uses_unwind_queries(self):
        session = MagicMock()
        session.__enter__.return_value = session
        session.__exit__.return_value = None
        driver = MagicMock()
        driver.session.return_value = session

        repository = KnowledgeGraphRepository(driver=driver)
        concept = ConceptRecord(
            concept_id="concept-1",
            slug="arrays",
            name="Arrays",
            description="Array basics",
            difficulty=1,
        )

        repository.replace_exercise_concepts_batch(
            [
                {
                    "exercise_id": "exercise-1",
                    "concepts": [
                        (
                            concept,
                            1.0,
                            [{"path": "REINFORCE", "weight": 0.7}],
                        )
                    ],
                }
            ]
        )

        self.assertEqual(session.run.call_count, 4)
        delete_tests_query = session.run.call_args_list[0].args[0]
        delete_paths_query = session.run.call_args_list[1].args[0]
        create_tests_query = session.run.call_args_list[2].args[0]
        create_paths_query = session.run.call_args_list[3].args[0]
        self.assertIn("WHERE e.exercise_id IN $exercise_ids", delete_tests_query)
        self.assertIn("WHERE e.exercise_id IN $exercise_ids", delete_paths_query)
        self.assertIn("UNWIND $rows AS row", create_tests_query)
        self.assertIn("UNWIND $rows AS row", create_paths_query)

    def test_replace_exercise_related_exercises_batch_uses_unwind_query(self):
        session = MagicMock()
        session.__enter__.return_value = session
        session.__exit__.return_value = None
        driver = MagicMock()
        driver.session.return_value = session

        repository = KnowledgeGraphRepository(driver=driver)
        related_exercise = ExerciseRecord(
            exercise_id="exercise-2",
            slug="sum-three",
            title="Sum Three",
            description="Add three numbers",
            content="Read and add three values",
            difficulty="easy",
            tags=["math"],
        )

        repository.replace_exercise_related_exercises_batch(
            [
                {
                    "exercise_id": "exercise-1",
                    "related_exercises": [
                        (
                            related_exercise,
                            {
                                "weight": 0.7,
                                "relation_type": "SIMILAR_PRACTICE",
                                "target_concept_id": "concept-1",
                                "shared_concept_ids": ["concept-1"],
                                "difficulty_gap": 0.0,
                                "progression_score": 0.7,
                                "similarity_score": 0.8,
                            },
                        )
                    ],
                }
            ]
        )

        self.assertEqual(session.run.call_count, 2)
        delete_query = session.run.call_args_list[0].args[0]
        create_query = session.run.call_args_list[1].args[0]
        self.assertIn("WHERE e.exercise_id IN $exercise_ids", delete_query)
        self.assertIn("UNWIND $rows AS row", create_query)


if __name__ == "__main__":
    unittest.main()
