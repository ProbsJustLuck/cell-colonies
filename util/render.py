from typing import Callable
import pygame

from constants import Constants
from classes.lerp import Lerp
from util import assets
from util.game_states import States as state
from util.ui_helpers import create_text, add_outline_to_image
from util.menu_assets import main_menu_buttons

STARTING_SIZE = 300
ENDING_SIZE = 160

ENDING_DISPLACEMENT = 160

_base1: pygame.Surface = add_outline_to_image(create_text("Cell", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))
_base2: pygame.Surface = add_outline_to_image(create_text("Colonies", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))

_title_scale_lerp: Lerp | None = None
_title_offset_lerp: Lerp | None = None
_centers: tuple[tuple[int,int], tuple[int,int]] | None = None

def draw_buttons():
    mouse_pos = pygame.mouse.get_pos()
    for b in main_menu_buttons:
        b.draw(assets.screen, mouse_pos)


def render_start_screen() -> None:
    global _base1, _base2, _title_scale_lerp, _title_offset_lerp

    # Background
    assets.screen.blit(assets.background, assets.background.get_rect(topleft = (0, 0)))

    # Fade in title text
    if state.starting_opacity < 255 and not _title_scale_lerp:
        state.starting_opacity += 2

        _base1.set_alpha(state.starting_opacity)
        _base2.set_alpha(state.starting_opacity)
        assets.screen.blit(_base1, _base1.get_rect(center = (Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2 - _base1.get_height() / 2)))
        assets.screen.blit(_base2, _base2.get_rect(center = (Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2 + (STARTING_SIZE / 6))))
        return
    
    # Initialize lerps
    if not _title_scale_lerp or not _title_offset_lerp:
        ease_func: Callable[[float], float] = lambda t: 4*t*t*t if t < 0.5 else 1 - ((-2*t + 2)**3.5) / 2

        _title_scale_lerp = Lerp(STARTING_SIZE, ENDING_SIZE, 2000, ease_func)
        _title_offset_lerp = Lerp(0, ENDING_DISPLACEMENT, 2000, ease_func)

    # Smooth animation
    if not _title_scale_lerp.done:
        now = pygame.time.get_ticks()
        scale = _title_scale_lerp.value(now) / STARTING_SIZE
        offset = _title_offset_lerp.value(now)

        # scale once per frame based on the base sizes
        text1 = pygame.transform.smoothscale(
            _base1,
            (int(_base1.get_width() * scale), int(_base1.get_height() * scale))
        )
        text2 = pygame.transform.smoothscale(
            _base2,
            (int(_base2.get_width() * scale), int(_base2.get_height() * scale))
        )

        mid_y = Constants.SCREEN_HEIGHT // 2
        gap = (_base1.get_height() * scale) / 2  # keeps spacing relative to text scales

        assets.screen.blit(text1, text1.get_rect(center=(Constants.SCREEN_WIDTH // 2, mid_y - gap - offset)))
        assets.screen.blit(text2, text2.get_rect(center=(Constants.SCREEN_WIDTH // 2, mid_y - offset + (STARTING_SIZE / 6) * scale)))
        return
    
    global _centers

    # Recompute the surfaces for the text to be in their final position (less laggy/math to do)
    if not _centers:    
        scale = ENDING_SIZE / STARTING_SIZE
        offset = ENDING_DISPLACEMENT
        mid_y = Constants.SCREEN_HEIGHT // 2
        gap = (_base1.get_height() * scale) / 2

        _base1 = pygame.transform.smoothscale(
            _base1,
            (int(_base1.get_width() * scale), int(_base1.get_height() * scale))
        )
        _base2 = pygame.transform.smoothscale(
            _base2,
            (int(_base2.get_width() * scale), int(_base2.get_height() * scale))
        )

        _centers = ((Constants.SCREEN_WIDTH // 2, int(mid_y - gap - offset)), (Constants.SCREEN_WIDTH // 2, int(mid_y - offset + (STARTING_SIZE / 6) * scale))) # math wasn't mathing

    # Display main title and fade in other text
    assets.screen.blit(_base1, _base1.get_rect(center=(_centers[0])))
    assets.screen.blit(_base2, _base2.get_rect(center=(_centers[1])))

    # Fade in other text text
    mouse_pos = pygame.mouse.get_pos()
    for button in main_menu_buttons:
        if button.style.opacity < 255: button.style.opacity = min(button.style.opacity + 2, 255)
        button.draw(assets.screen, mouse_pos)