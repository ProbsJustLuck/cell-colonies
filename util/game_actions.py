# Guess what, ANOTHER FILE!

from util.ui_helpers import fit_view
from util.game_states import States as state
from classes.ui.menu_area import MenuArea
from classes.world_manager import WorldManager


def create_world(size: int = 20, homebases: int = 4, walls: int = 30):
    state.world = WorldManager(size, homebases, walls)
    fit_view(size)


def quit():
    state.running = False


def start_game():
    state.current_area = MenuArea.SIMULATION
    if state.world is None: create_world(homebases=2, size=30)


def go_to_options():
    state.current_area = MenuArea.OPTIONS


def go_to_infopedia():
    state.current_area = MenuArea.INFO


def go_to_credits():
    state.current_area = MenuArea.CREDITS


def go_to_debug():
    state.current_area = MenuArea.DEBUG
