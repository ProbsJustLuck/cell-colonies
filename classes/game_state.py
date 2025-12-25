from enum import Enum, auto

class GameState(Enum):
    """
    Represents the possible states of a game tick to return
    """
    WIN = auto()
    LOSS = auto()
    CONTINUE = auto()