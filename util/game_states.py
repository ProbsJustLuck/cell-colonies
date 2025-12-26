import pygame

class States:
    running: bool = True
    paused: bool = False

    # Menu flags
    in_main_menu: bool = True
    starting_opacity: int = 0

    # Buttons

    font_cache: dict[int, pygame.font.Font] = {}