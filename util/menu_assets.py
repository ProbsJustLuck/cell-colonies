# Circular imports so another file !
import copy

import pygame
from classes.ui.button import Button, ButtonStyle, ButtonType
from classes.ui.slider import Slider, SliderStyle
from classes.ui.menu_area import MenuArea

from util.game_states import States as state
from util.game_actions import quit, go_to_credits, go_to_debug, go_to_infopedia, go_to_options, start_game, toggle_pause_simulation, forward, fast_forward, rewind, fast_rewind, go_to_main_menu, show_tps, hide_tps, set_tps, create_world, tps_down, tps_up

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
        Button("CELLS", (665, 355), "Click to view the cell catalogue!", style=copy.copy(_main_menu_style_small), on_enter=go_to_infopedia),
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
        Button("<-", (85, 615), "", style=ButtonStyle(height=30,width=50, scale=1.3), on_enter=go_to_main_menu),

        Button("TPS", (575, 615), "", type=ButtonType.TOGGLE,style=ButtonStyle(height=30,width=50, scale=1.2), on_enter=show_tps, on_leave=hide_tps),
        Button("", (135, 615), "",style=ButtonStyle(height=30,width=30, scale=1.2), on_enter=lambda button: create_world(seed=state.world.get_seed() if state.world else None)),

        Button("(", (527, 615), "", style=ButtonStyle(height=25,width=25, scale=1.3), on_enter=tps_down),
        Button(")", (621, 615), "", style=ButtonStyle(height=25,width=25, scale=1.3), on_enter=tps_up)
    ]
}
state.fast_rewind = buttons[MenuArea.SIMULATION][0]
state.rewind = buttons[MenuArea.SIMULATION][1]
state.pause = buttons[MenuArea.SIMULATION][2]
state.forward = buttons[MenuArea.SIMULATION][3]
state.fast_forward = buttons[MenuArea.SIMULATION][4]
state.tps_button = buttons[MenuArea.SIMULATION][6]
state.tps_down = buttons[MenuArea.SIMULATION][8]
state.tps_up = buttons[MenuArea.SIMULATION][9]

for _, l in buttons.items():
    for button in l:
        button.initialize()


sliders: dict[MenuArea, list[Slider]] = {
    MenuArea.SIMULATION: [
        Slider(
            rect=pygame.Rect(660, 420, 12, 200),
            orientation="v",
            min_value=20.0,
            max_value=0.5,
            value=2.0,
            snap_on_release=False,
            style=SliderStyle(),
            on_change=set_tps
        )
    ]
}
state.tps_slider = sliders[MenuArea.SIMULATION][0]