from pydantic import BaseModel, Field


class SubmissionTestCaseOutput(BaseModel):
    expect: str = ""
    output: str = ""


class SubmissionRecord(BaseModel):
    submission_id: str
    student_id: str
    exercise_id: str = ""
    code: str
    testcase_outputs: list[SubmissionTestCaseOutput] = Field(default_factory=list)
    created_at: str = ""
