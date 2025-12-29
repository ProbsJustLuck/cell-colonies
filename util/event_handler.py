import pygame

from classes.ui.menu_area import MenuArea

from util.game_states import States as state
from util.game_actions import quit
from util import menu_assets

def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT: quit()

    if not state.loaded_menu:
        if not state.skipped_animation and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            state.skipped_animation = True
            state.starting_opacity = 255
        return
    
    for slider in menu_assets.sliders.get(state.current_area, []):
        slider.handle_event(event)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #lc
        assert state.tps_button

        if state.show_tps and not (menu_assets.sliders[MenuArea.SIMULATION][0].rect.collidepoint(event.pos) or state.tps_button.rect.collidepoint(event.pos)):
            state.tps_button.click()
            return
        
        for button in menu_assets.buttons.get(state.current_area, []):
            if not button.rect: continue
            if button.rect.collidepoint(event.pos):
                button.click()
                break
        return
    
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2: #mc
        if state.current_area is MenuArea.SIMULATION and state.SIM_RECT.collidepoint(event.pos):
            pygame.event.set_grab(True); 
            pygame.mouse.set_visible(False)
            pygame.mouse.get_rel()

            state.old_cursor_pos = pygame.mouse.get_pos()
            state.panning = True
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.mouse.set_pos(state.old_cursor_pos)
        state.panning = False

    elif event.type == pygame.MOUSEMOTION and state.panning:
        if state.current_area is MenuArea.SIMULATION:
            assert state.world is not None
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
        
    elif event.type == pygame.MOUSEWHEEL: 
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
        