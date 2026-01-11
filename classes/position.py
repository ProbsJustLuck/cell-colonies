from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """
    Represents a position in a 2D grid with x and y coordinates.
    """
    x: int
    y: int


    def __str__(self) -> str: return f"Position ({self.x}, {self.y})"


pos_cache: dict[tuple[int, int], Position] = {}


def get_pos(pos: tuple[int, int]) -> Position:
    if pos not in pos_cache: pos_cache[pos] = Position(pos[0], pos[1])

    return pos_cache[pos]