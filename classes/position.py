from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Position:
    """
    Represents a position in a 2D grid with x and y coordinates. No methods.
    """
    x: int
    y: int