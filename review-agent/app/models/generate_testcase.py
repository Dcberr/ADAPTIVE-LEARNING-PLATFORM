from typing import NotRequired, TypedDict


class GenerateTestcase(TypedDict):
    id: int
    input: str
    expected_output: str
    status: str
    reason: str
    error: NotRequired[str]
