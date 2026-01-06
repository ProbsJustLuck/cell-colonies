# Circular imports so another file !
import copy

import pygame
from classes.ui.button import Button, ButtonStyle, ButtonType
from classes.ui.key_actions import KeyActions
from classes.ui.slider import Slider, SliderStyle
from classes.ui.menu_area import MenuArea

from util.game_states import States as state
from util.game_actions import quit, go_to_credits, go_to_infopedia, go_to_options, start_game, toggle_pause_simulation, forward, fast_forward, rewind, fast_rewind, go_to_main_menu, show_tps, hide_tps, set_tps, create_world, tps_down, tps_up, next_render_page, toggle_walls, toggle_homebases, toggle_rotators, toggle_attackers, toggle_gridlines, fit_view_button, toggle_change_seed, change_seed, copy_seed, paste_seed, regenerate_world, increase_homebases, decrease_homebases, increase_health, decrease_health, increase_spawn_rate, decrease_spawn_rate, increase_walls, decrease_walls, increase_sim_size, decrease_sim_size, reset_health, reset_homebases, reset_size, reset_spawn_ticks, reset_walls, load_world, return_to_main_menu, change_option_section, toggle_second_bindings, change_binding, reset_binding

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
        Button("OPTIONS", (535, 355), "Click to view and customize game options!", style=copy.copy(_main_menu_style_small), on_enter=go_to_options),
        Button("CELLS", (665, 355), "Click to view the cell catalogue!", style=copy.copy(_main_menu_style_small), on_enter=go_to_infopedia),
        Button("CREDITS", (600, 410), "Click to view the game credits!", style=ButtonStyle(font_size=29, height=45, width=250, scale=1.5), on_enter=go_to_credits),
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
        Button("", (135, 615), "",style=ButtonStyle(height=30,width=30, scale=1.2), on_enter=lambda button: create_world(seed=state.world.seed if state.world else None)),

        Button("(", (527, 615), "", style=ButtonStyle(height=25,width=25, scale=1.3), on_enter=tps_down),
        Button(")", (621, 615), "", style=ButtonStyle(height=25,width=25, scale=1.3), on_enter=tps_up),

        Button("<", (75, 50), "", disabled=True, style=ButtonStyle(height=25,width=30, scale=0.8), on_enter=next_render_page),
        Button("WALLS", (180, 50), "", type=ButtonType.TOGGLE, clicked = True, style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=toggle_walls, on_leave=toggle_walls,id="walls_toggle"),
        Button("HOMEBASES", (350, 50), "", type=ButtonType.TOGGLE, clicked = True, style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=toggle_homebases, on_leave=toggle_homebases,id="homebase_toggle"),
        Button("ROTATORS", (520, 50), "", type=ButtonType.TOGGLE, clicked = True, style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=toggle_rotators, on_leave=toggle_rotators,id="rotator_toggle"),
        Button("FIT VIEW", (180, 50), "", style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=fit_view_button, id="fit_view"),
        Button("GRIDLINES", (350, 50), "", type=ButtonType.TOGGLE, clicked = True, style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=toggle_gridlines, on_leave=toggle_gridlines,id="gridlines_toggle"),
        Button("ATTACKERS", (520, 50), "", type=ButtonType.TOGGLE, clicked = True, style=ButtonStyle(height=25,width=160, scale=0.8), on_enter=toggle_attackers, on_leave=toggle_attackers,id="attackers_toggle"),
        Button(">", (625, 50), "", style=ButtonStyle(height=25,width=30, scale=0.8), on_enter=next_render_page),
        Button("SEED", (105, 650), "", type=ButtonType.TOGGLE, style=ButtonStyle(height=25,width=90, scale=1.2), on_enter=toggle_change_seed, on_leave=toggle_change_seed)
    ]
}
state.fast_rewind = buttons[MenuArea.SIMULATION][0]
state.rewind = buttons[MenuArea.SIMULATION][1]
state.pause = buttons[MenuArea.SIMULATION][2]
state.forward = buttons[MenuArea.SIMULATION][3]
state.fast_forward = buttons[MenuArea.SIMULATION][4]
state.quit_button = buttons[MenuArea.SIMULATION][5]
state.tps_button = buttons[MenuArea.SIMULATION][6]
state.reset_button = buttons[MenuArea.SIMULATION][7]
state.tps_down = buttons[MenuArea.SIMULATION][8]
state.tps_up = buttons[MenuArea.SIMULATION][9]
state.prev_render_page = buttons[MenuArea.SIMULATION][10]
state.fit_view_button = buttons[MenuArea.SIMULATION][14]
state.next_render_page = buttons[MenuArea.SIMULATION][17]
state.seed_button = buttons[MenuArea.SIMULATION][18]


# it was here when i realized it would be better to properly id them instead of putting them in a list
special_buttons: dict[int, Button] = {
    0: Button(">", (818, 345), "Confirm and apply the entered seed!", style=ButtonStyle(height=44,width=30, scale=1.2, base="#707070", hover="#515151", border=2, disabled_opacity=150), on_enter=change_seed), # Change seed button
    1: Button("", (680, 500 + 10), "", style=ButtonStyle(height=60,width=60, scale=1.2, base="#707070", hover="#515151", disabled_opacity=150), on_enter=copy_seed), # Copy seed
    2: Button("", (750, 500 + 10), "", style=ButtonStyle(height=60,width=60, scale=1.2, base="#707070", hover="#515151", disabled_opacity=150), on_enter=paste_seed), # Paste seed
    3: Button("", (820, 500 + 10), "", style=ButtonStyle(height=60,width=60, scale=1.2, base="#707070", hover="#515151", disabled_opacity=150), on_enter=regenerate_world), # Regenerate world

    # Main option buttons
    4: Button("", (350, 500 + 10), "The amount of homebases to spawn. Click to reset to default!", style=ButtonStyle(height=40,width=40, scale=1, tooltip_scale=0.8, base="#707070", hover="#515151"), on_enter=reset_homebases),
    5: Button("", (400, 500 + 10), "The health multiplier of all entities. Click to reset to default!", style=ButtonStyle(height=40,width=40, scale=0.8, tooltip_scale=1, base="#707070", hover="#515151"), on_enter=reset_health),
    6: Button("", (450, 500 + 10), "The # of ticks it takes for a homebase to spawn an entity. Click to reset to default!", style=ButtonStyle(height=40,width=40, scale=1.2, tooltip_scale=0.6667, base="#707070", hover="#515151"), on_enter=reset_spawn_ticks),
    7: Button("", (500, 500 + 10), "The amount of walls to spawn. Click to reset to default!", style=ButtonStyle(height=40,width=40, scale=0.8, tooltip_scale=1, base="#707070", hover="#515151"), on_enter=reset_walls),
    8: Button("", (550, 500 + 10), "The size of the map. Click to reset to default!", style=ButtonStyle(height=40,width=40, scale=1.1, tooltip_scale=0.72727, base="#707070", hover="#515151"), on_enter=reset_size),

    # Option sliders
    9: Button("^", (350, 460 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.2, base="#707070", hover="#515151"), on_enter=increase_homebases),
    10: Button("v", (350, 540 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.1, base="#707070", hover="#515151"), on_enter=decrease_homebases, disabled=True),
    11: Button("^", (400, 460 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.2, base="#707070", hover="#515151"), on_enter=increase_health),
    12: Button("v", (400, 540 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.1, base="#707070", hover="#515151"), on_enter=decrease_health),
    13: Button("^", (450, 460 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.2, base="#707070", hover="#515151"), on_enter=increase_spawn_rate),
    14: Button("v", (450, 540 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.1, base="#707070", hover="#515151"), on_enter=decrease_spawn_rate),
    15: Button("^", (500, 460 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.2, base="#707070", hover="#515151"), on_enter=increase_walls),
    16: Button("v", (500, 540 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.1, base="#707070", hover="#515151"), on_enter=decrease_walls),
    17: Button("^", (550, 460 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.2, base="#707070", hover="#515151"), on_enter=increase_sim_size),
    18: Button("v", (550, 540 + 10), "", style=ButtonStyle(height=20,width=20, scale=1.1, base="#707070", hover="#515151"), on_enter=decrease_sim_size),
    
    # Main menu simulate save
    19: Button("SIMULATE", (600, 300), "Click to start a new simulation!", style=ButtonStyle(height=45, width=250, scale=1.5, opacity=0), on_enter=start_game),
    20: Button("SIMULATE", (575, 300), "Click to start a new simulation!", style=ButtonStyle(height=45, width=200, scale=1.5, opacity=0), on_enter=start_game),
    21: Button(">", (705, 300), "Load world from last save!", style=ButtonStyle(height=45, width=40, scale=1.5, opacity=0), on_enter=load_world),

    # Options buttons are below
    22: Button("<-", (305, 170), "Return to the main menu!", style=ButtonStyle(height=35, width=70, scale=1.5, opacity=255), on_enter=return_to_main_menu),
    23: Button("CONTROLS", (255, 250), "Change the control bindings", type=ButtonType.TOGGLE, clicked=True, style=ButtonStyle(height=45, width=170, scale=1.5, opacity=255, selected="#575757", disabled_opacity=255, disabled="#515151"), on_enter=change_option_section, id="23", disabled=True),
    24: Button("COLONIES", (255, 305), "Change which colony colors appear in game!", type=ButtonType.TOGGLE, style=ButtonStyle(height=45, width=170, scale=1.5, opacity=255, selected="#575757", disabled_opacity=255, disabled="#515151"), on_enter=change_option_section, id="24"),
    25: Button("MISC", (297, 360), "Change miscellaneous settings!", type=ButtonType.TOGGLE, style=ButtonStyle(height=45, width=85, scale=1.5, opacity=255, selected="#575757", disabled_opacity=255, disabled="#515151"), on_enter=change_option_section, id="25"),
    26: Button("DEBUG", (285, 415), "Used for developmental purposes.", type=ButtonType.TOGGLE, style=ButtonStyle(height=45, width=110, scale=1.5, opacity=255, selected="#575757", disabled_opacity=255, disabled="#515151"), on_enter=change_option_section, id="26"),

    27: Button(f"{pygame.key.name(state.bindings[KeyActions.PAN_ALIAS]).upper()}", (750, 280), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAN_ALIAS, on_right_click=reset_binding),
    28: Button(f"{pygame.key.name(state.bindings[KeyActions.PAN_UP]).upper()}", (750, 320), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAN_UP, on_right_click=reset_binding),
    29: Button(f"{pygame.key.name(state.bindings[KeyActions.PAN_DOWN]).upper()}", (750, 350), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAN_DOWN, on_right_click=reset_binding),
    30: Button(f"{pygame.key.name(state.bindings[KeyActions.PAN_LEFT]).upper()}", (750, 380), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAN_LEFT, on_right_click=reset_binding),
    31: Button(f"{pygame.key.name(state.bindings[KeyActions.PAN_RIGHT]).upper()}", (750, 410), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAN_RIGHT, on_right_click=reset_binding),
    32: Button(f"{pygame.key.name(state.bindings[KeyActions.REGENERATE_WORLD]).upper()}", (750, 450), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.REGENERATE_WORLD, on_right_click=reset_binding),

    33: Button("<", (450, 500), "", disabled=True, style=ButtonStyle(height=30, width=30, scale=0.9), on_enter=toggle_second_bindings),
    34: Button(">", (800, 500), "", style=ButtonStyle(height=30, width=30, scale=0.9), on_enter=toggle_second_bindings),

    35: Button(f"{pygame.key.name(state.bindings[KeyActions.ZOOM_IN_ALIAS]).upper()}", (750, 280), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.ZOOM_IN_ALIAS, on_right_click=reset_binding),
    36: Button(f"{pygame.key.name(state.bindings[KeyActions.ZOOM_OUT_ALIAS]).upper()}", (750, 310), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.ZOOM_OUT_ALIAS, on_right_click=reset_binding),
    37: Button(f"{pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}", (750, 350), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.ADVANCE_DIALOGUE, on_right_click=reset_binding),
    38: Button(f"{pygame.key.name(state.bindings[KeyActions.PAUSE_UNPAUSE]).upper()}", (750, 380), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.PAUSE_UNPAUSE, on_right_click=reset_binding),
    39: Button(f"{pygame.key.name(state.bindings[KeyActions.STEP_FORWARD]).upper()}", (750, 420), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.STEP_FORWARD, on_right_click=reset_binding),
    40: Button(f"{pygame.key.name(state.bindings[KeyActions.STEP_BACKWARD]).upper()}", (750, 450), "Left click to set, right click to reset", type=ButtonType.TOGGLE, style=ButtonStyle(height=20, width=140, scale=0.7, base="#c6c6c6", border=1), on_enter=change_binding, id=KeyActions.STEP_BACKWARD, on_right_click=reset_binding),
}
for button in special_buttons.values():
    button.initialize()
state.special_buttons = special_buttons


for _, l in buttons.items():
    for button in l:
        button.initialize()


sliders: dict[MenuArea, list[Slider]] = {
    MenuArea.SIMULATION: [
        Slider(
            rect=pygame.Rect(660, 420, 12, 200),
            orientation="v",
            min_value=20.0,
            max_value=0.1,
            value=2.0,
            snap=False,
            style=SliderStyle(),
            on_change=set_tps
        )
    ]
}
state.tps_slider = sliders[MenuArea.SIMULATION][0]

special_buttons: dict[int, Slider] = {
    0: Slider(
        rect=pygame.Rect(660, 420, 12, 200),
        orientation="v",
        min_value=20.0,
        max_value=0.1,
        value=2.0,
        snap=False,
        style=SliderStyle(),
        on_change=set_tps
    )
}