import logging

from fastapi import APIRouter, Depends, HTTPException
from code_review_ai.api.review_code_deps import get_review_service
from code_review_ai.api.review_code_schema import (
    ColumnContext,
    LineContext,
    ReviewItem,
    ReviewRequest,
    ReviewResponse,
)
from code_review_ai.models.review_state import ReviewState, create_initial_state
from code_review_ai.services.review_code_service import ReviewCodeService
from code_review_ai.utils.debug_logging import summarize_state

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/review_code", response_model=ReviewResponse)
async def review_code(
    request: ReviewRequest,
    review_code_service: ReviewCodeService = Depends(get_review_service),
):
    """
    Endpoint that uses the LangGraph workflow with Gemini for code review.
    """
    try:
        logger.debug(
            "Received review request with %s test results and %s history entries",
            len(request.test_results),
            len(request.history),
        )

        # Create initial state using the helper function
        state_in: ReviewState = create_initial_state(
            code=request.code,
            assignment_language=request.assignment.language,
            sandbox_results=[
                {
                    "id": str(case.testcase_id),
                    "input": case.input,
                    "actual": case.actual,
                    "expected": case.expect,
                }
                for case in [result for result in request.test_results]
            ],
            assignment_requirements=request.assignment.content,
            history=[
                {
                    "submission_id": str(submission.submission_id),
                    "code": submission.code,
                    "failed_test_case_ids": [
                        str(testcase_id)
                        for testcase_id in submission.failed_test_case_ids
                    ],
                    "passed_test_case_ids": [
                        str(testcase_id)
                        for testcase_id in submission.passed_test_case_ids
                    ],
                }
                for submission in request.history
            ],
        )
        logger.debug(
            "Created initial workflow state summary: %s", summarize_state(state_in)
        )

        # Run the review graph
        result_state = await review_code_service.review_code(state_in)
        logger.debug(
            "Workflow completed with result summary: %s",
            summarize_state(result_state),
        )
        # Get the overview and review items from the result state
        overview = result_state["overview"]
        review_items = [
            ReviewItem(
                code_snippet=item["code_snippet"],
                issue=item["issue"],
                type=item["type"],
                fix_suggestion=item["fix_suggestion"],
                line=LineContext(
                    start=(item.get("location") or {}).get("start_line", 1),
                    end=(item.get("location") or {}).get("end_line", 1),
                ),
                column=ColumnContext(
                    start=(item.get("location") or {}).get("start_col"),
                    end=(item.get("location") or {}).get("end_col"),
                ),
                review_link=item.get("review_link"),
            )
            for item in result_state["review_items"]
        ]

        response = ReviewResponse(
            summary=overview,
            detail="Review completed",
            review_items=review_items,
        )
        return response

    except Exception as e:
        logger.exception("Review process failed")
        raise HTTPException(status_code=500, detail=f"Review process failed: {str(e)}")
