# Guess what, ANOTHER FILE!
import copy
import math
from typing import TYPE_CHECKING, Any
import pygame
import os
import random

from classes.ui.colors import TeamColor
from classes.ui.key_actions import KeyActions
from classes.ui.typewriter import Message, Typewriter
from constants import Constants
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
    _team_color_length = len(state.allowed_colonies)
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

    check_homebases()
    check_walls()
    _check_size()

    if not world:
        state.world = WorldManager(state.sim_size, state.sim_homebases, state.sim_walls, seed)
    else:
        state.world = world
    from util.render import clear_icon_cache # i didnt wanna make another file
    clear_icon_cache()

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

    state.selected_cell = None

    state.unique_seeds.add(state.world.seed)


def load_world(button: "Button"):
    if state.last_played_game:
        assert isinstance(state.last_played_game["world"], WorldManager)
        assert isinstance(state.last_played_game["rng"], tuple)

        start_game(button=None, world = state.last_played_game["world"], rng=state.last_played_game["rng"])
        state.last_played_game = None
        if state.world and len(state.world.homebases) <= 1: state.game_end = True

        if (state.rewind and state.world and not state.world.get_snapshot(1)[0] and not state.rewind.disabled) or (state.rewind and state.world and state.world.get_snapshot(1)[0] and state.rewind.disabled): state.rewind.toggle()

        if (state.fast_rewind and state.world and not state.world.get_snapshot(2)[0] and not state.fast_rewind.disabled) or (state.fast_rewind and state.world and state.world.get_snapshot(2)[0] and state.fast_rewind.disabled): state.fast_rewind.toggle()

        if (state.pause and state.pause.disabled and not state.game_end) or (state.pause and not state.pause.disabled and state.game_end): state.pause.toggle()

        if (state.forward and state.forward.disabled and not state.game_end) or (state.forward and not state.forward.disabled and state.game_end): state.forward.toggle()

        if (state.fast_forward and state.fast_forward.disabled and not state.game_end) or (state.fast_forward and not state.fast_forward.disabled and state.game_end): state.fast_forward.toggle()


def quit(button: "Button | None" = None):
    state.running = False


def start_game(button: "Button | None", world: WorldManager | None = None, rng: tuple[Any, ...] | None = None):
    state.current_area = MenuArea.SIMULATION
    create_world(world=world, rng=rng)
    fit_view(state.sim_size)

    if not state.typewriter: state.typewriter = Typewriter(30, speed=20)

    if not state.seen_bob and not state.skip_tutorial: pygame.time.set_timer(assets.ROSS_CALL, 1000, loops=1)


def go_to_main_menu(button: "Button"):
    state.current_area = MenuArea.MAIN_MENU

    _save_game()

    state.game_end = False
    if state.show_tps and state.tps_button: state.tps_button.click()
    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.pause and not state.sim_pause: state.pause.click()

    assert state.typewriter

    if not state.typewriter.not_rude() and not state.finished_tutorial and not state.skip_tutorial:
        if state.typewriter.has_lines_left():
            state.typewriter.reset_to_queue()

            state.typewriter.prepend(Message(["Hey!", "It's rude to randomly quit out when", "I'm trying to teach you the game...", "", "Anyways..."], -2))
        else:
            state.typewriter.queue(Message(["Hey!", "It's rude to randomly quit out when", "I'm trying to teach you the game..."], -2))
    elif not state.finished_tutorial and (not state.skip_tutorial or state.seen_bob) and not state.skip_tutorial:
        state.typewriter.reset_progress()

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


def return_to_main_menu(button: "Button") -> None:
    state.current_area = MenuArea.MAIN_MENU

    if (state.conflicts and state.last_played_game and (not state.special_buttons[20].disabled and not state.special_buttons[21].disabled)) or (not state.conflicts and state.last_played_game and (state.special_buttons[20].disabled and state.special_buttons[21].disabled)):
        state.special_buttons[20].toggle()
        state.special_buttons[21].toggle()

    if (state.conflicts and not state.last_played_game and not state.special_buttons[19].disabled) or (not state.conflicts and not state.last_played_game and state.special_buttons[19].disabled): state.special_buttons[19].toggle()


def go_to_options(button: "Button"):
    if state.controls_section != "controls": change_option_section(state.special_buttons[23])
    state.current_area = MenuArea.OPTIONS


def go_to_infopedia(button: "Button"):
    match state.catalogue_area:
        case "homebase": pass

        case "attacker":
            btn = state.special_buttons[51]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "rotator":
            btn = state.special_buttons[52]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "teleporter":
            btn = state.special_buttons[53]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "annihilator":
            btn = state.special_buttons[58]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case _: # default/placeholder
            btn = state.special_buttons[49]
            if btn.disabled: btn.toggle()
    
    btn = state.special_buttons[50]
    if not btn.disabled: btn.toggle()

    state.catalogue_area = "homebase"

    state.current_area = MenuArea.CATALOGUE


def go_to_credits(button: "Button"):
    state.current_area = MenuArea.CREDITS


def go_to_debug(button: "Button"):
    state.current_area = MenuArea.DEBUG


def toggle_pause_simulation(button: "Button | None"):
    if (state.game_end and state.sim_pause) or not state.pause: return
    state.sim_pause = not state.sim_pause

    if button and state.waiting_for_pause and not state.paused_forward: state.paused_forward = True

    if state.sim_pause and state.world:
        state.pause.label = ">"
        state.pause.style.scale = 2

        if state.rewind and state.rewind.disabled and state.world.get_snapshot(1)[0]: state.rewind.toggle()
        if state.fast_rewind and state.fast_rewind.disabled and state.world.get_snapshot(2)[0]: state.fast_rewind.toggle()
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


def forward(button: "Button | None"):
    if not state.world: return
    _check_win(state.world.tick())

    if state.waiting_for_pause and not state.paused_forward: state.paused_forward = True

    if state.rewind and state.rewind.disabled: state.rewind.toggle()
    if state.world.get_snapshot(2)[0] and state.fast_rewind and state.fast_rewind.disabled: state.fast_rewind.toggle()


def fast_forward(button: "Button | None"):
    if not state.world: return
    _check_win(state.world.tick())
    if not state.game_end: _check_win(state.world.tick())

    if state.waiting_for_pause and not state.paused_forward: state.paused_forward = True

    if state.rewind and state.rewind.disabled: state.rewind.toggle()
    if state.fast_rewind and state.fast_rewind.disabled and state.world.get_snapshot(2)[0]: state.fast_rewind.toggle()


def rewind(button: "Button | None"):
    if not state.world: return
    state.game_end = False

    selected_id = state.selected_cell.id if state.selected_cell else None
    state.world.restore_snapshot(1)
    from util.render import clear_icon_cache
    clear_icon_cache()
    state.selected_cell = None

    if selected_id is not None: # have to do this cuz 0 would be skipped
        for row in state.world.map:
            for cell in row:
                if cell and cell.id == selected_id:
                    state.selected_cell = cell
                    break
            if state.selected_cell:
                break


    if state.waiting_for_rewind and not state.rewinded: state.rewinded = True
                

    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1)[0]:
        if state.rewind and not state.rewind.disabled: state.rewind.toggle()
        if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def fast_rewind(button: "Button | None"):
    if not state.world: return
    state.game_end = False

    selected_id = state.selected_cell.id if state.selected_cell else None
    state.world.restore_snapshot(2)
    from util.render import clear_icon_cache
    clear_icon_cache()
    state.selected_cell = None

    if selected_id is not None: # have to do this cuz 0 would be skipped
        for row in state.world.map:
            for cell in row:
                if cell and cell.id == selected_id:
                    state.selected_cell = cell
                    break
            if state.selected_cell:
                break


    if state.waiting_for_rewind and not state.rewinded: state.rewinded = True


    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1)[0] and state.rewind and not state.rewind.disabled: state.rewind.toggle()
    if not state.world.get_snapshot(2)[0] and state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def show_tps(button: "Button"): state.show_tps = True


def hide_tps(button: "Button"): state.show_tps = False


def set_tps(value: float): 
    state.target_tps = round(value, 1)

    if state.tps_slider: state.tps_slider.value = state.target_tps

    if state.target_tps >= 40.0 and state.tps_up and not state.tps_up.disabled: state.tps_up.toggle()
    elif state.target_tps < 40.0 and state.tps_up and state.tps_up.disabled: state.tps_up.toggle()

    if state.target_tps <= 0.1 and state.tps_down and not state.tps_down.disabled: state.tps_down.toggle()
    elif state.target_tps > 0.1 and state.tps_down and state.tps_down.disabled: state.tps_down.toggle()


def tps_up(button: "Button"):
    assert state.tps_slider and state.tps_button
    state.target_tps = round(state.target_tps + 0.1, 1)
    
    state.tps_slider.value = state.target_tps

    if state.tps_down and state.tps_down.disabled: state.tps_down.toggle()
    if state.target_tps >= 40.0 and not button.disabled: button.toggle()

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
    _team_color_length = len(state.allowed_colonies)
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


def change_option_section(button: "Button"):
    match state.controls_section:
        case "controls":
            b = state.special_buttons[23]
            b.clicked = False
            b.toggle()

        case "colonies": 
            b = state.special_buttons[24]
            b.clicked = False
            b.toggle()
        case "misc": 
            b = state.special_buttons[25]
            b.clicked = False
            b.toggle()
        case "debug": 
            b = state.special_buttons[26]
            b.clicked = False
            b.toggle()
        case _: pass

    match button.id:
        case "23": state.controls_section = "controls"
        case "24": state.controls_section = "colonies"
        case "25": state.controls_section = "misc"
        case "26": state.controls_section = "debug"
        case _: pass
    button.toggle()


def toggle_second_bindings(button: "Button"):
    state.second_binding_page = not state.second_binding_page

    state.special_buttons[33].toggle()
    state.special_buttons[34].toggle()


def change_binding(button: "Button"):
    if type(button.id) is KeyActions:
        state.rebinding = (button.id, button)

    button.label = "Press a key..."
    button.initialize()


def reset_binding(button: "Button"):
    if type(button.id) is KeyActions:
        state.bindings[button.id] = Constants.DEFAULT_BINDINGS[button.id]

        button.label = f"{pygame.key.name(state.bindings[button.id]).upper()}"
        button.initialize()

        if button.clicked: button.clicked = False

        # get rid of conflict if there isn't any
        state.conflicts.clear()
        items = list(state.bindings.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][1] == items[j][1]:
                    if items[i][0] not in state.conflicts: state.conflicts.append(items[i][0])
                    if items[j][0] not in state.conflicts: state.conflicts.append(items[j][0])


        if state.rebinding and state.rebinding[1] == button: state.rebinding = None


def change_binding_event(event: pygame.Event):
    if state.rebinding is None: return

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        state.rebinding[1].label = f"{pygame.key.name(state.bindings[state.rebinding[0]]).upper()}"
        state.rebinding[1].initialize()

        state.rebinding[1].clicked = False

        state.rebinding = None
        return

    elif event.type == pygame.KEYDOWN:
        state.bindings[state.rebinding[0]] = event.key

        # get rid of conflict if there isn't any
        state.conflicts.clear()
        items = list(state.bindings.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][1] == items[j][1]:
                    if items[i][0] not in state.conflicts: state.conflicts.append(items[i][0])
                    if items[j][0] not in state.conflicts: state.conflicts.append(items[j][0])

        state.rebinding[1].label = f"{pygame.key.name(state.bindings[state.rebinding[0]]).upper()}"
        state.rebinding[1].initialize()
        state.rebinding[1].clicked = False
        state.rebinding = None

    elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEWHEEL:
        state.rebinding[1].label = f"{pygame.key.name(state.bindings[state.rebinding[0]]).upper()}"
        state.rebinding[1].initialize()

        state.rebinding[1].clicked = False

        state.rebinding = None
        return
    

def toggle_color(button: "Button", color: TeamColor) -> None:
    if color in state.allowed_colonies:
        if len(state.allowed_colonies) < 3: 
            button.clicked = False
            return

        state.allowed_colonies.remove(color)

    else: state.allowed_colonies.append(color)


def _check_res() -> bool:
    if state.option_res == state.current_res and state.option_fullscreen == state.current_fullscreen:
        return True
    return False


def create_video(fullscreen: bool, resolution: int) -> None:
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    if not fullscreen: assets.display_screen = pygame.display.set_mode(assets.RESOLUTIONS[resolution], display=Constants.DISPLAY_MONITOR)
    else: assets.display_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)    


def increase_resolution(button: "Button") -> None:
    if state.option_res >= len(assets.RESOLUTIONS) - 1: return
    state.option_res = min(state.option_res + 1, len(assets.RESOLUTIONS) - 1)

    if state.option_res == state.current_res: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}"
    else: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}*"
    button.initialize()

    btn = state.special_buttons[43]
    if (_check_res() and not btn.disabled) or (not _check_res() and btn.disabled): btn.toggle()


def decrease_resolution(button: "Button") -> None:
    if state.option_res == 0: return
    state.option_res = max(state.option_res - 1, 0)

    if state.option_res == state.current_res: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}"
    else: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}*"
    button.initialize()

    btn = state.special_buttons[43]
    if (_check_res() and not btn.disabled) or (not _check_res() and btn.disabled): btn.toggle()


def toggle_fullscreen(button: "Button") -> None:
    state.option_fullscreen = not state.option_fullscreen

    if state.option_fullscreen == state.current_fullscreen: button.label = f"{'On' if state.option_fullscreen else 'Off'}"
    else: button.label = f"{'On' if state.option_fullscreen else 'Off'}*"
    button.initialize()

    btn = state.special_buttons[41]
    if (state.option_fullscreen and not btn.disabled) or (not state.option_fullscreen and btn.disabled): btn.toggle()

    btn = state.special_buttons[43]
    if (_check_res() and not btn.disabled) or (not _check_res() and btn.disabled): btn.toggle()


def apply_video_changes(button: "Button"):
    create_video(state.option_fullscreen, state.option_res)

    state.current_fullscreen = state.option_fullscreen
    state.current_res = state.option_res

    state.reverting = True
    state.skip_button_hover = True
    state.reverting_time = 10000

    pygame.time.set_timer(assets.REVERT_VIDEO_CHANGES, 0)
    pygame.time.set_timer(assets.REVERT_VIDEO_CHANGES, 10000, loops=1)


def revert_video_changes() -> None:
    create_video(state.revert_fullscreen, state.revert_res)

    state.reverting = False
    state.reverting_time = 0
    state.skip_button_hover = False
    pygame.time.set_timer(assets.REVERT_VIDEO_CHANGES, 0)

    state.current_res = state.revert_res
    state.option_res = state.revert_res

    button = state.special_buttons[41]
    if state.option_res == state.current_res: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}"
    else: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}*"
    button.initialize()

    state.current_fullscreen = state.revert_fullscreen
    state.option_fullscreen = state.revert_fullscreen

    button = state.special_buttons[42]
    if state.option_fullscreen == state.current_fullscreen: button.label = f"{'On' if state.option_fullscreen else 'Off'}"
    else: button.label = f"{'On' if state.option_fullscreen else 'Off'}*"
    button.initialize()

    btn = state.special_buttons[41]
    if (state.option_fullscreen and not btn.disabled) or (not state.option_fullscreen and btn.disabled): btn.toggle()

    button = state.special_buttons[43]
    if not button.disabled: button.toggle()


def keep_video_changes() -> None:
    state.reverting = False
    state.reverting_time = 0
    state.skip_button_hover = False
    pygame.time.set_timer(assets.REVERT_VIDEO_CHANGES, 0)

    state.revert_res = state.current_res

    button = state.special_buttons[41]
    if state.option_res == state.current_res: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}"
    else: button.label = f"{assets.RESOLUTIONS[state.option_res][0]}x{assets.RESOLUTIONS[state.option_res][1]}*"
    button.initialize()

    state.revert_fullscreen = state.current_fullscreen

    button = state.special_buttons[42]
    if state.option_fullscreen == state.current_fullscreen: button.label = f"{'On' if state.option_fullscreen else 'Off'}"
    else: button.label = f"{'On' if state.option_fullscreen else 'Off'}*"
    button.initialize()

    btn = state.special_buttons[41]
    if (state.option_fullscreen and not btn.disabled) or (not state.option_fullscreen and btn.disabled): btn.toggle()

    button = state.special_buttons[43]
    if not button.disabled: button.toggle()


def set_max_history(value: float): state.snapshot_frequency = round(value)


def set_max_catchup(value: float): state.max_catchup = round(value)


def set_sound_fx(value: float): state.sound_fx_volume = round(value, 2)


def set_music(value: float): state.music_volume = round(value, 2)


def toggle_skip(button: "Button"): state.skip_tutorial = not state.skip_tutorial


def toggle_paths(button: "Button"): state.show_paths = not state.show_paths


def toggle_target_lines(button: "Button"): state.show_target_lines = not state.show_target_lines


def change_catalogue_area(button: "Button"): 
    if button.id and button.id == "teleporter":
        if not state.finished_tutorial and not state.skip_tutorial and not state.unlocked_teleporter:
            button.clicked = False
            return
        elif (state.finished_tutorial or state.skip_tutorial) and not state.unlocked_teleporter:
            state.special_buttons[53].tooltip = ""
            state.special_buttons[58].tooltip = "Unlocked after unlocking Teleporter and visiting 10 unique seeds!"
            state.unlocked_teleporter = True

            from classes.teleporter import Teleporter
            from util import cell_registry

            cell_registry.spawnable_cells.append(Teleporter)
            cell_registry.spawn_rates.append(15)

            button.clicked = False
            return
    
    elif button.id and button.id == "annihilator":
        if (not state.unlocked_teleporter and not state.unlocked_annihilator) or len(state.unique_seeds) < 10:
            button.clicked = False
            return
        elif state.unlocked_teleporter and len(state.unique_seeds) >= 10 and not state.unlocked_annihilator:
            state.special_buttons[58].tooltip = ""
            state.unlocked_annihilator = True

            from classes.annihilator import Annihilator
            from util import cell_registry

            cell_registry.spawnable_cells.append(Annihilator)
            cell_registry.spawn_rates.append(100)

            button.clicked = False
            return

    match state.catalogue_area:
        case "homebase":
            btn = state.special_buttons[50]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "attacker":
            btn = state.special_buttons[51]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "rotator":
            btn = state.special_buttons[52]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "teleporter":
            btn = state.special_buttons[53]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case "annihilator":
            btn = state.special_buttons[58]
            if btn.disabled: btn.toggle()
            btn.clicked = False

        case _: # default/placeholder
            btn = state.special_buttons[49]
            if btn.disabled: btn.toggle()

    state.catalogue_area = button.id if button.id else "homebase"
    
    match state.catalogue_area:
        case "homebase":
            btn = state.special_buttons[50]
            if not btn.disabled: btn.toggle()

        case "attacker":
            btn = state.special_buttons[51]
            if not btn.disabled: btn.toggle()

        case "rotator":
            btn = state.special_buttons[52]
            if not btn.disabled: btn.toggle()

        case "teleporter":
            btn = state.special_buttons[53]
            if not btn.disabled: btn.toggle()

        case "annihilator":
            btn = state.special_buttons[58]
            if not btn.disabled: btn.toggle()

        case _:
            btn = state.special_buttons[49]
            if not btn.disabled: btn.toggle()


def rewind_button(button: "Button"):
    if not state.world or type(button.id) != str: return
    state.game_end = False

    selected_id = state.selected_cell.id if state.selected_cell else None
    state.world.restore_snapshot(int(button.id))
    from util.render import clear_icon_cache
    clear_icon_cache()
    state.selected_cell = None

    state.y_offset = max(state.y_offset, 50 * (min(10 - state.world.current_tick, 0)) + 15)

    if selected_id is not None: # have to do this cuz 0 would be skipped
        for row in state.world.map:
            for cell in row:
                if cell and cell.id == selected_id:
                    state.selected_cell = cell
                    break
            if state.selected_cell:
                break

    if state.waiting_for_rewind and not state.rewinded: state.rewinded = True
                

    if state.pause and state.pause.disabled: state.pause.toggle()
    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1)[0]:
        if state.rewind and not state.rewind.disabled: state.rewind.toggle()
        if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def complete_tutorial(button: "Button"):
    state.seen_bob = True
    state.finished_tutorial = True
    pygame.time.set_timer(assets.ROSS_REWIND, 0)
    if state.typewriter: state.typewriter.clear()


def show_first_credits(button: "Button") -> None:
    state.show_first_credits = True
    button.toggle()


def show_second_credits(button: "Button") -> None:
    state.show_second_credits = True
    button.toggle()