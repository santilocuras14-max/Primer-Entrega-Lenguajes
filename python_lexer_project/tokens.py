
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    type: str
    value: object
    line: int
    column: int
