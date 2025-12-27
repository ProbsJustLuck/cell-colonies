import pygame
from classes.ui.menu_area import MenuArea

class States:
    running: bool = True
    full_pause: bool = False
    sim_pause: bool = True

    # Menu flags
    skipped_animation: bool = False
    loaded_menu: bool = False
    current_area = MenuArea.MAIN_MENU
    starting_opacity: int = 0

    # Buttons
    

    font_cache: dict[int, pygame.font.Font] = {}