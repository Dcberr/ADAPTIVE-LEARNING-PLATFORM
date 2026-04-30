from typing import TypedDict, Any, Dict, List

from code_review_ai.api.review_code_schema import ReviewItem
from code_review_ai.models.improvement_note import ImprovementNote
from code_review_ai.models.logic_issue import LogicIssue
from code_review_ai.models.review_link import ReviewLink
from code_review_ai.models.sandbox_result import SandBoxResult


class SubmissionHistory(TypedDict):
    submission_id: str
    code: str
    failed_test_case_ids: List[str]
    passed_test_case_ids: List[str]


class ReviewState(TypedDict):
    code: str
    assignment_language: str
    sandbox_results: List[SandBoxResult]
    assignment_requirements: str
    history: List[SubmissionHistory]
    previous_failed_test_case_ids: List[str]
    persistent_failed_test_case_ids: List[str]
    fixed_test_case_ids: List[str]
    regressed_test_case_ids: List[str]
    logic_issues: Dict[str, LogicIssue]
    improvement_notes: List[ImprovementNote]
    review_links: List[ReviewLink]
    overview: str
    review_items: List[ReviewItem]
    scorecard: Dict[str, Any]


def create_initial_state(
    code: str,
    assignment_language: str,
    sandbox_results: List[SandBoxResult],
    assignment_requirements: str,
    history: List[SubmissionHistory],
) -> ReviewState:
    """Helper function to create a properly initialized ReviewState"""
    current_failed_test_case_ids = [result["id"] for result in sandbox_results]
    latest_previous_submission = history[0] if history else None
    previous_failed_test_case_ids = (
        latest_previous_submission.get("failed_test_case_ids", [])
        if latest_previous_submission
        else []
    )
    persistent_failed_test_case_ids = [
        testcase_id
        for testcase_id in current_failed_test_case_ids
        if testcase_id in previous_failed_test_case_ids
    ]
    fixed_test_case_ids = [
        testcase_id
        for testcase_id in previous_failed_test_case_ids
        if testcase_id not in current_failed_test_case_ids
    ]
    regressed_test_case_ids = [
        testcase_id
        for testcase_id in current_failed_test_case_ids
        if testcase_id not in previous_failed_test_case_ids
    ]

    return {
        "code": code,
        "assignment_language": assignment_language,
        "sandbox_results": sandbox_results,
        "assignment_requirements": assignment_requirements,
        "history": history,
        "previous_failed_test_case_ids": previous_failed_test_case_ids,
        "persistent_failed_test_case_ids": persistent_failed_test_case_ids,
        "fixed_test_case_ids": fixed_test_case_ids,
        "regressed_test_case_ids": regressed_test_case_ids,
        "logic_issues": {},
        "categorized_feedback": [],
        "improvement_notes": [],
        "review_links": [],
        "advanced_suggestions": [],
        "final_report": {},
        "static_issues": [],
        # initialize runtime flags
        "has_errors": False,
        "needs_improvement": False,
        "overview": "",
        "review_items": [],
        "scorecard": [],
    }
