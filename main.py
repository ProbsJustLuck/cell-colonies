import time
start_time = time.time()

import pygame

import util.assets as assets # type: ignore
from util.game_states import States as state
from util.event_handler import event_handler
from util.render import render_start_screen, render_game_screen
from util.ui_helpers import draw_text
from util.game_actions import toggle_pause_simulation

from classes.position import Position
from classes.game_state import GameState
from classes.ui.menu_area import MenuArea
from classes.world_manager import WorldManager # type: ignore

pygame.init()
pygame.display.set_caption("What's up danger")
fps_clock = pygame.Clock()
accum: float = 0.0

print(f"Load took {time.time() - start_time: .4f}s")

while state.running:
    downtime = fps_clock.tick(60)  # Limits game loop to 60 FPS

    for event in pygame.event.get(): event_handler(event)

    match state.current_area:
        case MenuArea.MAIN_MENU:
            render_start_screen()
        case MenuArea.SIMULATION:
            render_game_screen()

            if state.world and not state.sim_pause and not state.full_pause and not state.game_end:
                accum += downtime
                target = 1000.0 / state.target_tps

                for _ in range(state.max_catchup):
                    if accum < target: break
                    success = state.world.tick()

                    if success in [GameState.WIN, GameState.LOSS] and state.pause: 
                        state.game_end = True
                        toggle_pause_simulation(state.pause)
                        state.pause.toggle()
                        break

                    accum -= target
                    
        case _: pass

    
    draw_text(Position(3, 3), f"FPS: {round(fps_clock.get_fps(), 2)}", "#000000", 20)
    draw_text(Position(3, 13), f"Area: {state.current_area}", "#000000", 20)
    draw_text(Position(3, 23), f"Pause: {state.show_tps}", "#000000", 20)
    draw_text(Position(3, 33), f"Offset: {state.offset}", "#000000", 20)


    # flip the display to put your work on screen
    pygame.display.flip()

pygame.quit()