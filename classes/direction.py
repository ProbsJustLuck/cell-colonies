from enum import Enum

class Direction(Enum):
    """
    Represents the four cardinal directions. No methods, only class variables.
    """
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

    def __str__(self) -> str: return self.name.title()