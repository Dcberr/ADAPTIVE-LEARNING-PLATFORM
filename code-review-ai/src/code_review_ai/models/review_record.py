from pydantic import BaseModel


class ReviewRecord(BaseModel):
    review_id: str
    student_id: str
    exercise_id: str = ""
    submission_id: str = ""
    current_concept: str = ""
    created_at: str = ""
    summary: str
    detail: str
