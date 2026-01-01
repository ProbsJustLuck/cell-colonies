import pygame

from classes.position import Position
from classes.ui.menu_area import MenuArea

from util import assets
from util.game_states import States as state
from util.game_actions import quit
from util import menu_assets

def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT: quit()

    # Events
    if event.type == assets.CLEAR_TPS_TEXT and state.tps_button: 
        state.tps_button.label = "TPS"
        state.tps_button.initialize()
        return
    elif event.type == assets.CLEAR_HOMEBASE_TEXT:
        state.special_buttons[4].label = ""
        state.special_buttons[4].initialize()
    elif event.type == assets.CLEAR_HEALTH_TEXT:
        state.special_buttons[5].label = ""
        state.special_buttons[5].initialize()
    elif event.type == assets.CLEAR_SPAWN_TEXT:
        state.special_buttons[6].label = ""
        state.special_buttons[6].initialize()
    elif event.type == assets.CLEAR_WALL_TEXT:
        state.special_buttons[7].label = ""
        state.special_buttons[7].initialize()
    elif event.type == assets.CLEAR_SIZE_TEXT:
        state.special_buttons[8].label = ""
        state.special_buttons[8].initialize()


    if event.type == pygame.KEYDOWN and state.typing_seed:
        if event.key == pygame.K_BACKSPACE and state.seed_string:
            state.seed_string = state.seed_string[:-1]
            if ((state.seed_string.startswith("-") and len(state.seed_string) < 2) or (not state.seed_string.startswith("-") and len(state.seed_string) < 1)) and not state.special_buttons[0].disabled: state.special_buttons[0].toggle()
            return
        elif event.key == pygame.K_RETURN:
            state.typing_seed = False
            return
        elif event.key == pygame.K_ESCAPE:
            state.typing_seed = False
            state.seed_string = ""
            return
        else:
            if (
                not event.unicode.isdigit() and not (not state.seed_string and event.unicode == "-")
                ) or (
                    state.seed_string.startswith('-') and len(state.seed_string) > 10
                ) or (
                    not state.seed_string.startswith('-') and len(state.seed_string) > 9
            ): return

            state.seed_string += event.unicode
            if ((state.seed_string.startswith("-") and len(state.seed_string) > 1) or (not state.seed_string.startswith("-") and len(state.seed_string) > 0)) and state.special_buttons[0].disabled: state.special_buttons[0].toggle()
            return
    if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE and state.typing_seed: state.backspace_repeat = 0


    if not state.loaded_menu:
        if not state.skipped_animation and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            state.skipped_animation = True
            state.starting_opacity = 255
        return


    for slider in menu_assets.sliders.get(state.current_area, []):
            slider.handle_event(event)


    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #lc
        assert state.tps_button and state.tps_up and state.tps_down


        if state.changing_seed:
            if state.typing_box and not state.typing_seed and state.typing_box.collidepoint(event.pos):
                state.typing_seed = True
                return
            elif state.typing_seed and state.typing_box and not state.typing_box.collidepoint(event.pos):
                state.typing_seed = False
                return
            
            for i in range(19):
                if state.special_buttons[i].rect.collidepoint(event.pos):
                    state.special_buttons[i].click()
            

            if state.seed_box and state.seed_button and not state.seed_box.collidepoint(event.pos): state.seed_button.click()

            return


        if state.show_tps and not (menu_assets.sliders[MenuArea.SIMULATION][0].rect.collidepoint(event.pos) or state.tps_button.rect.collidepoint(event.pos) or state.tps_up.rect.collidepoint(event.pos) or state.tps_down.rect.collidepoint(event.pos)):
            state.tps_button.click()
            return
        

        for button in menu_assets.buttons.get(state.current_area, []):
            if (button.id in ["walls_toggle", "homebase_toggle", "rotator_toggle"] and not state.second_render_page) or (button.id in ["attackers_toggle", "gridlines_toggle", "fit_view"] and state.second_render_page): continue

            if not button.rect: continue
            if button.rect.collidepoint(event.pos):
                button.click()
                return
        

        if state.current_area is MenuArea.SIMULATION and state.world:
            origin = state.SIM_RECT.topleft + state.offset

            cell_size = int((state.SIM_RECT.width / state.sim_size) * state.zoom)
            world_rect = pygame.Rect(origin.x, origin.y, state.sim_size * cell_size, state.sim_size * cell_size)

            if world_rect.collidepoint(event.pos):
                col = int((event.pos[0] - origin.x) / cell_size)
                row = int((event.pos[1] - origin.y) / cell_size)

                pos = Position(row, col)
                cell = state.world.get_cell(pos)

                if cell and ((cell.name in state.disabled_cells and state.second_render_page) or (cell.name in state.disabled_cells and not state.second_render_page)): return

                state.selected_cell = state.world.get_cell(pos)
                state.selected_id = state.world.get_id(pos)
            else:
                state.selected_cell = None
        
        return


    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if state.tps_change > 0: state.tps_change = 0
        if state.homebase_change: state.homebase_change = 0
        if state.health_change: state.health_change = 0
        if state.spawn_change: state.spawn_change = 0
        if state.wall_change: state.wall_change = 0
        if state.size_change: state.size_change = 0
    

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2: #mc
        if state.current_area is MenuArea.SIMULATION and state.SIM_RECT.collidepoint(event.pos):
            pygame.event.set_grab(True); 
            pygame.mouse.set_cursor(assets.grab_cursor)
            pygame.mouse.get_rel()

            state.old_cursor_pos = pygame.mouse.get_pos()
            state.panning = True
            return
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
        pygame.event.set_grab(False)

        if state.current_area is MenuArea.SIMULATION and state.world and state.SIM_RECT.collidepoint(pygame.mouse.get_pos()): pygame.mouse.set_cursor(assets.crosshair_cursor)
        else: pygame.mouse.set_cursor(assets.arrow_cursor)

        state.panning = False
        return

    elif event.type == pygame.MOUSEMOTION :
        if state.current_area is MenuArea.SIMULATION and state.world:
            if state.panning:
                dx, dy = pygame.mouse.get_rel()
                state.offset += (dx, dy)

                world_px = state.world.size * (state.SIM_RECT.width / state.world.size) * state.zoom  # simplifies to SIM_RECT.width * zoom
                margin = (3 * state.SIM_RECT.width) / 7
                limit_x = world_px + margin
                limit_y = world_px + margin

                # wrap when you drift past the span
                if state.offset.x > limit_x: state.offset.x -= 2 * limit_x
                if state.offset.x < -limit_x: state.offset.x += 2 * limit_x

                if state.offset.y > limit_y: state.offset.y -= 2 * limit_y
                if state.offset.y < -limit_y: state.offset.y += 2 * limit_y

                return
            
            mouse_pos = pygame.mouse.get_pos()
            if state.SIM_RECT.collidepoint(mouse_pos) and not state.changing_seed: 
                pygame.mouse.set_cursor(assets.crosshair_cursor)

                origin = state.SIM_RECT.topleft + state.offset

                cell_size = int((state.SIM_RECT.width / state.sim_size) * state.zoom)
                world_rect = pygame.Rect(origin.x, origin.y, state.sim_size * cell_size, state.sim_size * cell_size)

                if world_rect.collidepoint(event.pos):
                    col = int((event.pos[0] - origin.x) / cell_size)
                    row = int((event.pos[1] - origin.y) / cell_size)

                    state.hovered_pos = Position(row, col)
                else:
                    state.hovered_pos = None
            elif state.typing_box and state.typing_box.collidepoint(mouse_pos): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else: pygame.mouse.set_cursor(assets.arrow_cursor)
        
    elif event.type == pygame.MOUSEWHEEL: 
        if state.changing_seed: return

        if state.current_area is MenuArea.SIMULATION and state.world and state.SIM_RECT.collidepoint(pygame.mouse.get_pos()): # Zoom
            if event.y > 0: # Up
                old_zoom = state.zoom_levels[state.zoom_index]
                state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index + 1))
                new_zoom = state.zoom_levels[state.zoom_index]

                # anchor to
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                base_cell = state.SIM_RECT.width / state.world.size
                origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
                world_pt = (mouse_pos - origin) / (base_cell * old_zoom)
                state.offset = mouse_pos - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
                state.zoom = new_zoom
                return

            if event.y < 0: # Down
                old_zoom = state.zoom_levels[state.zoom_index]
                state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index - 1))
                new_zoom = state.zoom_levels[state.zoom_index]

                # anchor to
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                base_cell = state.SIM_RECT.width / state.world.size
                origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
                world_pt = (mouse_pos - origin) / (base_cell * old_zoom)
                state.offset = mouse_pos - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
                state.zoom = new_zoom
                return
            
        elif state.current_area is MenuArea.SIMULATION and state.tps_button and state.tps_slider and (state.tps_button.rect.collidepoint(pygame.mouse.get_pos()) or state.tps_slider.rect.collidepoint(pygame.mouse.get_pos())) and state.tps_button:
            if event.y > 0 and state.target_tps < 20.0: # Up
                state.target_tps = round(min(state.target_tps + (event.y / 5), 20.0), 1)

                state.tps_slider.value = state.target_tps

                if state.tps_down and state.tps_down.disabled: state.tps_down.toggle()
                if state.target_tps >= 20.0 and state.tps_up and not state.tps_up.disabled: state.tps_up.toggle()

                state.tps_button.label = f"{state.target_tps}"
                state.tps_button.initialize()
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                return

            if event.y < 0 and state.target_tps > 0.1: # Down
                state.target_tps = round(max(state.target_tps + (event.y / 5), 0.1), 1)

                state.tps_slider.value = state.target_tps

                if state.tps_up and state.tps_up.disabled: state.tps_up.toggle()
                if state.target_tps <= 0.1 and state.tps_down and not state.tps_down.disabled: state.tps_down.toggle()

                state.tps_button.label = f"{state.target_tps}"
                state.tps_button.initialize()
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                return