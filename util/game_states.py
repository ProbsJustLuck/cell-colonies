import pygame

class States:
    running: bool = True
    paused: bool = False

    in_main_menu: bool = True
    starting_opacity: int = 0

    start_game_rect: pygame.Rect | None = None
    infopedia_rect: pygame.Rect | None = None
    controls_rect: pygame.Rect | None = None
    quit_rect: pygame.Rect | None = None

    font_cache: dict[int, pygame.font.Font] = {}