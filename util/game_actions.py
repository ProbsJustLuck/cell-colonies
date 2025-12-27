# Guess what, ANOTHER FILE!

from util.game_states import States as state
from classes.ui.menu_area import MenuArea

def quit():
    state.running = False


def start_game():
    state.current_area = MenuArea.SIMULATION


def go_to_options():
    state.current_area = MenuArea.OPTIONS


def go_to_infopedia():
    state.current_area = MenuArea.INFO


def go_to_credits():
    state.current_area = MenuArea.CREDITS


def go_to_debug():
    state.current_area = MenuArea.DEBUG