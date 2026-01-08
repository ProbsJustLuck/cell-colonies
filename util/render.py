from typing import Callable
import pygame

from classes.ui.colors import TeamColor
from classes.ui.key_actions import KeyActions # type: ignore
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
from util.game_actions import create_world, toggle_color
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


def clear_icon_cache() -> None:
    global _icons, _cell_size
    _icons.clear()
    _cell_size = None


def get_icon(surf: pygame.Surface, cell_size: int, opacity: int | None = None) -> pygame.Surface:
    key = (id(surf), cell_size, opacity)

    icon = _icons.get(key)
    if icon: return icon

    icon = pygame.transform.smoothscale(surf, (cell_size, cell_size))
    if opacity:
        icon = icon.copy()
        icon.set_alpha(opacity)
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
    mouse_pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
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


    if state.last_played_game:
        button = state.special_buttons[20]
        if not state.skipped_animation:
            if not button.disabled and _button_opacity_lerp:
                button.style.opacity = int(_button_opacity_lerp.value(pygame.time.get_ticks()))
        else:
            button.style.opacity = 255
            button.style.overwrite_opacity = -1
                
        button.draw(assets.screen, mouse_pos)

        button = state.special_buttons[21]
        if not state.skipped_animation:
            if not button.disabled and _button_opacity_lerp:
                button.style.opacity = int(_button_opacity_lerp.value(pygame.time.get_ticks()))
        else:
            button.style.opacity = 255
            button.style.overwrite_opacity = -1
                
        button.draw(assets.screen, mouse_pos)
    else:
        button = state.special_buttons[19]
        if not state.skipped_animation:
            if not button.disabled and _button_opacity_lerp:
                button.style.opacity = int(_button_opacity_lerp.value(pygame.time.get_ticks()))
        else:
            button.style.opacity = 255
            button.style.overwrite_opacity = -1
                
        button.draw(assets.screen, mouse_pos)


    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None


def render_game_screen(downtime: int):
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
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Health: {cell.health: .2f} / {cell.max_health: .2f} HP ({(cell.health/cell.max_health * 100):.2f}%)", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Cells Alive: {cell.cells_amount} (peak {cell.max_cells_alive})", "#000000", 35)

            last_cell = cell.last_cell_spawned
            if last_cell:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Last Cell Spawned: {last_cell.name} - Position ({last_cell.pos.x}, {last_cell.pos.y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Last Cell Spawned: None", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Ticks Until Spawn: {max(state.spawn_rate - cell.spawn_ticks, 0)}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Ticks Since Targetted: {max(0, cell.ticks_since_targeted - 1)} (max 8)", "#000000", 35)

        elif isinstance(cell, Attacker):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Target: {cell.target.color.name} {cell.target.name} - Position ({cell.target.pos.x}, {cell.target.pos.y})", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Health: {cell.health:.2f} / 1.00 HP ({(cell.health * 100):.2f}%)    Rotated: {cell.rotated}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Direction: {cell.direction}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Ticks Since Valid Path: {cell.ticks_since_valid_path} (max 5)", "#000000", 35)

            if cell.path:
                draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Next Spot: Position ({cell.path[0].x}, {cell.path[0].y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Next Spot: None!", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 5)), f"Path Length: {len(cell.path)}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 6)), f"Damage: {cell.damage}", "#000000", 35)

        elif isinstance(cell, Rotator):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Health: {cell.health:.2f} / {cell.max_health:.2f} HP ({(cell.health/cell.max_health * 100):.2f}%)", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Stationary: {cell.stationary}", "#000000", 35)

            if cell.target:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Target: Position ({cell.target.x}, {cell.target.y})", "#000000", 35)
            else:
                draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Target: {cell.target}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 3)), f"Path Length: {len(cell.path)}", "#000000", 35)

            draw_text(Position(675, 160 + (LINE_SPACING * 4)), f"Age Max: {max(10, (round(state.world.size * 1.5) - state.world.walls_amount // 6))}", "#000000", 35)

        elif isinstance(cell, Wall):
            draw_text(Position(675, 160 + (LINE_SPACING * 0)), f"Generic wall.", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 1)), f"Entities cannot move through this.", "#000000", 35)
            draw_text(Position(675, 160 + (LINE_SPACING * 2)), f"Does not belong to a colony.", "#000000", 35)
        
        # Name
        if cell.name != "Wall":
            draw_text(Position(750, 90), f"{cell.color.name} {title} (Age {cell.age})", "#000000", 43)
            draw_text(Position(751, 90), f"{cell.color.name} {title} (Age {cell.age})", "#000000", 43)
        else:
            draw_text(Position(750, 90), f"{title} (Age {cell.age})", "#000000", 43)
            draw_text(Position(751, 90), f"{title} (Age {cell.age})", "#000000", 43)

        # Type
        draw_text(Position(751, 118), f"{cell.type} Cell - Position ({cell.pos.x}, {cell.pos.y}) [ID #{cell.id}]", "#000000", 35)

    # Typewriter
    if state.typewriter:
        state.typewriter.update(downtime)
        if state.typewriter.has_lines_left():
            state.typewriter.draw(assets.screen, (700, 430), line_spacing=20)

            if state.typewriter.finished_line():
                state.finished_timer += 1

                if state.finished_timer > 50: draw_text(Position(1070, 650), "Press C to continue!", "#7B7B7B", 25, mode="bottomright", opacity=200)
    
    pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
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

    # Typewriter stuff
    if state.typewriter and state.typewriter.id != -1:
        match state.typewriter.id:
            case 0:
                surf = pygame.Surface(state.SIM_RECT.size, pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=5)

                assets.screen.blit(surf, state.SIM_RECT.topleft)

            case 3:
                rect = pygame.Rect(235, 585, 230, 60)
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=5)

                assets.screen.blit(surf, rect.topleft)

            case 4:
                if state.pause and state.fast_forward and state.forward:
                    rect = state.pause.rect.inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

                    rect = pygame.Rect(state.forward.rect.topleft, (state.forward.rect.size[0] + state.fast_forward.rect.size[0], state.fast_forward.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)
            
            case 6:
                if state.rewind and state.fast_rewind:
                    rect = pygame.Rect(state.fast_rewind.rect.topleft, (state.rewind.rect.size[0] + state.rewind.rect.size[0], state.rewind.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 9:
                if state.rewind and state.fast_rewind:
                    rect = pygame.Rect(state.fast_rewind.rect.topleft, (state.rewind.rect.size[0] + state.rewind.rect.size[0], state.rewind.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 10:
                if state.tps_down and state.tps_button and state.tps_up:
                    rect = pygame.Rect((state.tps_down.rect.topleft[0], state.tps_down.rect.topleft[1] - 3), (state.tps_down.rect.size[0] + state.tps_button.rect.size[0] + state.tps_up.rect.size[0] + 7, state.tps_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 12:
                if state.tps_down and state.tps_up:
                    rect = pygame.Rect(state.tps_down.rect.topleft, (state.tps_down.rect.size[0], state.tps_down.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

                    rect = pygame.Rect(state.tps_up.rect.topleft, (state.tps_up.rect.size[0], state.tps_up.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 13:
                if state.tps_button:
                    rect = pygame.Rect(state.tps_button.rect.topleft, (state.tps_button.rect.size[0], state.tps_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)
                if state.tps_slider and state.show_tps:
                    rect = pygame.Rect(state.tps_slider.rect.topleft, (state.tps_slider.rect.size[0], state.tps_slider.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 14:
                if state.seed_button:
                    rect = pygame.Rect(state.seed_button.rect.topleft, (state.seed_button.rect.size[0], state.seed_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 15:
                if state.prev_render_page and state.next_render_page and state.fit_view_button:
                    rect = pygame.Rect(state.prev_render_page.rect.topleft, (state.prev_render_page.rect.size[0] + state.fit_view_button.rect.size[0] * 3 + 15 + state.next_render_page.rect.size[0], state.prev_render_page.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 16:
                if state.quit_button and state.reset_button:
                    rect = pygame.Rect(state.quit_button.rect.topleft, (state.quit_button.rect.size[0] + state.reset_button.rect.size[0] + 5, state.quit_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 17:
                if state.reset_button:
                    rect = pygame.Rect(state.reset_button.rect.topleft, (state.reset_button.rect.size[0], state.reset_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case 18:
                if state.quit_button:
                    rect = pygame.Rect(state.quit_button.rect.topleft, (state.quit_button.rect.size[0], state.quit_button.rect.size[1])).inflate(11, 11)
                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=4)

                    assets.screen.blit(surf, rect.topleft)

            case _:
                pass


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
                draw_text(Position(410, 335), f"{state.seed_string}", "#ffffff", size=50, opacity=180)
            else: 
                draw_text(Position(410, 335), f"{state.seed_string}", "#ffffff", size=50)
    
        draw_text(Position(405, 375), "ENTER to confirm, ESC to cancel", "#000000", size=30)

        mouse = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
        for i in range(19):
            menu_assets.special_buttons[i].draw(assets.screen, mouse)

        string = state.seed_string.strip("-")
        draw_text(Position(795, 370), f"{len(string)}/10", "#ffffff", size=25, mode="bottomright", opacity=160)

        if state.typing_seed and state.caret_timer / 500 <= 1:
            WIDTH = assets.big_font.size("1")[0]
            height = 2
            x = state.typing_box.x + 9 + assets.big_font.size(state.seed_string[:len(state.seed_string)])[0]
            y = state.typing_box.centery + assets.big_font.get_height() // 2
            pygame.draw.line(assets.screen, (255,255,255), (x, y), (x + WIDTH, y), height)

        assets.screen.blit(assets.COPY_ICON, (655, 475 + 10))
        assets.screen.blit(assets.PASTE_ICON, (730, 475 + 10))
        assets.screen.blit(assets.REGENERATE_ICON, (805, 483 + 10))

        if not state.special_buttons[4].label: assets.screen.blit(assets.HOMEBASE_ICON, (326, 475 + 10))
        if not state.special_buttons[5].label: assets.screen.blit(assets.HEART_ICON, (383, 492))
        if not state.special_buttons[6].label: assets.screen.blit(assets.HOURGLASS_ICON, (432, 491))
        if not state.special_buttons[7].label: assets.screen.blit(assets.WALL_ICON, (480, 490))

        if not state.special_buttons[8].label:
            # hor
            pygame.draw.line(assets.screen, "#000000", (535, 495), (563, 495), 2)
            pygame.draw.line(assets.screen, "#000000", (535, 502), (563, 502), 2)
            pygame.draw.line(assets.screen, "#000000", (535, 509), (563, 509), 2)
            pygame.draw.line(assets.screen, "#000000", (535, 516), (563, 516), 2)
            pygame.draw.line(assets.screen, "#000000", (535, 523), (563, 523), 2)

            # ver
            pygame.draw.line(assets.screen, "#000000", (535, 495), (535, 523), 2)
            pygame.draw.line(assets.screen, "#000000", (542, 495), (542, 523), 2)
            pygame.draw.line(assets.screen, "#000000", (549, 495), (549, 523), 2)
            pygame.draw.line(assets.screen, "#000000", (556, 495), (556, 523), 2)
            pygame.draw.line(assets.screen, "#000000", (563, 495), (563, 523), 2)

        if (state.old_health != state.health_multiplier) or (state.old_homebases != state.sim_homebases) or (state.old_size != state.sim_size) or (state.old_walls != state.sim_walls):
            draw_text(Position(310, 580), "*Some changes will applied on next simulation reload!", "#B80000", 23)

    if state.waiting_for_pan and state.panned and state.zoomed:
        state.waiting_for_pan = False
        state.panned = False
        state.zoomed = False

        pygame.time.set_timer(assets.ROSS_PAN_REMINDER, 0, loops=1)
        pygame.time.set_timer(assets.ROSS_PAN, 1000, loops=1)

    if state.waiting_for_pause and state.paused_forward:
        state.waiting_for_pause = False
        state.paused_forward = False

        pygame.time.set_timer(assets.ROSS_PAUSE_REMINDER, 0, loops=1)
        pygame.time.set_timer(assets.ROSS_PAUSE, 10000, loops=1)

    if state.waiting_for_rewind and state.rewinded:
        state.waiting_for_rewind = False
        state.rewinded = False

        pygame.time.set_timer(assets.ROSS_REWIND_REMINDER, 0, loops=1)
        pygame.time.set_timer(assets.ROSS_REWIND, 1000, loops=1)

    # Rewind timeline
    pygame.draw.rect(assets.screen, "#FF0000", state.TIMELINE_RECT)
    pygame.draw.line(assets.screen, "#000000", (state.TIMELINE_RECT.topleft[0], state.TIMELINE_RECT.topleft[1]), (state.TIMELINE_RECT.topright[0] - 1, state.TIMELINE_RECT.topright[1]), 2)
    pygame.draw.line(assets.screen, "#000000", (state.TIMELINE_RECT.bottomleft[0], state.TIMELINE_RECT.bottomleft[1]), (state.TIMELINE_RECT.bottomright[0] - 1, state.TIMELINE_RECT.bottomright[1]), 2)
    buttons: list[Button.Button] = []
    if state.world.history:
        for i in range(len(state.world.history)):
            x = state.TIMELINE_RECT.centerx
            y = state.TIMELINE_RECT.top + 20 + state.y_offset + 50 * i
            height = 35
            WIDTH = 25 # type: ignore
            if (state.TIMELINE_RECT.top >= y + height) or (state.TIMELINE_RECT.bottom <= y): continue

            text = create_text(f"{i + 1}", "#000000", 35)
            text_rect: pygame.rect.Rect = text.get_rect(midtop = (x, y + height // 2))
            crop = text_rect
            if state.TIMELINE_RECT.bottom < y + height:
                crop = text_rect.clip(state.TIMELINE_RECT)

                height = state.TIMELINE_RECT.bottom - y
            button = Button.Button("", (x, y), "", style=Button.ButtonStyle(width = WIDTH, height = height, border=2), id=f"{i + 1}")

            buttons.append(button)
            button.initialize()
            button.draw(assets.screen, assets.get_scale_mouse_pos(pygame.mouse.get_pos()))
            assets.screen.blit(text, text_rect, crop)



    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None


def render_options_screen() -> None:
    assets.screen.blit(assets.main_menu_background, assets.main_menu_background.get_rect(topleft = (0, 0)))

    rect = pygame.Rect(350, 150, 560, 400)
    pygame.draw.rect(assets.screen, "#9e9e9e", rect)
    pygame.draw.rect(assets.screen, "#000000", rect.inflate(3, 3), width=3, border_radius=2)

    mouse_pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
    state.special_buttons[22].draw(assets.screen, mouse_pos)

    for i in range(23, 27): state.special_buttons[i].draw(assets.screen, mouse_pos)

    match state.controls_section:
        case "controls":
            draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 40), "Change Controls", "#000000", 50, mode="center")
            draw_text(Position(rect.topleft[0] + rect.size[0] // 2 + 2, rect.top + 40), "Change Controls", "#000000", 50, mode="center")

            draw_text(Position(rect.topleft[0] + 150, rect.top + 90), "Action", "#000000", 40, mode="center")
            pygame.draw.line(assets.screen, "#000000", (rect.topleft[0] + 106, rect.top + 102), (rect.topleft[0] + 190, rect.top + 102), 2)

            draw_text(Position(rect.topleft[0] + 400, rect.top + 90), "Key", "#000000", 40, mode="center")
            pygame.draw.line(assets.screen, "#000000", (rect.topleft[0] + 368, rect.top + 102), (rect.topleft[0] + 426, rect.top + 102), 2)

            for i in range(33, 35):
                state.special_buttons[i].draw(assets.screen, mouse_pos)

            if not state.second_binding_page:
                overlay = pygame.Surface((435, 30), pygame.SRCALPHA)
                
                # Pan Alias (grab)
                if KeyActions.PAN_ALIAS in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 115))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 130), "Pan Alias (grab)", "#000000", 30, mode="center")

                # Pan Up
                if KeyActions.PAN_UP in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 155))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 170), "Pan Up (key)", "#000000", 30, mode="center")

                # Pan Down
                if KeyActions.PAN_DOWN in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 185))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 200), "Pan Down (key)", "#000000", 30, mode="center")

                # Pan Left
                if KeyActions.PAN_LEFT in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 215))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 230), "Pan Left (key)", "#000000", 30, mode="center")

                # Pan Right
                if KeyActions.PAN_RIGHT in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 245))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 260), "Pan Right (key)", "#000000", 30, mode="center")

                # Regenerate World
                if KeyActions.REGENERATE_WORLD in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 55, rect.topleft[1] + 285))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 300), "Regenerate World", "#000000", 30, mode="center")

                for i in range(27, 33):
                    state.special_buttons[i].draw(assets.screen, mouse_pos)

            else:
                overlay = pygame.Surface((475, 30), pygame.SRCALPHA)
                
                # Zoom In Alias
                if KeyActions.ZOOM_IN_ALIAS in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 115))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 130), "Zoom In Alias", "#000000", 30, mode="center")

                # Zoom Out Alias
                if KeyActions.ZOOM_OUT_ALIAS in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 145))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 160), "Zoom Out Alias", "#000000", 30, mode="center")


                # Advance/Skip Dialogue
                if KeyActions.ADVANCE_DIALOGUE in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 185))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 200), "Advance/Skip Dialogue", "#000000", 30, mode="center")

                # Pause/Unpause
                if KeyActions.PAUSE_UNPAUSE in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 215))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 230), "Pause/Unpause Sim", "#000000", 30, mode="center")


                # Step Forward
                if KeyActions.STEP_FORWARD in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 255))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 270), "Step Forward", "#000000", 30, mode="center")

                # Step Backward
                if KeyActions.STEP_BACKWARD in state.conflicts: overlay.fill((255, 0, 0, 140))
                else: overlay.fill((0, 0, 0, 72))

                assets.screen.blit(overlay, (rect.topleft[0] + 35, rect.topleft[1] + 285))
                draw_text(Position(rect.topleft[0] + 150, rect.top + 300), "Step Backward", "#000000", 30, mode="center")

                for i in range(35, 41):
                    state.special_buttons[i].draw(assets.screen, mouse_pos)

            if state.conflicts:
                draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 340), "There are some conflicts with keys!", "#AA0000", 25, mode="center")
                draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 355), "You cannot start a simulation until", "#AA0000", 25, mode="center")
                draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 370), "the conflicts are resolved.", "#AA0000", 25, mode="center")

        case "colonies":
            if not state.toggle_colonies:
                y = rect.top + 120
                x = rect.topleft[0] + 120

                for i, color in enumerate(TeamColor):
                    button = Button.Button("", (x, y), style=Button.ButtonStyle(width=32, height=32, base=f"#{color.value.primary[0]:02x}{color.value.primary[1]:02x}{color.value.primary[2]:02x}", hover=f"#{color.value.primary[0]:02x}{color.value.primary[1]:02x}{color.value.primary[2]:02x}", selected=f"#{color.value.primary[0]:02x}{color.value.primary[1]:02x}{color.value.primary[2]:02x}", selected_opacity=100), type=Button.ButtonType.TOGGLE, on_enter=lambda button, color=color: toggle_color(button, color), on_leave=lambda button, color=color: toggle_color(button, color))
                    button.initialize()

                    state.toggle_colonies.append(button)
                    x += 80
                    if x > 820:
                        x = rect.topleft[0] + 120
                        y += 100

            draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 40), "Toggle Colonies", "#000000", 50, mode="center")
            draw_text(Position(rect.topleft[0] + rect.size[0] // 2 + 2, rect.top + 40), "Toggle Colonies", "#000000", 50, mode="center")

            for button in state.toggle_colonies:
                button.draw(assets.screen, assets.get_scale_mouse_pos(pygame.mouse.get_pos()))

        case "misc":
            draw_text(Position(rect.topleft[0] + rect.size[0] // 2, rect.top + 40), "Miscellaneous", "#000000", 50, mode="center")
            draw_text(Position(rect.topleft[0] + rect.size[0] // 2 + 2, rect.top + 40), "Miscellaneous", "#000000", 50, mode="center")

            draw_text(Position(390, rect.top + 75), "Max History Length", "#000000", 35)
            draw_text(Position(665, rect.top + 75), "Max Ticks per Frame", "#000000", 35)
            
            for i in range(2): state.special_sliders[i].draw(assets.screen)

            VERTICAL_OFFSET = 10

            # Max history
            slider = state.special_sliders[0]
            slider.draw(assets.screen)
            draw_text(Position(slider.rect.bottomleft[0], slider.rect.bottomleft[1] + VERTICAL_OFFSET), "1", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.bottomright[0], slider.rect.bottomright[1] + VERTICAL_OFFSET), "100", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.centerx, slider.rect.bottom + VERTICAL_OFFSET), f"{state.max_history}", "#000000", 22, mode="center")

            # Max catchup
            slider = state.special_sliders[1]
            slider.draw(assets.screen)
            draw_text(Position(slider.rect.bottomleft[0], slider.rect.bottomleft[1] + VERTICAL_OFFSET), "1", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.bottomright[0], slider.rect.bottomright[1] + VERTICAL_OFFSET), "70", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.centerx, slider.rect.bottom + VERTICAL_OFFSET), f"{state.max_catchup}", "#000000", 22, mode="center")

            draw_text(Position(435, rect.top + 150), "Resolution", "#000000", 35)
            draw_text(Position(720, rect.top + 150), "Fullscreen", "#000000", 35)
            for i in range(41, 44): state.special_buttons[i].draw(assets.screen, mouse_pos)

            draw_text(Position(455, rect.top + 240), "Sound", "#000000", 35)
            draw_text(Position(745, rect.top + 240), "Music", "#000000", 35)

            # Sound fx
            slider = state.special_sliders[2]
            slider.draw(assets.screen)
            draw_text(Position(slider.rect.bottomleft[0], slider.rect.bottomleft[1] + VERTICAL_OFFSET), "0%", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.bottomright[0], slider.rect.bottomright[1] + VERTICAL_OFFSET), "100%", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.centerx, slider.rect.bottom + VERTICAL_OFFSET), f"{state.sound_fx_volume * 100: .0f}%", "#000000", 22, mode="center")

            # Music
            slider = state.special_sliders[3]
            slider.draw(assets.screen)
            draw_text(Position(slider.rect.bottomleft[0], slider.rect.bottomleft[1] + VERTICAL_OFFSET), "0%", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.bottomright[0], slider.rect.bottomright[1] + VERTICAL_OFFSET), "100%", "#000000", 15, mode="center")
            draw_text(Position(slider.rect.centerx, slider.rect.bottom + VERTICAL_OFFSET), f"{state.music_volume * 100: .0f}%", "#000000", 22, mode="center")


            button = state.special_buttons[46]
            if (state.seen_bob and not button.disabled) or (not state.seen_bob and button.disabled): button.toggle()
            button.draw(assets.screen, mouse_pos)

            if state.reverting:
                Button.pending_tooltip = None

                WIDTH = 400
                HEIGHT = 250
                rect = pygame.rect.Rect(assets.screen.size[0] // 2 - WIDTH // 2, assets.screen.size[1] // 2 - HEIGHT // 2, WIDTH, HEIGHT)
                pygame.draw.rect(assets.screen, "#888888", rect)
                pygame.draw.rect(assets.screen, "#000000", rect.inflate(3, 3), width=4, border_radius=2)

                old = state.skip_button_hover
                state.skip_button_hover = False
                for i in range(44, 46):
                    state.special_buttons[i].draw(assets.screen, mouse_pos)

                state.skip_button_hover = old

                text = add_outline_to_image(create_text("Keep video changes?", "#FF0000", 40), 2, "#000000")
                assets.screen.blit(text, text.get_rect(center = (assets.screen.size[0] // 2, assets.screen.size[1] // 2 - 60)))

                num = round(state.reverting_time / 1000, 1)
                text = add_outline_to_image(create_text(f"Reverting in {num:.1f}s...", "#FF0000", 30), 2, "#000000")
                assets.screen.blit(text, text.get_rect(center = (assets.screen.size[0] // 2, assets.screen.size[1] // 2 - 30)))

        case "debug":
            for i in range(47, 49):
                state.special_buttons[i].draw(assets.screen, mouse_pos)

        case _: pass


    
    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None


def render_cells_catalogue() -> None:
    assets.screen.blit(assets.main_menu_background, assets.main_menu_background.get_rect(topleft = (0, 0)))
    mouse_pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())

    WIDTH = 600
    HEIGHT = 400
    rect = pygame.rect.Rect(assets.screen.size[0] // 2 - (WIDTH // 2) + 20, assets.screen.size[1] // 2 - HEIGHT // 2, WIDTH, HEIGHT)
    pygame.draw.rect(assets.screen, "#888888", rect)
    pygame.draw.rect(assets.screen, "#000000", rect.inflate(3, 3), width=4, border_radius=2)

    for i in range(49, 54): state.special_buttons[i].draw(assets.screen, mouse_pos)

    ICON_SPACING = 63

    hb = pygame.transform.scale_by(assets.base_homebase.copy(), 0.7)
    if state.catalogue_area == "homebase":
        hb = pygame.transform.scale_by(hb, 1.1)
        hb.fill(TeamColor.BLUE.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    else:
        hb = pygame.transform.scale_by(hb, 0.9)
        hb.fill(TeamColor.GREY.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    assets.screen.blit(hb, hb.get_rect(center=(254, 229 + ICON_SPACING * 0)))

    atk = pygame.transform.scale_by(assets.base_attacker_right.copy(), 0.7)
    if state.catalogue_area == "attacker":
        atk = pygame.transform.scale_by(atk, 1.1)
        atk.fill(TeamColor.BLUE.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    else:
        atk = pygame.transform.scale_by(atk, 0.9) 
        atk.fill(TeamColor.GREY.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    assets.screen.blit(atk, atk.get_rect(center=(254, 230 + ICON_SPACING * 1)))

    rot = pygame.transform.scale_by(assets.base_rotator.copy(), 0.7)
    if state.catalogue_area == "rotator": 
        rot = pygame.transform.scale_by(rot, 1.1)
        rot.fill(TeamColor.BLUE.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    else:
        rot = pygame.transform.scale_by(rot, 0.9) 
        rot.fill(TeamColor.GREY.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
    assets.screen.blit(rot, rot.get_rect(center=(254, 230 + ICON_SPACING * 2)))

    if (not state.finished_tutorial and not state.skip_tutorial) and not state.unlocked_teleporter: assets.screen.blit(assets.locked_icon, assets.locked_icon.get_rect(center=(254, 230 + ICON_SPACING * 3)))
    elif (state.finished_tutorial or state.skip_tutorial) and not state.unlocked_teleporter:
        if state.special_buttons[53].tooltip == "Unlocked after finishing (or skipping) the tutorial!": state.special_buttons[53].tooltip = "Click to unlock!"
        icon = assets.unlocked_icon.convert_alpha()
        icon.fill((TeamColor.GREEN.value.primary[0], TeamColor.GREEN.value.primary[1], TeamColor.GREEN.value.primary[2], 0), special_flags=pygame.BLEND_RGB_ADD)

        assets.screen.blit(add_outline_to_image(icon, 1, "#000000"), icon.get_rect(center=(254, 229 + ICON_SPACING * 3)))
    elif state.unlocked_teleporter and state.catalogue_area == "teleporter":
        tele = pygame.transform.scale_by(assets.base_teleporter.copy(), 0.7)
        tele = pygame.transform.scale_by(tele, 1.1)
        tele.fill(TeamColor.BLUE.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
        assets.screen.blit(tele, tele.get_rect(center=(254, 230 + ICON_SPACING * 3)))
    elif state.unlocked_teleporter and state.catalogue_area != "teleporter":
        tele = pygame.transform.scale_by(assets.base_teleporter.copy(), 0.7)
        tele = pygame.transform.scale_by(tele, 0.9)
        tele.fill(TeamColor.GREY.value.primary, special_flags=pygame.BLEND_RGBA_MULT)
        assets.screen.blit(tele, tele.get_rect(center=(254, 230 + ICON_SPACING * 3)))

    match state.catalogue_area:
        case "homebase":
            button = state.special_buttons[50]
            pygame.draw.line(assets.screen, "#888888", (button.rect.topright[0], button.rect.topright[1] + 3,), (button.rect.bottomright[0], button.rect.bottomright[1] - 4), 7)

            icon = pygame.transform.scale_by(assets.base_homebase, 1.5)
            icon.fill(state.allowed_colonies[state.cell_color_index].value.primary, special_flags=pygame.BLEND_RGBA_MULT)
            assets.screen.blit(icon, (rect.topleft[0] + 20, rect.topleft[1] + 20))

            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 35), "Homebase", "#000000", 60)
            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 75), f"CORE Cell", "#373737", 40)

            LINE_SPACING = 30

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 0), "Base Health: 3 HP", "#000000", 40)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 1), "Base Spawning Cooldown: 3 Ticks", "#000000", 40)

            LINE_SPACING = 20 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 0), "This cell spawns other cells around it on a set timer. Cells", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 1), "spawned from a homebase also spawn on the same colony", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 2), '(or "team") as it.', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 4), 'The objective of Cell Colonies is for one homebase to be', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 5), "left standing! If one homebase remains, it's counted as", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 6), 'a win for that homebase. If none remain, the game ends', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 7), 'in a loss.', "#000000", 32)

        case "attacker":
            button = state.special_buttons[51]
            pygame.draw.line(assets.screen, "#888888", (button.rect.topright[0], button.rect.topright[1] + 3,), (button.rect.bottomright[0], button.rect.bottomright[1] - 4), 7)

            icon = pygame.transform.scale_by(assets.base_attacker_right, 1.5)
            icon.fill(state.allowed_colonies[state.cell_color_index].value.primary, special_flags=pygame.BLEND_RGBA_MULT)
            assets.screen.blit(icon, (rect.topleft[0] + 20, rect.topleft[1] + 20))

            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 35), "Attacker", "#000000", 60)
            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 75), f"HOSITLE Cell", "#373737", 40)

            LINE_SPACING = 30 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 0), "Base Health: 1 HP", "#000000", 40)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 1), "Base Damage: 0.7-1.2 DMG (randomized)", "#000000", 40)

            LINE_SPACING = 20 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 0), "When spawned, this cell will target a random enemy", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 1), "homebase, and move towards it. If it reaches its target, it", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 2), 'will deal damage to it and die.', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 4), 'When rotated by a rotator, this cell will move forwards in', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 5), "the direction its facing until it hits a wall, then pathfind", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 220 + LINE_SPACING * 6), 'as normal.', "#000000", 32)

        case "rotator":
            button = state.special_buttons[52]
            pygame.draw.line(assets.screen, "#888888", (button.rect.topright[0], button.rect.topright[1] + 3,), (button.rect.bottomright[0], button.rect.bottomright[1] - 4), 7)

            icon = pygame.transform.scale_by(assets.base_rotator, 1.5)
            icon.fill(state.allowed_colonies[state.cell_color_index].value.primary, special_flags=pygame.BLEND_RGBA_MULT)
            assets.screen.blit(icon, (rect.topleft[0] + 20, rect.topleft[1] + 20))

            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 35), "Rotator", "#000000", 60)
            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 75), f"UTILITY Cell", "#373737", 40)

            LINE_SPACING = 30 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 0), "Base Health: 2 HP", "#000000", 40)

            LINE_SPACING = 20 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 0), "When spawned, it picks an empty space within 5 squares of", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 1), "its homebase, and moves towards it. If it reaches its target,", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 2), 'it will become stationary and no longer move.', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 4), 'This cell rotates cell surrounding it, flipping their direction', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 5), 'if possible.', "#000000", 32)

        case "teleporter":
            button = state.special_buttons[53]
            pygame.draw.line(assets.screen, "#888888", (button.rect.topright[0], button.rect.topright[1] + 3,), (button.rect.bottomright[0], button.rect.bottomright[1] - 4), 7)

            icon = pygame.transform.scale_by(assets.base_teleporter, 1.5)
            icon.fill(state.allowed_colonies[state.cell_color_index].value.primary, special_flags=pygame.BLEND_RGBA_MULT)
            assets.screen.blit(icon, (rect.topleft[0] + 20, rect.topleft[1] + 20))

            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 35), "Teleporter", "#000000", 60)
            draw_text(Position(rect.topleft[0] + 130, rect.topleft[1] + 75), f"UTILITY Cell", "#373737", 40)

            LINE_SPACING = 30 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 140 + LINE_SPACING * 0), "Base Health: 2 HP", "#000000", 40)

            LINE_SPACING = 20 # type: ignore

            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 0), "When spawned, it picks an empty space anywhere on the", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 1), "map, and moves towards it. If it reaches its target, it will", "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 2), 'become stationary and no longer move.', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 4), 'This cell teleports cell ALL cells around it (including', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 5), 'homebases) not on its colony to a random empty spot', "#000000", 32)
            draw_text(Position(rect.topleft[0] + 25, rect.topleft[1] + 180 + LINE_SPACING * 6), 'on the map.', "#000000", 32)

        case _: pass


    if Button.pending_tooltip:
        Button.pending_tooltip()
        Button.pending_tooltip = None