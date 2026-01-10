import time

from classes.ui.key_actions import KeyActions
from classes.ui.typewriter import Message
from util import assets
start_time = time.time()

import pygame

from util.game_states import States as state
from util.event_handler import event_handler
from util.render import render_start_screen, render_game_screen, render_options_screen, render_cells_catalogue, render_credits
from util.ui_helpers import draw_text
from util.game_actions import toggle_pause_simulation, check_homebases, check_walls, set_tps

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

count = 0
while state.running:
    downtime = fps_clock.tick(60)  # Limits game loop to 60 FPS
    pressed_keys = pygame.key.get_pressed()

    TRIGGER = 1000

    if state.current_area is MenuArea.SIMULATION:
        if downtime > TRIGGER and state.target_tps not in [2.0, 0.5, 0.1]:
            set_tps(2.0)

            assert state.typewriter

            if not state.typewriter.tps_reset() and not state.typewriter.tps_reset_2():
                if state.typewriter.has_lines_left():
                    state.typewriter.reset_to_queue()

                    state.typewriter.prepend(Message(["Uh oh. Your system was LAGGING hard!", "I've reset the TPS to 2. Be careful when", "setting the TPS too high!", "", "Anyways..."], -3))
                else:
                    state.typewriter.queue(Message(["Uh oh. Your system was LAGGING hard!", "I've reset the TPS to 2. Be careful when", "setting the TPS too high!"], -3))
            elif not state.finished_tutorial and (not state.skip_tutorial or state.seen_bob):
                state.typewriter.reset_progress()

        elif downtime > TRIGGER * 3 and state.target_tps == 2.0:
            set_tps(0.5)

            assert state.typewriter

            if not state.typewriter.tps_reset_2():
                if state.typewriter.has_lines_left():
                    state.typewriter.reset_to_queue()

                    state.typewriter.prepend(Message(["UH OH. Your system was STILL lagging hard!", "I've set the TPS to 0.5. Be careful when", "setting the TPS too high!", "Maybe even consider a better device...", "", "Anyways..."], -4))
                else:
                    state.typewriter.queue(Message(["UH OH. Your system was STILL lagging hard!", "I've set the TPS to 0.5. Be careful when", "setting the TPS too high!", "Maybe even consider a better device..."], -4))
            elif not state.finished_tutorial and (not state.skip_tutorial or state.seen_bob):
                state.typewriter.reset_progress()

        elif downtime > TRIGGER * 3 and state.target_tps == 0.5:
            set_tps(0.1)

            assert state.typewriter

            if not state.typewriter.tps_reset_3():
                if state.typewriter.has_lines_left():
                    state.typewriter.reset_to_queue()

                    state.typewriter.prepend(Message(["UH OH. Your system was still lagging a lot!", "I've set the TPS to 0.1. Try setting some", "settings lower, it will help!!", "Maybe even consider a better device...", "", "Anyways..."], -5))
                else:
                    state.typewriter.queue(Message(["UH OH. Your system was still lagging a lot!", "I've set the TPS to 0.1. Try setting some", "settings lower, it will help!!", "Maybe even consider a better device..."], -5))
            elif not state.finished_tutorial and (not state.skip_tutorial or state.seen_bob):
                state.typewriter.reset_progress()

    for event in pygame.event.get(): event_handler(event)

    match state.current_area:
        case MenuArea.MAIN_MENU:
            render_start_screen()

        case MenuArea.SIMULATION:
            render_game_screen(downtime)

            if state.world and not state.sim_pause and not state.full_pause and not state.game_end: # tick logic
                accum += downtime
                if accum > 20000: accum = 1000
                target = 1000.0 / state.target_tps

                count = 0
                for _ in range(state.max_catchup):
                    if accum < target: break
                    success = state.world.tick()
                    ticks_count += 1
                    count += 1

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


            if pygame.mouse.get_pressed()[0] and state.tps_up and state.tps_up.rect.collidepoint(assets.get_scale_mouse_pos(pygame.mouse.get_pos())) and state.tps_slider and state.tps_button: # tps up
                state.tps_change += 1
                if state.tps_change > 40 and state.target_tps < 40.0: 
                    state.target_tps = round(min(40.0, state.target_tps + 0.2), 1)
                    state.tps_slider.value = state.target_tps

                    if state.tps_down and state.tps_down.disabled: state.tps_down.toggle()

                    state.tps_button.label = f"{state.target_tps}"
                    state.tps_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                    if state.target_tps >= 40.0 and not state.tps_up.disabled: state.tps_up.toggle()


            if pygame.mouse.get_pressed()[0] and state.tps_down and state.tps_down.rect.collidepoint(assets.get_scale_mouse_pos(pygame.mouse.get_pos())) and state.tps_slider and state.tps_button: # tps down
                state.tps_change += 1
                if state.tps_change > 40 and state.target_tps > 0.1: 
                    state.target_tps = round(max(0.1, state.target_tps - 0.2), 1)
                    state.tps_slider.value = state.target_tps

                    if state.tps_up and state.tps_up.disabled: state.tps_up.toggle()

                    state.tps_button.label = f"{state.target_tps}"
                    state.tps_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)
                    
                    if state.target_tps <= 0.1 and not state.tps_down.disabled: state.tps_down.toggle()

            elif state.world and not state.changing_seed and not state.show_tps:
                offset = pygame.Vector2(0, 0)

                if pressed_keys[state.bindings[KeyActions.PAN_UP]]: offset.y += 1

                if pressed_keys[state.bindings[KeyActions.PAN_DOWN]]: offset.y -= 1

                if pressed_keys[state.bindings[KeyActions.PAN_RIGHT]]: offset.x -= 1

                if pressed_keys[state.bindings[KeyActions.PAN_LEFT]]: offset.x += 1

                if offset.length_squared() != 0: offset = offset.normalize() * 5 * state.zoom

                state.offset += offset

                limit = state.SIM_RECT.width * state.zoom + (3 * state.SIM_RECT.width) / 7

                # wrap
                if state.offset.x > limit: state.offset.x -= 2 * limit
                if state.offset.x < -limit: state.offset.x += 2 * limit

                if state.offset.y > limit: state.offset.y -= 2 * limit
                if state.offset.y < -limit: state.offset.y += 2 * limit

            if state.changing_seed:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] and state.typing_box: # backspace
                    state.backspace_repeat = min(40, state.backspace_repeat + 1)
                    if state.backspace_repeat == 40 and state.seed_string:
                        state.seed_string = state.seed_string[:-1]
                        if ((state.seed_string.startswith("-") and len(state.seed_string) < 2) or (not state.seed_string.startswith("-") and len(state.seed_string) < 1)) and not state.special_buttons[0].disabled: state.special_buttons[0].toggle()
                state.caret_timer += downtime
                if state.caret_timer >= 1000:
                    state.caret_timer = 0

                _team_color_amount = len(state.allowed_colonies)
                _mouse_down = pygame.mouse.get_pressed()[0]
                _mouse_pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())


                _change_button = state.special_buttons[9]
                _label_button = state.special_buttons[4]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # homebase up
                    state.homebase_change += 1
                    if state.homebase_change > 40 and state.sim_homebases < _team_color_amount and state.sim_homebases < state.sim_size**2 - state.sim_walls:
                        state.sim_homebases = min(min(state.sim_size**2 - state.sim_walls, state.sim_homebases + 1), _team_color_amount)

                        if state.special_buttons[10].disabled: state.special_buttons[10].toggle()
                        check_walls()

                        _label_button.label = f"{state.sim_homebases}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 1000, loops=1)
                        
                        if state.sim_homebases >= _team_color_amount and not _change_button.disabled: _change_button.toggle()

                _change_button = state.special_buttons[10]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # homebase down
                    state.homebase_change += 1
                    if state.homebase_change > 40 and state.sim_homebases > 2:
                        state.sim_homebases = max(2, state.sim_homebases - 1)

                        if state.special_buttons[9].disabled: state.special_buttons[9].toggle()
                        check_walls()

                        _label_button.label = f"{state.sim_homebases}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 1000, loops=1)
                        
                        if state.sim_homebases <= 2 and not _change_button.disabled: _change_button.toggle()
                if _label_button.rect.collidepoint(_mouse_pos):
                    _label_button.label = f"{state.sim_homebases}"
                    _label_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_HOMEBASE_TEXT, 50, loops=1)


                _change_button = state.special_buttons[11]
                _label_button = state.special_buttons[5]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # health multi up
                    state.health_change += 1
                    if state.health_change > 40 and state.health_multiplier < 5.0: 
                        state.health_multiplier = round(min(5.0, state.health_multiplier + 0.1), 1)

                        if state.special_buttons[12].disabled: state.special_buttons[12].toggle()

                        _label_button.label = f"x{state.health_multiplier:.1f}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 1000, loops=1)
                        
                        if state.health_multiplier >= 5.0 and not _change_button.disabled: _change_button.toggle()

                _change_button = state.special_buttons[12]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # health multi down
                    state.health_change += 1
                    if state.health_change > 40 and state.health_multiplier > 0.1: 
                        state.health_multiplier = round(max(0.1, state.health_multiplier - 0.1), 1)

                        if state.special_buttons[11].disabled: state.special_buttons[11].toggle()

                        _label_button.label = f"x{state.health_multiplier:.1f}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 1000, loops=1)
                        
                        if state.health_multiplier <= 0.1 and not _change_button.disabled: _change_button.toggle()
                if _label_button.rect.collidepoint(_mouse_pos):
                    _label_button.label = f"x{state.health_multiplier:.1f}"
                    _label_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_HEALTH_TEXT, 50, loops=1)


                _change_button = state.special_buttons[13]
                _label_button = state.special_buttons[6]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # spawn rate up
                    state.spawn_change += 1
                    if state.spawn_change > 40 and state.spawn_rate < 8: 
                        state.spawn_rate = min(8, state.spawn_rate + 1)

                        if state.special_buttons[14].disabled: state.special_buttons[14].toggle()

                        _label_button.label = f"{state.spawn_rate}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 1000, loops=1)
                        
                        if state.spawn_rate >= 8 and not _change_button.disabled: _change_button.toggle()

                _change_button = state.special_buttons[14]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # spawn rate down
                    state.spawn_change += 1
                    if state.spawn_change > 40 and state.spawn_rate > 1: 
                        state.spawn_rate = round(max(1, state.spawn_rate - 1), 1)

                        if state.special_buttons[13].disabled: state.special_buttons[13].toggle()

                        _label_button.label = f"{state.spawn_rate}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 1000, loops=1)
                        
                        if state.spawn_rate <= 1 and not _change_button.disabled: _change_button.toggle()
                if _label_button.rect.collidepoint(_mouse_pos):
                    _label_button.label = f"{state.spawn_rate}"
                    _label_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_SPAWN_TEXT, 50, loops=1)


                _change_button = state.special_buttons[15]
                _label_button = state.special_buttons[7]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # walls up
                    state.wall_change += 1
                    if state.wall_change > 40 and state.sim_walls < state.sim_size**2 - state.sim_homebases: 
                        state.sim_walls = min(state.sim_size**2 - state.sim_homebases, state.sim_walls + 2)
                        if state.wall_change > 100 and state.sim_walls < state.sim_size**2 - state.sim_homebases: state.sim_walls = min(state.sim_size**2 - state.sim_homebases, state.sim_walls + 5)

                        if state.special_buttons[16].disabled: state.special_buttons[16].toggle()
                        check_homebases()

                        _label_button.label = f"{state.sim_walls}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 1000, loops=1)
                        
                        if state.sim_walls >= state.sim_size**2 - state.sim_homebases and not _change_button.disabled: _change_button.toggle()

                _change_button = state.special_buttons[16]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # walls down
                    state.wall_change += 1
                    if state.wall_change > 40 and state.sim_walls > 0:
                        state.sim_walls = max(0, state.sim_walls - 2)
                        if state.wall_change > 100 and state.sim_walls > 0: state.sim_walls = max(0, state.sim_walls - 5)

                        if state.special_buttons[15].disabled: state.special_buttons[15].toggle()
                        check_homebases()

                        _label_button.label = f"{state.sim_walls}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 1000, loops=1)
                        
                        if state.sim_walls <= 0 and not _change_button.disabled: _change_button.toggle()
                if _label_button.rect.collidepoint(_mouse_pos):
                    _label_button.label = f"{state.sim_walls}"
                    _label_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_WALL_TEXT, 50, loops=1)


                _change_button = state.special_buttons[17]
                _label_button = state.special_buttons[8]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # size up
                    state.size_change += 1
                    if state.size_change > 40 and state.sim_size < 100: 
                        state.sim_size = min(100, state.sim_size + 1)
                        if state.size_change > 100 and state.sim_size < 100: state.sim_size = min(100, state.sim_size + 3)

                        if state.special_buttons[18].disabled: state.special_buttons[18].toggle()
                        check_walls()
                        check_homebases()

                        _label_button.label = f"{state.sim_size}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 1000, loops=1)
                        
                        if state.sim_size >= 100 and not _change_button.disabled: _change_button.toggle()

                _change_button = state.special_buttons[18]
                if _mouse_down and _change_button.rect.collidepoint(_mouse_pos): # size down
                    state.size_change += 1
                    if state.size_change > 40 and state.sim_size > 2:
                        state.sim_size = max(2, state.sim_size - 1)
                        if state.size_change > 100 and state.sim_size > 2: state.sim_size = max(2, state.sim_size - 3)

                        if state.special_buttons[17].disabled: state.special_buttons[17].toggle()
                        check_walls()
                        check_homebases()

                        _label_button.label = f"{state.sim_size}"
                        _label_button.initialize()
                        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
                        pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 1000, loops=1)
                        
                        if state.sim_size <= 2 and not _change_button.disabled: _change_button.toggle()
                if _label_button.rect.collidepoint(_mouse_pos):
                    _label_button.label = f"{state.sim_size}"
                    _label_button.initialize()
                    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 0)
                    pygame.time.set_timer(assets.CLEAR_SIZE_TEXT, 50, loops=1)

        case MenuArea.OPTIONS:
            if state.reverting and state.reverting_time >= 0: state.reverting_time = max(state.reverting_time - downtime, 0)
            render_options_screen()

        case MenuArea.CATALOGUE:
            render_cells_catalogue()
            state.cell_color_timer += downtime
            if state.cell_color_timer > 1000:
                state.cell_color_timer = 0
                state.cell_color_index += 1
                state.cell_color_index %= len(state.allowed_colonies)

        case MenuArea.CREDITS:
            render_credits(downtime)


        case _: pass

    
    draw_text(Position(3, 3), f"FPS: {round(fps_clock.get_fps(), 2)},   TPS: {round(state.tps, 2)},     Homebases Alive: {len(state.world.homebases) if state.world else 0}    Length: {len(state.unique_seeds)}", "#000000", 20)
    draw_text(Position(3, 13), f"Current Tick: {state.world.current_tick if state.world else 0},    Hovered Position: {state.hovered_pos} Offset: {state.y_offset}    Ticks Last Frame: {count}", "#000000", 20)

    # flip the display to put your work on screen
    assets.display_screen.blit(pygame.transform.smoothscale(assets.screen, assets.display_screen.get_size()), (0, 0))
    pygame.display.flip()

pygame.quit()