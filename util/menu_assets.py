# Circular imports so another file !
import copy
from classes.ui.button import Button, ButtonStyle, ButtonType
from classes.ui.menu_area import MenuArea
from util.game_actions import quit, go_to_credits, go_to_debug, go_to_infopedia, go_to_options, start_game

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

buttons: dict[MenuArea, list[Button]] = {
    MenuArea.MAIN_MENU: [
        Button("SIMULATE", (600, 300), "Click to start a new simulation!", type=ButtonType.TOGGLE, style=copy.copy(_main_menu_style_main), on_enter=start_game),
        Button("OPTIONS", (535, 355), "Click to view and customize game options!", style=copy.copy(_main_menu_style_small), on_enter=go_to_options),
        Button("INFO", (665, 355), "Click to view the cell catalogue!", style=copy.copy(_main_menu_style_small), on_enter=go_to_infopedia),
        Button("CREDITS", (535, 410), "Click to view the game credits!", style=copy.copy(_main_menu_style_small), on_enter=go_to_credits),
        Button("DEBUG", (665, 410), "Click to enter a debug simulation!", style=copy.copy(_main_menu_style_small), on_enter=go_to_debug),
        Button("QUIT", (600, 465), "Click to quit the game :(", style=copy.copy(_main_menu_style_quit), on_enter=quit),
        # Button("INFOPEDIA", (475, 250), "View the enemy catalogue", on_click=go_infopedia),
        # Button("QUIT GAME", (400, 300), "Exit the game", on_click=quit_game),
        # Button("CONTROLS", (222, 180), "Change control mappings", style=ButtonStyle(width=140, font_size=30, padding=5, border=2), is_selected=lambda: state.controls_sect == "Controls"),
    ]
}
for _, l in buttons.items():
    for button in l:
        button.initialize()
        # if button.type == ButtonType.TOGGLE: button.toggle()