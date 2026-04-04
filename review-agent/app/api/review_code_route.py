import logging

from fastapi import APIRouter, Depends, HTTPException
from app.api.review_code_deps import get_review_service
from app.api.review_code_schema import (
    ColumnContext,
    LineContext,
    ReviewItem,
    ReviewRequest,
    ReviewResponse,
)
from app.models.review_state import ReviewState, create_initial_state
from app.services.review_code_service import ReviewCodeService
from app.utils.debug_logging import summarize_state

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
            "Received review request with %s test results and %s expected concepts",
            len(request.test_results),
            len(request.assignment.expected_concepts),
        )

        # Create initial state using the helper function
        state_in: ReviewState = create_initial_state(
            code=request.student_submission.code,
            sandbox_results=[
                {
                    "id": i,
                    "input": case.input,
                    "actual": case.actual,
                    "expected": case.expect,
                }
                for i, case in enumerate(
                    [
                        result
                        for result in request.test_results
                        if result.status == "fail"
                    ]
                )
            ],
            assignment_requirements=request.assignment.content,
            expected_concepts=request.assignment.expected_concepts,
        )
        logger.debug("Created initial workflow state summary: %s", summarize_state(state_in))

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
                    start=item["location"].get("start_line", 1),
                    end=item["location"].get("end_line", 1),
                ),
                column=ColumnContext(
                    start=item["location"].get("start_col"),  # returns None if missing
                    end=item["location"].get("end_col"),
                ),
            )
            for item in result_state["review_items"]
        ]

        return ReviewResponse(
            summary=overview,
            detail="Review completed",
            review_items=review_items,
        )

    except Exception as e:
        logger.exception("Review process failed")
        raise HTTPException(status_code=500, detail=f"Review process failed: {str(e)}")
