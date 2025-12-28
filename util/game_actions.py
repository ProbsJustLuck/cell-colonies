# Guess what, ANOTHER FILE!
from typing import TYPE_CHECKING

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



def create_world(size: int = 20, homebases: int = 4, walls: int = 30):
    state.world = WorldManager(size, homebases, walls)
    fit_view(size)


def quit(button: "Button | None" = None):
    state.running = False


def start_game(button: "Button"):
    state.current_area = MenuArea.SIMULATION
    create_world(homebases=2, size=30)


def go_to_options(button: "Button"):
    state.current_area = MenuArea.OPTIONS


def go_to_infopedia(button: "Button"):
    state.current_area = MenuArea.INFO


def go_to_credits(button: "Button"):
    state.current_area = MenuArea.CREDITS


def go_to_debug(button: "Button"):
    state.current_area = MenuArea.DEBUG


def toggle_pause_simulation(button: "Button"):
    state.sim_pause = not state.sim_pause

    if state.sim_pause:
        button.label = ">"
        button.style.scale = 2
    else:
        button.label = "||"
        button.style.scale = 1.4
    button.initialize()


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

    state.world.restore_snapshot(1)

    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1):
        if state.rewind and not state.rewind.disabled: state.rewind.toggle()
        if state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()


def fast_rewind(button: "Button"):
    if not state.world: return
    state.game_end = False

    state.world.restore_snapshot(2)

    if state.forward and state.forward.disabled: state.forward.toggle()
    if state.fast_forward and state.fast_forward.disabled: state.fast_forward.toggle()

    if not state.world.get_snapshot(1) and state.rewind and not state.rewind.disabled: state.rewind.toggle()
    if not state.world.get_snapshot(2) and state.fast_rewind and not state.fast_rewind.disabled: state.fast_rewind.toggle()