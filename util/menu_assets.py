# Circular imports so another file !
import copy
from classes.ui.button import Button, ButtonStyle
from util.game_actions import quit

_main_menu_style_main = ButtonStyle(
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

main_menu_buttons: list[Button] = [
    Button("SIMULATE", (600, 300), "Click to start a new game!", style=copy.copy(_main_menu_style_main), on_enter=quit),
    Button("OPTIONS", (535, 355), "Click to view and customize game options!", style=copy.copy(_main_menu_style_small), on_enter=quit),
    Button("INFO", (665, 355), "Click to view the cell catalogue!", style=copy.copy(_main_menu_style_small), on_enter=quit),
    Button("CREDITS", (535, 410), "Click to view the game credits!", style=copy.copy(_main_menu_style_small), on_enter=quit),
    Button("DEBUG", (665, 410), "Click to enter a debug simulation!", style=copy.copy(_main_menu_style_small), on_enter=quit),
    Button("QUIT", (600, 465), "Click to start a new game!", style=copy.copy(_main_menu_style_main), on_enter=quit),
    # Button("INFOPEDIA", (475, 250), "View the enemy catalogue", on_click=go_infopedia),
    # Button("QUIT GAME", (400, 300), "Exit the game", on_click=quit_game),
    # Button("CONTROLS", (222, 180), "Change control mappings", style=ButtonStyle(width=140, font_size=30, padding=5, border=2), is_selected=lambda: state.controls_sect == "Controls"),
]
for button in main_menu_buttons: button.initialize()