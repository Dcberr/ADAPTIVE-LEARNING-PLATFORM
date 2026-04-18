from pydantic import BaseModel
from typing import List, Optional


class ProblemDTO(BaseModel):
    """DTO for representing a LeetCode problem"""
    title: str
    difficulty: str
    content: str
    constraints: List[str]
    examples: dict  # Dictionary of examples, e.g. {"example1": {"input": "...", "output": "...", "explanation": "..."}, ...}
    code_snippet: str

    class Config:
        from_attributes = True


class ProblemListResponseDTO(BaseModel):
    """DTO for paginated list response"""
    total: int
    page: int
    limit: int
    data: List[ProblemDTO]
