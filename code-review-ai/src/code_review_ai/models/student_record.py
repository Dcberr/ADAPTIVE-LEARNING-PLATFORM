from pydantic import BaseModel


class StudentRecord(BaseModel):
    student_id: str
    current_concept: str = ""
    notes: str = ""
