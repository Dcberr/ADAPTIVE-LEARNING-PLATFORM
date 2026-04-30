from __future__ import annotations

import unittest
from uuid import uuid4

from code_review_api_client import ProblemResponse

from import_exercise_batch.model import LeetCodeProblemChange
from import_exercise_batch.process.subprocess.api import CodeReviewSubProcess


def _build_exercise_change(
    *,
    exercise_id: str | None,
    question_slug: str,
) -> LeetCodeProblemChange:
    return LeetCodeProblemChange(
        exercise_id=exercise_id,
        question_slug=question_slug,
        title="Two Sum",
        content="Problem content",
        sample_test_case="1\n2",
        code_snippet="class Solution {}",
        difficulty="EASY",
        topic_tag_slugs=["array"],
        similar_question_slugs=[],
        latest_sample_test_case="",
        latest_code_snippet="",
        latest_topic_tag_slugs=[],
        latest_similar_question_slugs=[],
        diff_type="create",
        is_change_content=False,
        is_change_topic=False,
        is_change_similar_question=False,
    )


class CodeReviewSubProcessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.subprocess = CodeReviewSubProcess(
            base_url="http://example.com",
            max_retries=1,
            backoff_seconds=0,
            batch_import_chunk_size=10,
        )

    def test_merge_import_results_uses_problem_response_ids(self) -> None:
        exercises = [
            _build_exercise_change(exercise_id=None, question_slug="two-sum"),
            _build_exercise_change(
                exercise_id="existing-id",
                question_slug="add-two-numbers",
            ),
        ]
        imported_problems = [
            ProblemResponse(
                id=uuid4(),
                externalId="add-two-numbers",
                title="Add Two Numbers",
            ),
            ProblemResponse(
                id=uuid4(),
                externalId="two-sum",
                title="Two Sum",
            ),
        ]

        merged = self.subprocess._merge_import_results(exercises, imported_problems)

        self.assertEqual(str(imported_problems[1].id), merged[0].exercise_id)
        self.assertEqual(str(imported_problems[0].id), merged[1].exercise_id)

    def test_merge_import_results_raises_when_response_is_missing_slug(self) -> None:
        exercises = [_build_exercise_change(exercise_id=None, question_slug="two-sum")]
        imported_problems = [
            ProblemResponse(
                id=uuid4(),
                externalId="different-slug",
                title="Other Problem",
            )
        ]

        with self.assertRaisesRegex(ValueError, "missing problems for slugs"):
            self.subprocess._merge_import_results(exercises, imported_problems)

    def test_parse_testcases_from_content_for_multi_param_input(self) -> None:
        content = """
        <p><strong class=\"example\">Example 1:</strong></p>
        <pre>
        <strong>Input:</strong> nums = [2,7,11,15], target = 9
        <strong>Output:</strong> [0,1]
        </pre>
        """

        testcases = self.subprocess._parse_testcases(sample_test_case="", content=content)

        self.assertEqual(1, len(testcases))
        self.assertEqual("[2,7,11,15]\n9", testcases[0].input)
        self.assertEqual("[0,1]", testcases[0].expected_output)

    def test_parse_testcases_from_content_for_single_param_input(self) -> None:
        content = """
        <p><strong class=\"example\">Example 1:</strong></p>
        <pre>
        Input: s = \"leetcode\"
        Output: true
        </pre>
        """

        testcases = self.subprocess._parse_testcases(sample_test_case="", content=content)

        self.assertEqual(1, len(testcases))
        self.assertEqual('"leetcode"', testcases[0].input)
        self.assertEqual("true", testcases[0].expected_output)


if __name__ == "__main__":
    unittest.main()