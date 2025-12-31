from classes.direction import Direction

class Constants:
    DIRECTION_MAPPINGS: dict[Direction, tuple[int, int]] = {
        Direction.NORTH: (-1, 0),
        Direction.SOUTH: (1, 0),
        Direction.EAST:  (0, 1),
        Direction.WEST:  (0, -1), 
    }

    POSITION_MAPPINGS: dict[tuple[int, int], Direction] = {
        value: key for key, value in DIRECTION_MAPPINGS.items()
    }

    SCREEN_WIDTH: int = 1200
    SCREEN_HEIGHT: int = 700

    # Sim
    DEFAULT_ZOOM: float = 1.05
    MAX_ZOOM: float = 10
    MIN_ZOOM: float = 0.1
    ZOOM_FACTOR: float = 1.1
    WORLD_OOB_FACTOR: int = 20