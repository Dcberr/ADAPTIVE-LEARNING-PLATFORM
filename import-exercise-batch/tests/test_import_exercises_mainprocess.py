from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType

from import_exercise_batch.model import LeetCodeProblem


def _load_import_exercises_mainprocess_class() -> type:
    api_module = ModuleType("import_exercise_batch.process.subprocess.api")
    api_module.CodeReviewAiSubProcess = type("CodeReviewAiSubProcess", (), {})
    api_module.CodeReviewSubProcess = type("CodeReviewSubProcess", (), {})
    sys.modules[api_module.__name__] = api_module

    csv_module = ModuleType("import_exercise_batch.process.subprocess.csv")
    csv_module.ExerciseCsvSubProcess = type("ExerciseCsvSubProcess", (), {})
    sys.modules[csv_module.__name__] = csv_module

    database_module = ModuleType("import_exercise_batch.process.subprocess.database")
    database_module.ExerciseDatabaseSubProcess = type(
        "ExerciseDatabaseSubProcess", (), {}
    )
    sys.modules[database_module.__name__] = database_module

    leetcode_module = ModuleType("import_exercise_batch.process.subprocess.leetcode")
    leetcode_module.LeetCodeFetchSubProcess = type("LeetCodeFetchSubProcess", (), {})
    sys.modules[leetcode_module.__name__] = leetcode_module

    module_path = (
        Path(__file__).resolve().parents[1]
        / "src/import_exercise_batch/process/mainprocess/import_exercises.py"
    )
    spec = importlib.util.spec_from_file_location(
        "test_import_exercises_module",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load import_exercises.py for testing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ImportExercisesMainProcess


ImportExercisesMainProcess = _load_import_exercises_mainprocess_class()


def _build_problem(
    *,
    question_slug: str = "two-sum",
    content: str = "Problem content",
    sample_test_case: str = "1\n2",
    code_snippet: str = "class Solution {};",
) -> LeetCodeProblem:
    return LeetCodeProblem(
        question_slug=question_slug,
        title="Two Sum",
        content=content,
        sample_test_case=sample_test_case,
        code_snippet=code_snippet,
        difficulty="EASY",
        topic_tag_slugs=["array"],
        similar_question_slugs=[],
    )


class ImportExercisesMainProcessTest(unittest.TestCase):
    def test_problem_has_full_payload_requires_content_sample_and_snippet(self) -> None:
        self.assertTrue(_build_problem().has_full_payload())
        self.assertFalse(_build_problem(content="").has_full_payload())
        self.assertFalse(_build_problem(sample_test_case="").has_full_payload())
        self.assertFalse(_build_problem(code_snippet="").has_full_payload())

    def test_filter_exercises_with_full_payload_skips_incomplete_exercises(self) -> None:
        process = ImportExercisesMainProcess.__new__(ImportExercisesMainProcess)
        complete_problem = _build_problem(question_slug="two-sum")
        incomplete_problem = _build_problem(
            question_slug="unique-substrings-with-equal-digit-frequency",
            content="",
            code_snippet="",
        )

        filtered = process._filter_exercises_with_full_payload(
            [complete_problem, incomplete_problem],
            tag_slug="string",
        )

        self.assertEqual([complete_problem], filtered)


if __name__ == "__main__":
    unittest.main()
