from enum import Enum, auto

class GameState(Enum):
    WIN = auto()
    LOSS = auto()
    CONTINUE = auto()