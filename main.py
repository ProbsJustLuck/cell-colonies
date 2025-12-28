import time
start_time = time.time()

import pygame

import util.assets as assets # type: ignore
from util.game_states import States as state
from util.event_handler import event_handler
from util.render import render_start_screen, render_game_screen
from util.ui_helpers import draw_text

from classes.position import Position
from classes.ui.menu_area import MenuArea
from classes.world_manager import WorldManager # type: ignore

pygame.init()
pygame.display.set_caption("What's up danger")
clock = pygame.Clock()

print(f"Load took {time.time() - start_time: .4f}s")

while state.running:
    for event in pygame.event.get(): event_handler(event)

    match state.current_area:
        case MenuArea.MAIN_MENU:
            render_start_screen()
        case MenuArea.SIMULATION:
            render_game_screen()
        case _: pass

    
    draw_text(Position(3, 3), f"FPS: {round(clock.get_fps(), 2)}", "#000000", 20)
    draw_text(Position(3, 13), f"Area: {state.current_area}", "#000000", 20)
    draw_text(Position(3, 23), f"Zoom: {state.zoom}", "#000000", 20)
    draw_text(Position(3, 33), f"Offset: {state.offset}", "#000000", 20)


    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()