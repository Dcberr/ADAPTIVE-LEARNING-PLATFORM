from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from types import ModuleType

from import_exercise_batch.model import LeetCodeProblem


def _load_import_exercises_mainprocess_class() -> type:
    original_modules: dict[str, ModuleType | None] = {}

    def _swap_module(name: str, module: ModuleType) -> None:
        original_modules[name] = sys.modules.get(name)
        sys.modules[name] = module

    api_module = ModuleType("import_exercise_batch.process.subprocess.api")
    api_module.CodeReviewAiSubProcess = type("CodeReviewAiSubProcess", (), {})
    api_module.CodeReviewSubProcess = type("CodeReviewSubProcess", (), {})
    _swap_module(api_module.__name__, api_module)

    csv_module = ModuleType("import_exercise_batch.process.subprocess.csv")
    csv_module.ExerciseCsvSubProcess = type("ExerciseCsvSubProcess", (), {})
    _swap_module(csv_module.__name__, csv_module)

    database_module = ModuleType("import_exercise_batch.process.subprocess.database")
    database_module.ExerciseDatabaseSubProcess = type(
        "ExerciseDatabaseSubProcess", (), {}
    )
    _swap_module(database_module.__name__, database_module)

    leetcode_module = ModuleType("import_exercise_batch.process.subprocess.leetcode")
    leetcode_module.LeetCodeFetchSubProcess = type("LeetCodeFetchSubProcess", (), {})
    _swap_module(leetcode_module.__name__, leetcode_module)

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
    try:
        spec.loader.exec_module(module)
        return module.ImportExercisesMainProcess
    finally:
        for module_name, original_module in original_modules.items():
            if original_module is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = original_module


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

    def test_prepare_csv_path_uses_existing_csv_when_requested(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        csv_path = Path(temp_dir.name) / "import_exercises.csv"
        csv_path.write_text("question_slug\n", encoding="utf-8")

        process = ImportExercisesMainProcess.__new__(ImportExercisesMainProcess)
        process.use_existing_csv = True
        process.settings = SimpleNamespace(
            database=SimpleNamespace(import_csv_path=csv_path)
        )

        resolved_csv_path = process._prepare_csv_path()

        self.assertEqual(csv_path, resolved_csv_path)

    def test_prepare_csv_path_raises_when_existing_csv_is_missing(self) -> None:
        process = ImportExercisesMainProcess.__new__(ImportExercisesMainProcess)
        process.use_existing_csv = True
        process.settings = SimpleNamespace(
            database=SimpleNamespace(
                import_csv_path=Path("/tmp/does-not-exist-import-exercises.csv")
            )
        )

        with self.assertRaises(FileNotFoundError):
            process._prepare_csv_path()


if __name__ == "__main__":
    unittest.main()
