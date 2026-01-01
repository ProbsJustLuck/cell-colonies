from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Position:
    """
    Represents a position in a 2D grid with x and y coordinates.
    """
    x: int
    y: int


    def __str__(self) -> str: return f"Position ({self.x}, {self.y})"