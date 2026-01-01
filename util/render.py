from typing import Callable
import pygame

from classes.wall import Wall
from constants import Constants
from classes.lerp import Lerp
import classes.ui.button as Button
from classes.position import Position
from classes.attacker import Attacker
from classes.homebase import Homebase
from classes.rotator import Rotator

from util import assets
from util.game_states import States as state
from util.ui_helpers import create_text, add_outline_to_image, draw_text, fit_view
from util.game_actions import create_world
from util import menu_assets

STARTING_SIZE = 300
ENDING_SIZE = 160

ENDING_DISPLACEMENT = 160

# Bunch of caches
_base1: pygame.Surface = add_outline_to_image(create_text("Cell", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))
_base2: pygame.Surface = add_outline_to_image(create_text("Colonies", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))

_title_scale_lerp: Lerp | None = None
_title_offset_lerp: Lerp | None = None
_button_opacity_lerp: Lerp | None = None
_centers: tuple[tuple[int,int], tuple[int,int]] | None = None

_icons: dict[tuple[int, int, int | None], pygame.Surface] = {}
_cell_size: int | None = None


def get_icon(surf: pygame.Surface, cell_size: int, alpha: int | None = None) -> pygame.Surface:
    key = (id(surf), cell_size, alpha)

    icon = _icons.get(key)
    if icon: return icon

    icon = pygame.transform.smoothscale(surf, (cell_size, cell_size))
    if alpha:
        icon = icon.copy()
        icon.set_alpha(alpha)
    _icons[key] = icon
    return icon


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

    if not state.world: 
        create_world()
        fit_view(state.sim_size)
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
    if "Gridlines" not in state.disabled_cells:
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
    global _icons, _cell_size
    cell_size = int((state.SIM_RECT.width / world_size) * state.zoom)

    if cell_size != _cell_size:
        _icons.clear()
        _cell_size = cell_size

    for row in range(world_size):
        for col in range(world_size):
            cell = state.world.get_cell(Position(row, col))
            if not cell: continue
            if cell.name in state.disabled_cells: continue

            x = int(origin.x + col * cell_size)
            y = int(origin.y + row * cell_size)

            rect = pygame.Rect(x, y, cell_size, cell_size)
            visible = rect.clip(state.SIM_RECT)
            if rect.width <= 0 or rect.height <= 0: continue

            src = pygame.Rect(visible.x - rect.x, visible.y - rect.y, visible.width, visible.height)
            icon = get_icon(cell.icon, cell_size, 180)
            assets.screen.blit(icon, visible.topleft, area=src)


    # makes the edges cleaner
    pygame.draw.rect(assets.screen, "#000000", state.SIM_RECT, width=2, border_radius=4)


    # Selected cell
    if state.selected_cell:
        if not state.selected_cell.alive: 
            state.selected_cell = None
            return
        cell = state.selected_cell

        rect = pygame.Rect(660, 70, 500, 300)
        pygame.draw.rect(assets.screen, "#a5a5a5", rect)
        pygame.draw.rect(assets.screen, "#000000", rect, width=4, border_radius=4)

        icon = get_icon(cell.icon, 64)
        assets.screen.blit(icon, (670, 80))

        title = cell.name
        LINE_SPACING = 28
        if isinstance(cell, Homebase): 
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Health: {cell.health} / {cell.max_health} HP ({(cell.health/cell.max_health * 100):.2f}%)", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Cells Alive: {cell.cells_amount} (peak {cell.max_cells_alive})", "#000000", 35)

            last_cell = cell.last_cell_spawned
            if last_cell:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Last Cell Spawned: {last_cell.name} - Position ({last_cell.pos.x}, {last_cell.pos.y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Last Cell Spawned: None", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Ticks Until Spawn: {Constants.SPAWN_TICKS - cell.spawn_ticks}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Ticks Since Targetted: {max(0, cell.ticks_since_targeted - 1)} (max 8)", "#000000", 35)


        elif isinstance(cell, Attacker):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Target: {cell.target.color.name} {cell.target.name} - Position ({cell.target.pos.x}, {cell.target.pos.y})", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Rotated: {cell.rotated}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Direction: {cell.direction}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Ticks Since Valid Path: {cell.ticks_since_valid_path} (max 5)", "#000000", 35)

            if cell.path:
                draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Next Spot: Position ({cell.path[0].x}, {cell.path[0].y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Next Spot: None!", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 5)), f"Path Length: {len(cell.path)}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 6)), f"Damage: {cell.damage}", "#000000", 35)

        elif isinstance(cell, Rotator):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Health: {cell.health} / {cell.max_health} HP ({(cell.health/cell.max_health * 100):.2f}%)", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Stationary: {cell.stationary}", "#000000", 35)

            if cell.target:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Target: Position ({cell.target.x}, {cell.target.y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Target: {cell.target}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Path Length: {len(cell.path)}", "#000000", 35)

        elif isinstance(cell, Wall):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Generic wall.", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Entities cannot move through this.", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Does not belong to a colony.", "#000000", 35)
        
        # Name
        if cell.name != "Wall":
            draw_text(Position(750, 90), f"{cell.color.name} {title}", "#000000", 43)
            draw_text(Position(751, 90), f"{cell.color.name} {title}", "#000000", 43)
        else:
            draw_text(Position(750, 90), f"{title}", "#000000", 43)
            draw_text(Position(751, 90), f"{title}", "#000000", 43)

        # Type
        draw_text(Position(751, 118), f"{cell.type} Cell - Position ({cell.pos.x}, {cell.pos.y}) [ID #{cell.id}]", "#000000", 35)


    pos = pygame.mouse.get_pos()
    for button in menu_assets.buttons.get(state.current_area, []):
        if (button.id in ["walls_toggle", "homebase_toggle", "rotator_toggle"] and not state.second_render_page) or (button.id in ["attackers_toggle", "gridlines_toggle", "fit_view"] and state.second_render_page): continue

        button.draw(assets.screen, pos)

    assets.screen.blit(assets.rotation_arrow, (124, 602))

    if state.show_tps: # tps slider
        rect = pygame.Rect(647, 378, 40, 255)
        pygame.draw.rect(assets.screen, "#000000", rect)

        rect = pygame.Rect(650, 381, 34, 249)
        pygame.draw.rect(assets.screen, "#a5a5a5", rect)

        draw_text(Position(667, 398), f"{state.target_tps:.1f}", "#000000", 27, mode="center")

        for slider in menu_assets.sliders.get(state.current_area, []):
            slider.draw(assets.screen)
    
    if state.changing_seed:
        rect = pygame.Rect(300, 100, 600, 500)

        pygame.draw.rect(assets.screen, "#000000", rect, width=10, border_radius=4)
        rect = rect.inflate(-10, -10)
        state.seed_box = rect.copy()
        pygame.draw.rect(assets.screen, "#a5a5a5", rect, border_radius=4)

        draw_text(Position(435, 150), "Seed Settings", "#000000", 80)
        draw_text(Position(436, 150), "Seed Settings", "#000000", 80)

        draw_text(Position(600, 250), "Current Seed", "#272727", 40, mode="center")
        draw_text(Position(600, 290), f"{state.world.seed}", "#000000", 60, mode="center")

        rect = pygame.Rect(400, 320, 400, 50)
        if not state.typing_seed:
            pygame.draw.rect(assets.screen, "#ffffff", rect, width=10, border_radius=1)
        else:
            pygame.draw.rect(assets.screen, "#fffa70", rect, width=10, border_radius=1)

        rect = rect.inflate(-4, -4)
        state.typing_box = rect.copy()
        pygame.draw.rect(assets.screen, "#000000", rect, border_radius=1)

        if not state.seed_string: 
            draw_text(Position(410, 335), "Type seed...", "#ffffff", size=50, opacity=110)

        if state.seed_string:
            if not state.typing_seed:
                draw_text(Position(410, 335), f"{state.seed_string}", "#ffffff", size=50, opacity=140)
            else: 
                draw_text(Position(410, 335), f"{state.seed_string}", "#ffffff", size=50)
    
        draw_text(Position(405, 375), "ENTER to confirm, ESC to cancel", "#000000", size=30)

        mouse = pygame.mouse.get_pos()
        for i in range(4):
            menu_assets.special_buttons[i].draw(assets.screen, mouse)

        string = state.seed_string.strip("-")
        draw_text(Position(795, 370), f"{len(string)}/10", "#ffffff", size=25, mode="bottomright", opacity=160)

        if state.typing_seed and state.caret_timer / 500 <= 1:
            width = assets.big_font.size("1")[0]
            height = 2
            x = state.typing_box.x + 9 + assets.big_font.size(state.seed_string[:len(state.seed_string)])[0]
            y = state.typing_box.centery + assets.big_font.get_height() // 2
            pygame.draw.line(assets.screen, (255,255,255), (x, y), (x + width, y), height)

        assets.screen.blit(assets.COPY_ICON, (625, 475))
        assets.screen.blit(assets.PASTE_ICON, (700, 475))
        assets.screen.blit(assets.REGENERATE_ICON, (775, 483))


    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None