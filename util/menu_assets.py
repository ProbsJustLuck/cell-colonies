# Circular imports so another file !
import copy
from classes.ui.button import Button, ButtonStyle
from classes.ui.menu_area import MenuArea

from util.game_states import States
from util.game_actions import quit, go_to_credits, go_to_debug, go_to_infopedia, go_to_options, start_game, toggle_pause_simulation, forward, fast_forward, rewind, fast_rewind

_main_menu_style_main = ButtonStyle(
    height=45,
    width=250,
    scale=1.5,
    opacity=0
)
_main_menu_style_quit = ButtonStyle(
    font_size=29,
    height=45,
    width=250,
    scale=1.5,
    opacity=0
)
_main_menu_style_small = ButtonStyle(
    font_size=29,
    height=45,
    width=120,
    scale=1.5,
    opacity=0
)

_simulation_play = ButtonStyle(
    height=40,
    width=40,
    scale=2
)
_simulation_time = ButtonStyle(
    height=30,
    width=30,
    scale=1.2
)

buttons: dict[MenuArea, list[Button]] = {
    MenuArea.MAIN_MENU: [
        Button("SIMULATE", (600, 300), "Click to start a new simulation!", style=copy.copy(_main_menu_style_main), on_enter=start_game),
        Button("OPTIONS", (535, 355), "Click to view and customize game options!", style=copy.copy(_main_menu_style_small), on_enter=go_to_options),
        Button("INFO", (665, 355), "Click to view the cell catalogue!", style=copy.copy(_main_menu_style_small), on_enter=go_to_infopedia),
        Button("CREDITS", (535, 410), "Click to view the game credits!", style=copy.copy(_main_menu_style_small), on_enter=go_to_credits),
        Button("DEBUG", (665, 410), "Click to enter a debug simulation!", style=copy.copy(_main_menu_style_small), on_enter=go_to_debug),
        Button("QUIT", (600, 465), "Click to quit the game :(", style=copy.copy(_main_menu_style_quit), on_enter=quit)
    ],
    MenuArea.SIMULATION: [
        Button("((", (264, 615), "", style=(_simulation_time), on_enter=fast_rewind, disabled=True),
        Button("(", (300, 615), "", style=(_simulation_time), on_enter=rewind, disabled=True),
        Button(">", (350, 615), "", style=(_simulation_play), on_enter=toggle_pause_simulation),
        Button(")", (400, 615), "", style=(_simulation_time), on_enter=forward),
        Button("))", (436, 615), "", style=(_simulation_time), on_enter=fast_forward),
    ]
}
States.fast_rewind = buttons[MenuArea.SIMULATION][0]
States.rewind = buttons[MenuArea.SIMULATION][1]
States.forward = buttons[MenuArea.SIMULATION][3]
States.fast_forward = buttons[MenuArea.SIMULATION][4]

for _, l in buttons.items():
    for button in l:
        button.initialize()