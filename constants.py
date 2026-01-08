import pygame
from classes.direction import Direction
from classes.ui.key_actions import KeyActions

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

    DISPLAY_WIDTH: int = 960
    DISPLAY_HEIGHT: int = 560

    DISPLAY_MONITOR: int = 0

    # Sim
    DEFAULT_ZOOM: float = 1.05
    MAX_ZOOM: float = 10
    MIN_ZOOM: float = 0.1
    ZOOM_FACTOR: float = 1.1
    WORLD_OOB_FACTOR: int = 20
    SPAWN_TICKS = 3

    # Misc
    DEFAULT_BINDINGS: dict[KeyActions, int] = {
        KeyActions.PAN_ALIAS: pygame.K_a,

        KeyActions.PAN_UP: pygame.K_UP,
        KeyActions.PAN_DOWN: pygame.K_DOWN,
        KeyActions.PAN_LEFT: pygame.K_LEFT,
        KeyActions.PAN_RIGHT: pygame.K_RIGHT,

        KeyActions.ZOOM_IN_ALIAS: pygame.K_PLUS,
        KeyActions.ZOOM_OUT_ALIAS: pygame.K_MINUS,

        KeyActions.ADVANCE_DIALOGUE: pygame.K_c,
        KeyActions.PAUSE_UNPAUSE: pygame.K_SPACE,

        KeyActions.STEP_FORWARD: pygame.K_PERIOD,
        KeyActions.STEP_BACKWARD: pygame.K_COMMA,

        KeyActions.REGENERATE_WORLD: pygame.K_r,
    }