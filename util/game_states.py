from typing import TYPE_CHECKING
import pygame
from classes.ui.menu_area import MenuArea
from constants import Constants

if TYPE_CHECKING:
    from classes.world_manager import WorldManager
    from classes.ui.button import Button

class States:
    running: bool = True
    full_pause: bool = False
    sim_pause: bool = True

    # Menu flags
    skipped_animation: bool = False
    loaded_menu: bool = False
    current_area = MenuArea.MAIN_MENU
    starting_opacity: int = 0

    # Simulation
    game_end: bool = False
    panning: bool = False
    world: "WorldManager | None" = None
    target_tps: float = 2
    max_catchup: int = 5
    max_history: int = 20
    show_tps: bool = False
    
    ## Zooming + panning
    offset: pygame.Vector2 = pygame.Vector2(0, 0)
    SIM_RECT = pygame.Rect(55, 70, 590, 520)
    zoom: float = Constants.DEFAULT_ZOOM
    zoom_levels: list[float] = []
    zoom_index: int = 0
    panning: bool = False
    old_cursor_pos: tuple[int, int] = (0, 0)

    ## Rewind/forward
    fast_forward: "Button | None" = None
    forward: "Button | None" = None
    pause: "Button | None" = None
    rewind: "Button | None" = None
    fast_rewind: "Button | None" = None
    tps_button: "Button | None" = None

    font_cache: dict[int, pygame.font.Font] = {}
