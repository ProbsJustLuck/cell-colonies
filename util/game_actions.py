# Guess what, ANOTHER FILE!
import copy
import math
from typing import TYPE_CHECKING, Any
import pygame
import random

from classes.ui.colors import TeamColor
from classes.ui.typewriter import Typewriter
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


def check_walls():
    if state.sim_walls > state.sim_size**2 - state.sim_homebases:
        state.sim_walls = max(min(state.sim_size**2 - state.sim_homebases, state.sim_walls), 0)

        state.special_buttons[7].label = f"{state.sim_walls}"
        state.special_buttons[7].initialize()
        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 1000, loops=1)


    button = state.special_buttons[15]
    if state.sim_walls >= state.sim_size**2 - state.sim_homebases and not button.disabled: button.toggle()
    if state.sim_walls < state.sim_size**2 - state.sim_homebases and button.disabled: button.toggle()

    button = state.special_buttons[16]
    if state.sim_walls <= 0 and not button.disabled: button.toggle()
    if state.sim_walls > 0 and button.disabled: button.toggle()


def check_homebases():
    _team_color_length = len(list(TeamColor))
    if state.sim_homebases > min(state.sim_size**2 - state.sim_walls, _team_color_length):
        state.sim_homebases = max(min(state.sim_size**2 - state.sim_walls, state.sim_homebases, _team_color_length), 2)

        state.special_buttons[4].label = f"{state.sim_homebases}"
        state.special_buttons[4].initialize()
        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 1000, loops=1)

    button = state.special_buttons[9]
    if (state.sim_homebases >= state.sim_size**2 - state.sim_walls or state.sim_homebases >= _team_color_length) and not button.disabled: button.toggle()
    if state.sim_homebases < state.sim_size**2 - state.sim_walls and state.sim_homebases < _team_color_length and button.disabled: button.toggle()

    button = state.special_buttons[10]
    if state.sim_homebases <= 2 and not button.disabled: button.toggle()
    if state.sim_homebases > 2 and button.disabled: button.toggle()


def _check_size():
    if state.sim_size < math.ceil(math.sqrt(state.sim_walls + state.sim_homebases)):
        state.sim_size = min(max(math.ceil(math.sqrt(state.sim_walls + state.sim_homebases)), state.sim_size, 2), 100)

        state.special_buttons[8].label = f"{state.sim_size}"
        state.special_buttons[8].initialize()
        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 1000, loops=1)


    button = state.special_buttons[17]
    if state.sim_size >= 100 and not button.disabled: button.toggle()
    if state.sim_size < 100 and button.disabled: button.toggle()

    button = state.special_buttons[18]
    if state.sim_size <= 2 and not button.disabled: button.toggle()
    if state.sim_size > 2 and button.disabled: button.toggle()


def _save_game():
    if not state.world: return

    state.last_played_game = {
        "world": copy.deepcopy(state.world),
        "rng": copy.deepcopy(state.world.rng.getstate())
    }


def create_world(seed: int | None = None, world: WorldManager | None = None, rng: tuple[Any, ...] | None = None):
    if not state.sim_pause: toggle_pause_simulation(None)
    state.game_end = False

    if not world:
        state.world = WorldManager(state.sim_size, state.sim_homebases, state.sim_walls, seed)
    else:
        state.world = world

    

    if rng: state.world.rng.setstate(rng)

    if state.rewind and not state.rewind.disabled: state.rewind.toggle()
    if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()
    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    state.old_size = state.sim_size
    state.old_homebases = state.sim_homebases
    state.old_walls = state.sim_walls
    state.old_health = state.health_multiplier


def load_world(button: "Button"):
    if state.last_played_game:
        assert isinstance(state.last_played_game["world"], WorldManager)
        assert isinstance(state.last_played_game["rng"], tuple)

        start_game(button=None, world = state.last_played_game["world"], rng=state.last_played_game["rng"])
        state.last_played_game = None


def quit(button: "Button | None" = None):
    state.running = False


def start_game(button: "Button | None", world: WorldManager | None = None, rng: tuple[Any, ...] | None = None):
    state.current_area = MenuArea.SIMULATION
    create_world(world=world, rng=rng)
    fit_view(state.sim_size)

    if not state.typewriter: state.typewriter = Typewriter(30, speed=20)

    if not state.seen_bob: pygame.time.set_timer(assets.ROSS_CALL, 1000, loops=1)

    state.target_tps = 2.0


def go_to_main_menu(button: "Button"):
    state.current_area = MenuArea.MAIN_MENU

    _save_game()

    state.game_end = False
    if state.show_tps and state.tps_button: state.tps_button.click()
    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.pause and not state.sim_pause: state.pause.click()

    # Flags off (safety)
    state.panning = False
    state.changing_seed = False
    state.typing_seed = False
    state.seed_string = ""
    state.selected_cell = None
    state.selected_id = None
    state.second_render_page = False
    state.hovered_pos = None

    pygame.time.set_timer(assets.ROSS_CALL, 0)


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
    state.seed_string = ""
    
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
        else:
            if seed.isdigit(): 
                state.seed_string = str(seed)
        if ((state.seed_string.startswith("-") and len(state.seed_string) > 1) or (not state.seed_string.startswith("-") and len(state.seed_string) > 0)) and state.special_buttons[0].disabled: state.special_buttons[0].toggle()


def regenerate_world(button: "Button | None"):
    state.seed_string = str(random.randrange(2**32))
    if ((state.seed_string.startswith("-") and len(state.seed_string) > 1) or (not state.seed_string.startswith("-") and len(state.seed_string) > 0)) and state.special_buttons[0].disabled: state.special_buttons[0].toggle()


def increase_homebases(button: "Button"):
    _team_color_length = len(list(TeamColor))
    state.sim_homebases = min(_team_color_length, state.sim_homebases + 1, state.sim_size**2 - state.sim_walls)
    if state.sim_homebases >= min(_team_color_length, state.sim_size**2 - state.sim_walls): button.toggle()

    if state.special_buttons[10].disabled: state.special_buttons[10].toggle()
    check_walls()

    state.special_buttons[4].label = f"{state.sim_homebases}"
    state.special_buttons[4].initialize()
    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 1000, loops=1)

    state.homebase_change = 1


def decrease_homebases(button: "Button"):
    state.sim_homebases = max(2, state.sim_homebases - 1)
    if state.sim_homebases <= 2: button.toggle()

    if state.special_buttons[9].disabled: state.special_buttons[9].toggle()
    check_walls()

    state.special_buttons[4].label = f"{state.sim_homebases}"
    state.special_buttons[4].initialize()
    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 1000, loops=1)

    state.homebase_change = 1


def increase_health(button: "Button"):
    state.health_multiplier = round(min(5.0, state.health_multiplier + 0.1), 1)
    if state.health_multiplier >= 5.0: button.toggle()

    if state.special_buttons[12].disabled: state.special_buttons[12].toggle()

    state.special_buttons[5].label = f"x{state.health_multiplier}"
    state.special_buttons[5].initialize()
    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 1000, loops=1)

    state.homebase_change = 1


def decrease_health(button: "Button"):
    state.health_multiplier = round(max(0.1, state.health_multiplier - 0.1), 1)
    if state.health_multiplier <= 0.1: button.toggle()

    if state.special_buttons[11].disabled: state.special_buttons[11].toggle()

    state.special_buttons[5].label = f"x{state.health_multiplier}"
    state.special_buttons[5].initialize()
    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 1000, loops=1)

    state.health_change = 1


def increase_spawn_rate(button: "Button"):
    state.spawn_rate = min(8, state.spawn_rate + 1)
    if state.spawn_rate >= 8: button.toggle()

    if state.special_buttons[14].disabled: state.special_buttons[14].toggle()

    state.special_buttons[6].label = f"{state.spawn_rate}"
    state.special_buttons[6].initialize()
    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 1000, loops=1)

    state.spawn_change = 1


def decrease_spawn_rate(button: "Button"):
    state.spawn_rate = max(1, state.spawn_rate - 1)
    if state.spawn_rate <= 1: button.toggle()

    if state.special_buttons[13].disabled: state.special_buttons[13].toggle()

    state.special_buttons[6].label = f"{state.spawn_rate}"
    state.special_buttons[6].initialize()
    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 1000, loops=1)

    state.spawn_change = 1


def increase_walls(button: "Button"):
    state.sim_walls = min(state.sim_size**2 - state.sim_homebases, state.sim_walls + 1)
    if state.sim_walls >= state.sim_size**2 - state.sim_homebases: button.toggle()

    if state.special_buttons[16].disabled: state.special_buttons[16].toggle()
    check_homebases()

    state.special_buttons[7].label = f"{state.sim_walls}"
    state.special_buttons[7].initialize()
    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 1000, loops=1)

    state.wall_change = 1


def decrease_walls(button: "Button"):
    state.sim_walls = min(state.sim_size**2 - state.sim_homebases, state.sim_walls - 1)
    if state.sim_walls <= 0: button.toggle()

    if state.special_buttons[15].disabled: state.special_buttons[15].toggle()
    check_homebases()

    state.special_buttons[7].label = f"{state.sim_walls}"
    state.special_buttons[7].initialize()
    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 1000, loops=1)

    state.wall_change = 1


def increase_sim_size(button: "Button"):
    state.sim_size = min(100, state.sim_size + 1)
    if state.sim_size >= 100: button.toggle()

    if state.special_buttons[18].disabled: state.special_buttons[18].toggle()
    check_walls()
    check_homebases()

    state.special_buttons[8].label = f"{state.sim_size}"
    state.special_buttons[8].initialize()
    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 1000, loops=1)

    state.size_change = 1


def decrease_sim_size(button: "Button"):
    state.sim_size = max(2, state.sim_size - 1)
    if state.sim_size <= 2: button.toggle()

    if state.special_buttons[17].disabled: state.special_buttons[17].toggle()
    check_walls()
    check_homebases()

    state.special_buttons[8].label = f"{state.sim_size}"
    state.special_buttons[8].initialize()
    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 1000, loops=1)

    state.size_change = 1


def reset_homebases(button: "Button"):
    state.sim_homebases = 2
    _check_size()
    check_walls()
    check_homebases()


def reset_health(button: "Button"): state.health_multiplier = 1.0


def reset_spawn_ticks(button: "Button"): state.spawn_rate = 3


def reset_walls(button: "Button"): 
    state.sim_walls = 40
    _check_size()
    check_homebases()
    check_walls()


def reset_size(button: "Button"):
    state.sim_size = 20
    check_walls()
    check_homebases()