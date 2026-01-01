import time

from util import assets
start_time = time.time()

import pygame

from util.game_states import States as state
from util.event_handler import event_handler
from util.render import render_start_screen, render_game_screen
from util.ui_helpers import draw_text
from util.game_actions import toggle_pause_simulation

from classes.position import Position
from classes.game_state import GameState
from classes.ui.menu_area import MenuArea

pygame.init()
pygame.display.set_caption("What's up danger")

fps_clock = pygame.Clock()
accum: float = 0.0
ticks_count = 0.0
last_measure = pygame.time.get_ticks()

print(f"Load took {time.time() - start_time: .4f}s")

while state.running:
    downtime = fps_clock.tick(60)  # Limits game loop to 60 FPS
    pressed_keys = pygame.key.get_pressed()

    for event in pygame.event.get(): event_handler(event)

    match state.current_area:
        case MenuArea.MAIN_MENU:
            render_start_screen()
        case MenuArea.SIMULATION:
            render_game_screen()

            if state.world and not state.sim_pause and not state.full_pause and not state.game_end: # tick logic
                accum += downtime
                target = 1000.0 / state.target_tps

                for _ in range(state.max_catchup):
                    if accum < target: break
                    success = state.world.tick()
                    ticks_count += 1

                    if success in [GameState.WIN, GameState.LOSS] and state.pause: 
                        state.game_end = True
                        toggle_pause_simulation(state.pause)
                        state.pause.toggle()
                        break

                    accum -= target

            current_time = pygame.time.get_ticks()
            if current_time - last_measure >= 1000: # Measure TPS
                state.tps = ticks_count * 1000.0 / (current_time - last_measure)
                ticks_count = 0
                last_measure = current_time

            if pygame.mouse.get_pressed()[0] and state.tps_up and state.tps_up.rect.collidepoint(pygame.mouse.get_pos()) and state.tps_slider and state.tps_button: # tps up
                state.tps_change += 1
                if state.tps_change > 40 and state.target_tps < 20.0: 
                    state.target_tps = round(min(20.0, state.target_tps + 0.2), 1)
                    state.tps_slider.value = state.target_tps

                    state.tps_button.label = f"{state.target_tps}"
                    state.tps_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                    if state.target_tps >= 20.0 and not state.tps_up.disabled: state.tps_up.toggle()

            if pygame.mouse.get_pressed()[0] and state.tps_down and state.tps_down.rect.collidepoint(pygame.mouse.get_pos()) and state.tps_slider and state.tps_button: # tps down
                state.tps_change += 1
                if state.tps_change > 40 and state.target_tps > 0.1: 
                    state.target_tps = round(max(0.1, state.target_tps - 0.2), 1)
                    state.tps_slider.value = state.target_tps

                    state.tps_button.label = f"{state.target_tps}"
                    state.tps_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)
                    
                    if state.target_tps <= 0.1 and not state.tps_down.disabled: state.tps_down.toggle()

            if state.changing_seed:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] and state.typing_box:
                    state.backspace_repeat = min(40, state.backspace_repeat + 1)
                    if state.backspace_repeat == 40 and state.seed_string:
                        state.seed_string = state.seed_string[:-1]
                        if ((state.seed_string.startswith("-") and len(state.seed_string) < 2) or (not state.seed_string.startswith("-") and len(state.seed_string) < 1)) and not state.special_buttons[0].disabled: state.special_buttons[0].toggle()
                state.caret_timer += downtime
                if state.caret_timer >= 1000:
                    state.caret_timer = 0
        case _: pass

    
    draw_text(Position(3, 3), f"FPS: {round(fps_clock.get_fps(), 2)}, TPS: {round(state.tps, 2)}", "#000000", 20)
    draw_text(Position(3, 13), f"Homebases Alive: {len(state.world.homebases) if state.world else 0}", "#000000", 20)
    draw_text(Position(3, 23), f"Current Tick: {state.world.current_tick if state.world else 0}", "#000000", 20)

    # flip the display to put your work on screen
    pygame.display.flip()

pygame.quit()