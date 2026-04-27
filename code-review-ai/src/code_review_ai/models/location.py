from typing import TypedDict


class Location(TypedDict):
    start_line: int
    start_col: int
    end_line: int
    end_col: int
