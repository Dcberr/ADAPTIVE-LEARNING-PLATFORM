from typing import TypedDict


class SandBoxResult(TypedDict):
    id: int
    input: str
    expected: str
    actual: str
