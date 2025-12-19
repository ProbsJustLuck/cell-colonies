from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int