from typing import TypedDict


class SandBoxResult(TypedDict):
    id: str
    input: str
    expected: str
    actual: str
