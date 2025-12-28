from typing import TYPE_CHECKING
import pygame
from classes.ui.menu_area import MenuArea
from constants import Constants

if TYPE_CHECKING:
    from classes.world_manager import WorldManager

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
    panning: bool = False
    world: "WorldManager | None" = None 
    
    ## Zooming + panning
    offset: pygame.Vector2 = pygame.Vector2(0, 0)
    SIM_RECT = pygame.Rect(55, 55, 590, 590)
    zoom: float = Constants.DEFAULT_ZOOM
    zoom_levels: list[float] = []
    zoom_index: int = 0
    panning: bool = False
    old_cursor_pos: tuple[int, int] = (0, 0)

    font_cache: dict[int, pygame.font.Font] = {}
