from typing import Callable
import pygame

from constants import Constants
from classes.lerp import Lerp
import classes.ui.button as Button
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
import classes.wall as wall
from classes.position import Position

from util import assets
from util.game_states import States as state
from util.ui_helpers import create_text, add_outline_to_image, draw_text
from util.game_actions import create_world
from util import menu_assets

STARTING_SIZE = 300
ENDING_SIZE = 160

ENDING_DISPLACEMENT = 160

_base1: pygame.Surface = add_outline_to_image(create_text("Cell", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))
_base2: pygame.Surface = add_outline_to_image(create_text("Colonies", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))

_title_scale_lerp: Lerp | None = None
_title_offset_lerp: Lerp | None = None
_button_opacity_lerp: Lerp | None = None
_centers: tuple[tuple[int,int], tuple[int,int]] | None = None


def render_start_screen() -> None:
    global _base1, _base2, _title_scale_lerp, _title_offset_lerp, _button_opacity_lerp

    # Background
    assets.screen.blit(assets.main_menu_background, assets.main_menu_background.get_rect(topleft = (0, 0)))

    for slider in menu_assets.sliders.get(state.current_area, []):
        slider.draw(assets.screen)

    if not state.skipped_animation:

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

            state.starting_opacity = 0
            return
    
    global _centers

    # Recompute the surfaces for the text to be in their final position (less laggy/math to do)
    if not _centers:
        state.loaded_menu = True

        _base1.set_alpha(255)
        _base2.set_alpha(255)

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

        _button_opacity_lerp = Lerp(0, 255, 2000)

    # Display main title and fade in other text
    assets.screen.blit(_base1, _base1.get_rect(center=(_centers[0])))
    assets.screen.blit(_base2, _base2.get_rect(center=(_centers[1])))

    # Fade in other text text
    mouse_pos = pygame.mouse.get_pos()
    for button in menu_assets.buttons.get(state.current_area, []):
        if not state.skipped_animation:
            if not button.disabled and _button_opacity_lerp:
                button.style.opacity = int(_button_opacity_lerp.value(pygame.time.get_ticks()))
            elif _button_opacity_lerp: 
                button.style.overwrite_opacity = min(int(_button_opacity_lerp.value(pygame.time.get_ticks())), button.style.disabled_opacity)
        else:
            button.style.opacity = 255
            button.style.overwrite_opacity = -1

        button.draw(assets.screen, mouse_pos)
    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None


def render_game_screen():
    # Background
    assets.screen.blit(assets.simulation_background, assets.simulation_background.get_rect(topleft = (0, 0)))

    if not state.world: create_world(homebases=2, size=50)
    assert state.world

    world_size = state.world.size

    # Viewport
    pygame.draw.rect(assets.screen, "#283c50", state.SIM_RECT)
    pygame.draw.rect(assets.screen, "#000000", state.SIM_RECT, width=3, border_radius=4)

    # Get cell sizes
    base_cell = state.SIM_RECT.width / world_size
    cell_size = max(2, int(base_cell * state.zoom))
    origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset

    # Gridlines
    line_color = (70, 90, 110)
    world_rect = pygame.Rect(origin.x, origin.y, world_size * cell_size, world_size * cell_size)
    clipped_rect = state.SIM_RECT.clip(world_rect) # stop rendering gridlines and cells offscreen

    for i in range(world_size + 1):
        x = origin.x + i * cell_size
        y = origin.y + i * cell_size

        # ver
        if state.SIM_RECT.left <= x <= state.SIM_RECT.right: pygame.draw.line(assets.screen, line_color, (x, clipped_rect.top), (x, clipped_rect.bottom))
        # hor
        if state.SIM_RECT.top <= y <= state.SIM_RECT.bottom: pygame.draw.line(assets.screen, line_color, (clipped_rect.left, y), (clipped_rect.right, y))

    # Draw cells
    for row in range(world_size):
        for col in range(world_size):
            cell = state.world.get_cell(Position(row, col))
            if cell is None:
                continue
            if isinstance(cell, homebase.Homebase):
                color = (200, 60, 60)
            elif isinstance(cell, attacker.Attacker):
                color = (60, 60, 200)
            elif isinstance(cell, rotator.Rotator):
                color = (60, 180, 180)
            elif isinstance(cell, wall.Wall):
                color = (100, 100, 100)
            else:
                color = (160, 160, 160)

            x = int(origin.x + col * cell_size)
            y = int(origin.y + row * cell_size)

            rect = pygame.Rect(x, y, cell_size, cell_size)
            rect = rect.clip(state.SIM_RECT)
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(assets.screen, color, rect)

    # makes the top edge cleaner
    pygame.draw.rect(assets.screen, "#000000", state.SIM_RECT, width=3, border_radius=4)

    pos = pygame.mouse.get_pos()
    for button in menu_assets.buttons.get(state.current_area, []):
        button.draw(assets.screen, pos)
    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None

    if state.show_tps:
        rect = pygame.Rect(647, 378, 40, 255)
        pygame.draw.rect(assets.screen, "#000000", rect)

        rect = pygame.Rect(650, 381, 34, 249)
        pygame.draw.rect(assets.screen, "#a5a5a5", rect)

        draw_text(Position(667, 398), f"{state.target_tps:.1f}", "#000000", 27, mode="center")

        for slider in menu_assets.sliders.get(state.current_area, []):
            slider.draw(assets.screen)
        