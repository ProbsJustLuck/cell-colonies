# Guess what, ANOTHER FILE!
from typing import TYPE_CHECKING
import pygame
import random

from util import assets
from util.ui_helpers import fit_view
from util.game_states import States as state

from classes.ui.menu_area import MenuArea
from classes.world_manager import WorldManager
from classes.game_state import GameState

if TYPE_CHECKING:
    from classes.ui.button import Button


def _check_win(gamestate: GameState):
    if gamestate in [GameState.WIN, GameState.LOSS]:
        if state.forward and not state.forward.disabled: state.forward.toggle()
        if state.fast_forward and not state.fast_forward.disabled: state.fast_forward.toggle()

        state.game_end = True
        if state.pause and not state.pause.disabled: state.pause.toggle()


def create_world(seed: int | None = None):
    if not state.sim_pause: toggle_pause_simulation(None)
    state.game_end = False
    state.world = WorldManager(state.sim_size, state.sim_homebases, state.sim_walls, seed)

    if state.rewind and not state.rewind.disabled: state.rewind.toggle()
    if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()
    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()


def quit(button: "Button | None" = None):
    state.running = False


def start_game(button: "Button"):
    state.current_area = MenuArea.SIMULATION
    create_world()
    fit_view(state.sim_size)

    state.target_tps = 2.0


def go_to_main_menu(button: "Button"):
    state.current_area = MenuArea.MAIN_MENU

    state.game_end = False
    if state.show_tps and state.tps_button: state.tps_button.click()
    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.pause and not state.sim_pause: state.pause.click()
    state.panning = False


def go_to_options(button: "Button"):
    state.current_area = MenuArea.OPTIONS


def go_to_infopedia(button: "Button"):
    state.current_area = MenuArea.INFO


def go_to_credits(button: "Button"):
    state.current_area = MenuArea.CREDITS


def go_to_debug(button: "Button"):
    state.current_area = MenuArea.DEBUG


def toggle_pause_simulation(button: "Button | None"):
    if (state.game_end and state.sim_pause) or not state.pause: return
    state.sim_pause = not state.sim_pause

    if state.sim_pause and state.world:
        state.pause.label = ">"
        state.pause.style.scale = 2

        if state.rewind and state.rewind.disabled and state.world.get_snapshot(1): state.rewind.toggle()
        if state.fast_rewind and state.fast_rewind.disabled and state.world.get_snapshot(2): state.fast_rewind.toggle()
        if not state.game_end and state.forward and state.forward.disabled: state.forward.toggle()
        if not state.game_end and state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()
    else:
        state.pause.label = "||"
        state.pause.style.scale = 1.4

        if state.rewind and not state.rewind.disabled: state.rewind.toggle()
        if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()
        if state.forward and not state.forward.disabled: state.forward.toggle()
        if state.fast_forward and not state.fast_forward.disabled: state.fast_forward.toggle()
    state.pause.initialize()


def forward(button: "Button"):
    if not state.world: return
    _check_win(state.world.tick())

    if state.rewind and state.rewind.disabled: state.rewind.toggle()
    if state.world.get_snapshot(2) and state.fast_rewind and state.fast_rewind.disabled: state.fast_rewind.toggle()


def fast_forward(button: "Button"):
    if not state.world: return
    _check_win(state.world.tick())
    if not state.game_end: _check_win(state.world.tick())

    if state.rewind and state.rewind.disabled: state.rewind.toggle()
    if state.fast_rewind and state.fast_rewind.disabled and state.world.get_snapshot(2): state.fast_rewind.toggle()


def rewind(button: "Button"):
    if not state.world: return
    state.game_end = False

    selected_id = state.selected_cell.id if state.selected_cell else None
    state.world.restore_snapshot(1)
    state.selected_cell = None

    if selected_id is not None: # have to do this cuz 0 would be skipped
        for row in state.world.map:
            for cell in row:
                if cell and cell.id == selected_id:
                    state.selected_cell = cell
                    break
            if state.selected_cell:
                break
                

    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1):
        if state.rewind and not state.rewind.disabled: state.rewind.toggle()
        if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def fast_rewind(button: "Button"):
    if not state.world: return
    state.game_end = False

    selected_id = state.selected_cell.id if state.selected_cell else None
    state.world.restore_snapshot(1)
    state.selected_cell = None

    if selected_id is not None: # have to do this cuz 0 would be skipped
        for row in state.world.map:
            for cell in row:
                if cell and cell.id == selected_id:
                    state.selected_cell = cell
                    break
            if state.selected_cell:
                break


    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1) and state.rewind and not state.rewind.disabled: state.rewind.toggle()
    if not state.world.get_snapshot(2) and state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def show_tps(button: "Button"): state.show_tps = True


def hide_tps(button: "Button"): state.show_tps = False


def set_tps(value: float): 
    state.target_tps = round(value, 1)

    if state.target_tps >= 20.0 and state.tps_up: state.tps_up.toggle()
    elif state.target_tps <= 0.1 and state.tps_down: state.tps_down.toggle()


def tps_up(button: "Button"):
    assert state.tps_slider and state.tps_button
    state.target_tps = round(state.target_tps + 0.1, 1)
    
    state.tps_slider.value = state.target_tps

    if state.tps_down and state.tps_down.disabled: state.tps_down.toggle()
    if state.target_tps >= 20.0 and not button.disabled: button.toggle()

    state.tps_button.label = f"{state.target_tps}"
    state.tps_button.initialize()
    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

    state.tps_change = 1


def tps_down(button: "Button"):
    assert state.tps_slider and state.tps_button
    state.target_tps = round(state.target_tps - 0.1, 1)

    state.tps_slider.value = state.target_tps

    if state.tps_up and state.tps_up.disabled: state.tps_up.toggle()
    if state.target_tps <= 0.1 and not button.disabled: button.toggle()

    state.tps_button.label = f"{state.target_tps}"
    state.tps_button.initialize()
    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

    state.tps_change = 1


def next_render_page(button: "Button"):
    state.second_render_page = not state.second_render_page
    if state.prev_render_page: state.prev_render_page.disabled = not state.prev_render_page.disabled
    if state.next_render_page: state.next_render_page.disabled = not state.next_render_page.disabled


def toggle_walls(button: "Button"):
    if "Wall" not in state.disabled_cells: 
        state.disabled_cells.append("Wall")
        if getattr(state.selected_cell, "name", "") == "Wall":
            state.selected_cell = None
            state.selected_id = None
    else: state.disabled_cells.remove("Wall")


def toggle_homebases(button: "Button"):
    if "Homebase" not in state.disabled_cells: 
        state.disabled_cells.append("Homebase")
        if getattr(state.selected_cell, "name", "") == "Homebase":
            state.selected_cell = None
            state.selected_id = None
    else: state.disabled_cells.remove("Homebase")


def toggle_rotators(button: "Button"):
    if "Rotator" not in state.disabled_cells: 
        state.disabled_cells.append("Rotator")
        if getattr(state.selected_cell, "name", "") == "Rotator":
            state.selected_cell = None
            state.selected_id = None
    else: state.disabled_cells.remove("Rotator")


def toggle_attackers(button: "Button"):
    if "Attacker" not in state.disabled_cells: 
        state.disabled_cells.append("Attacker")
        if getattr(state.selected_cell, "name", "") == "Attacker":
            state.selected_cell = None
            state.selected_id = None
    else: state.disabled_cells.remove("Attacker")


def toggle_gridlines(button: "Button"):
    if "Gridlines" not in state.disabled_cells: state.disabled_cells.append("Gridlines")
    else: state.disabled_cells.remove("Gridlines")


def fit_view_button(button: "Button"):
    assert state.world
    fit_view(state.world.size)


def toggle_change_seed(button: "Button"):
    state.changing_seed = not state.changing_seed
    
    if state.changing_seed and not state.special_buttons[0].disabled: state.special_buttons[0].toggle()


def change_seed(button: "Button"):
    create_world(seed=int(state.seed_string))
    state.seed_string = ""
    if not state.special_buttons[0].disabled: state.special_buttons[0].toggle()


def copy_seed(button: "Button"):
    assert state.world
    pygame.scrap.put_text(str(state.world.seed))


def paste_seed(button: "Button"):
    text = pygame.scrap.get_text()
    if text:
        seed = text.strip()
        if seed.startswith("-"):
            if seed[1:].isdigit(): 
                state.seed_string = str(seed)
                state.typing_seed = True
        else:
            if seed.isdigit(): 
                state.seed_string = str(seed)
                state.typing_seed = True
        if ((state.seed_string.startswith("-") and len(state.seed_string) > 1) or (not state.seed_string.startswith("-") and len(state.seed_string) > 0)) and state.special_buttons[0].disabled: state.special_buttons[0].toggle()


def regenerate_world(button: "Button | None"):
    state.seed_string = str(random.randrange(2**32))
    if ((state.seed_string.startswith("-") and len(state.seed_string) > 1) or (not state.seed_string.startswith("-") and len(state.seed_string) > 0)) and state.special_buttons[0].disabled: state.special_buttons[0].toggle()