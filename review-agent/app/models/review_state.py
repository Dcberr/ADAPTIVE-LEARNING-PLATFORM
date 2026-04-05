from typing import TypedDict, Any, Dict, List

from app.api.review_code_schema import ReviewItem
from app.models.generate_testcase import GenerateTestcase
from app.models.improvement_note import ImprovementNote
from app.models.logic_issue import LogicIssue
from app.models.sandbox_result import SandBoxResult


class ReviewState(TypedDict):
    code: str
    assignment_language: str
    sandbox_results: List[SandBoxResult]
    assignment_requirements: str
    expected_concepts: List[str]
    logic_issues: Dict[int, LogicIssue]
    concept_issues: List[Dict[str, Any]]
    generated_testcases: List[GenerateTestcase]
    improvement_notes: List[ImprovementNote]
    overview: str
    review_items: List[ReviewItem]


def create_initial_state(
    code: str,
    assignment_language: str,
    sandbox_results: List[SandBoxResult],
    assignment_requirements: str,
    expected_concepts: List[str],
) -> ReviewState:
    """Helper function to create a properly initialized ReviewState"""
    return {
        "code": code,
        "assignment_language": assignment_language,
        "sandbox_results": sandbox_results,
        "assignment_requirements": assignment_requirements,
        "expected_concepts": expected_concepts,
        "logic_issues": [],
        "concept_issues": [],
        "generated_testcases": [],
        "categorized_feedback": [],
        "improvement_notes": [],
        "advanced_suggestions": [],
        "final_report": {},
        "static_issues": [],
        # initialize runtime flags
        "has_errors": False,
        "needs_improvement": False,
        "overview": "",
        "review_items": [],
    }
