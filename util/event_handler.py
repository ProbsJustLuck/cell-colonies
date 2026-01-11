import pygame

from classes.position import get_pos
from classes.ui.key_actions import KeyActions
from classes.ui.menu_area import MenuArea
from classes.ui.typewriter import Message

from constants import Constants
from util import assets
from util.game_states import States as state
from util.game_actions import create_world, quit, check_homebases, check_walls, toggle_pause_simulation, change_binding_event, revert_video_changes, forward, fast_forward, rewind, fast_rewind
from util import menu_assets


def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT: quit()

    if hasattr(event, "pos"):
        data = event.dict.copy()
        width, height = pygame.display.get_window_size()

        data["pos"] = assets.get_scale_mouse_pos(event.pos)
        if "rel" in data: data["rel"] = int(data["rel"][0] * (Constants.SCREEN_WIDTH / (Constants.SCREEN_WIDTH / width))), int(data["rel"][1] * (Constants.SCREEN_HEIGHT / (Constants.SCREEN_HEIGHT / height)))

        event = pygame.event.Event(event.type, data)

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

    elif event.type == assets.ROSS_CALL:
        if state.typewriter and not state.finished_tutorial:
            state.seen_bob = True
            state.typewriter.queue(Message(["Hello, welcome to Cell Colonies!", "My name is Bob Ross. You can tell from", " my hair.", "", "I will be your guide and tutorial for", "this game!"]))

            state.typewriter.queue(Message(["I'll help get you started for now.", "", "If you look around the screen, you'll", "find many different buttons and sliders", "for you to play with!"]))

            state.typewriter.queue(Message(["An example would be the simulation zone,", "the main attraction of this game!", "", "I've marked it in red on your screen.", "", "Here you'll find the main simulation", "with every cell and its team displayed!"], 0))
    
    elif event.type == assets.ROSS_PAN:
        if state.typewriter and not state.finished_tutorial:
            state.typewriter.queue(Message(["Great work! You've got a knack for that.", "", "Anyways, we can move onto the next", "area of our tour."]))
            state.typewriter.queue(Message(["Take a look at those controls below the", "simulation zone.", "", "Those allow you to control the", "playback of the current simulation!"], 3))
            state.typewriter.queue(Message(["That middle button pauses/unpauses", "the current simulation.", "", "The buttons to the right of the pause", "button control moving the simulation one", "or two ticks forward respectively.", "When the simulation ends, you cannot", "use either of them!"], 4))
    elif event.type == assets.ROSS_PAN_REMINDER:
        if state.typewriter and not state.finished_tutorial:
            state.typewriter.queue(Message(["Hey, you okay?", "I'm waiting for you to pan and zoom", "remember?"]))
            state.typewriter.queue(Message(["If you've forgotten, you can pan by", "using (MMB) and moving your mouse,", "and zoom using (Wheel Up/Down)!"]))
            state.typewriter.queue(Message(["Remember, you have to hover over the", "simulation zone to be able to do those!"], 2))

    elif event.type == assets.ROSS_PAUSE:
        if state.typewriter and not state.finished_tutorial:
            if not state.sim_pause: toggle_pause_simulation(None)
            state.typewriter.queue(Message(["Good job! I gave you some extra time to", "play around with the simulation.", "", "The basis of Cell Colonies is for one", "homebase to be left standing! Homebases", "are marked by cells with house icons."]))
            state.typewriter.queue(Message(["For more information on every cell", "in the game, I recommend checking", "out the cell catalogue in the main menu!", "", "It houses most of the information in the", "game about every cell."]))
            state.typewriter.queue(Message(["Next up are the buttons to the left of the", "pause button! These are the rewind", "buttons, basically going back in time 1-2", "ticks in the simulation respectively!"], 6))
    elif event.type == assets.ROSS_PAUSE_REMINDER:
        if state.typewriter and not state.finished_tutorial:
            state.typewriter.queue(Message(["Hey, you okay?", "I'm waiting for you to unpause, remember?"]))
            state.typewriter.queue(Message(["If you've forgotten, you can unpause by", "using (LMB) on the middle pause button,", "and forward using (LMB) on the forward", "or fast forward buttons!"], 4))
            state.typewriter.queue(Message(["Remember, you have to hover over the", "buttons to do those!"], 7))

    elif event.type == assets.ROSS_REWIND:
        if state.typewriter and not state.finished_tutorial:
            state.typewriter.queue(Message(["Nice!", "", "For the next area, we'll focus on", "controlling the unpaused speed of", "the simulation."]))
            state.typewriter.queue(Message(["See the tps button in the bottom?", "", "Scrolling directly on the tps button will", "change the TPS based off your input!"], 10))
            state.typewriter.queue(Message(["The two buttons beside the TPS button", "allow you to fine-tune the TPS to", "whatever you wish too."], 12))
            state.typewriter.queue(Message(["Finally, pressing the TPS button pulls", "up a slider to allow easier", "control over the TPS.", "", "You can try this now!", f"Once you're finished, press ({pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}) and", "I'll explain the next part."], 13))

            state.typewriter.queue(Message(["We can move on now.", "Remember, changing the TPS too high", "might drop your framerate by a lot"]))
            state.typewriter.queue(Message(["In the bottom left, you'll notice the seed", "button.", "", "Pressing this will bring up a new menu,", "allowing you to set the seed of the world", "and set different world options, such as", "how often Homebases will spawn entities!"], 14))
            state.typewriter.queue(Message(["You'll also find some options to copy the", "current seed and paste a seed in, letting", "you share creative and interesting", "seeds that you find to others!", "", "Beware, some options can be VERY", " laggy when maxed!"]))
            state.typewriter.queue(Message(["Try some of the options out!", "I'll let you play around with the settings", "for a bit.", "", f"Once you're finished, press ({pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}) and", "I'll explain the next part!"]))

            state.typewriter.queue(Message(["Next on the tour is the visibility toolbar.", "Look at the top of your screen and you'll", "find it!", "", "This toolbar toggles visibility of certain", "aspects of the game for you."], 15))
            state.typewriter.queue(Message(["The first button actually just resets", "your view, but other than that, the rest", "of the buttons are relatively self", "explanatory."]))
            state.typewriter.queue(Message(["Try some of the options out!", "I'll let you play around with the settings", "for a bit.", "", f"Once you're finished, press ({pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}) and", "I'll explain the next part!"]))

            state.typewriter.queue(Message(["Now try clicking on a cell!", "It'll bring up a cool menu above me,", "showing you different information", "about the cell you clicked on.", "", "All cells have unique information to show in", "the sidebar!"]))
            state.typewriter.queue(Message(["I'll let you play around for a bit.", "", f"Once you're finished, press ({pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}) and", "I'll explain the mext part!"]))

            state.typewriter.queue(Message(["The final area I want to explain is the", "rewind timeline, seen on the left.", "It shows a timeline of all previous", "ticks, allowing you to easily rewind to", "previous ticks!"], 20))
            state.typewriter.queue(Message(["You can scroll the list with (Wheel Up/Down).", "Its very handy, I use it all the time!"]))
            state.typewriter.queue(Message(["I'll let you play around for a bit.", "", f"Once you're finished, press ({pygame.key.name(state.bindings[KeyActions.ADVANCE_DIALOGUE]).upper()}) and", "I'll explain the final part!"]))

            state.typewriter.queue(Message(["The final area to cover is the bottom left,", "just above the seed button.", "This area only has two buttons in it."], 16))
            state.typewriter.queue(Message(["The button to the right resets your", "current world to the original, with the", "same game settings you set. Its useful", "to retry a simulation from scratch!"], 17))
            state.typewriter.queue(Message(["Its also useful if the rewind reached", "the max history length and you want", "to go farther."]))
            state.typewriter.queue(Message(["The button to the left is pretty simple, it", "just quits to the main menu."], 18))
            state.typewriter.queue(Message(["If you ever want to return to your", "current simulation, don't worry! Quitting", "via this button saves your simulation,", "you can rejoin it via the main menu!"]))

            state.typewriter.queue(Message(["And that's everything!", "If you have any questions, you can", "always call me.", "", "Enjoy!"], 19))
    elif event.type == assets.ROSS_REWIND_REMINDER:
        if state.typewriter and not state.finished_tutorial:
            state.typewriter.queue(Message(["Hey, you okay?", "I'm waiting for you to rewind, remember?"]))
            state.typewriter.queue(Message(["If you've forgotten, you can rewind by", "using (LMB) on either rewind button!", "", "You have to have some ticks to rewind to", "in order to rewind!"], 9))
            state.typewriter.queue(Message(["If you can't rewind, try unpausing for", "a few ticks, then retrying."], 9))
            state.typewriter.queue(Message(["Remember, you have to hover over the", "buttons to do those!"], 11))

    elif event.type == assets.REVERT_VIDEO_CHANGES:
        revert_video_changes()
        return


    if state.reverting:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button1 = state.special_buttons[44]
            button2 = state.special_buttons[45]
            
            if button1.rect.collidepoint(event.pos):
                button1.click()
            elif button2.rect.collidepoint(event.pos):
                button2.click()
        
        return


    # Keys/clicks
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

    if event.type == pygame.KEYDOWN and state.typewriter and state.typewriter.done and event.key == pygame.K_c:
        match state.typewriter.id:
            case 0:
                state.typewriter.queue(Message(["To give you better viewing options for", "the simulation zone, you can pan (MMB)", "and zoom (Wheel Up/Down) while", "hovered over it.", "", "Give it a try now!"], 1))
                return
        
            case 1:
                state.waiting_for_pan = True
                pygame.time.set_timer(assets.ROSS_PAN_REMINDER, 20000, loops=1)

            case 2:
                pygame.time.set_timer(assets.ROSS_PAN_REMINDER, 20000, loops=1)

            case 4:
                state.typewriter.queue(Message(["Give it a try  now!", f"You can click on them using (LMB)", "", "I'll wait for you to mess around with this!"], 5))
                return
            
            case 5:
                state.waiting_for_pause = True
                pygame.time.set_timer(assets.ROSS_PAUSE_REMINDER, 20000, loops=1)

            case 6:
                state.typewriter.queue(Message(["Taking snapshots every tick can be laggy,", "so snapshots are taken every few ticks,", "then the rest are manually simulated!", "", "The frequenct can be set in options!", f"The current frequency is every {state.snapshot_frequency} ticks."]))
                state.typewriter.queue(Message(["Rewinding can only be done when the", "simulation is paused!", "", "Try it out now!"], 8))
                return

            case 7:
                pygame.time.set_timer(assets.ROSS_PAUSE_REMINDER, 20000, loops=1)

            case 8:
                state.waiting_for_rewind = True
                pygame.time.set_timer(assets.ROSS_REWIND_REMINDER, 20000, loops=1)

            case 11:
                pygame.time.set_timer(assets.ROSS_REWIND_REMINDER, 20000, loops=1)

            case 19:
                state.finished_tutorial = True

            case _: pass

        
        state.typewriter.next()
    elif event.type == pygame.KEYDOWN and state.typewriter and not state.typewriter.finished_line() and event.key == pygame.K_c: state.typewriter.skip()


    if not state.loaded_menu:
        if not state.skipped_animation and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            state.skipped_animation = True
            state.starting_opacity = 255
        return


    for slider in menu_assets.sliders.get(state.current_area, []):
        slider.handle_event(event)
    if state.current_area is MenuArea.OPTIONS and state.controls_section == "misc":
        for i in range(4):
            state.special_sliders[i].handle_event(event)

    change_binding_event(event)

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
        if state.current_area is MenuArea.MAIN_MENU:
            if state.last_played_game:
                for i in range(20, 22):
                    if state.special_buttons[i].rect.collidepoint(event.pos):
                        state.special_buttons[i].click()
            else:
                if state.special_buttons[19].rect.collidepoint(event.pos):
                    state.special_buttons[19].click()

        elif state.current_area is MenuArea.OPTIONS:
            for i in range(22, 27): # Option sections
                if state.special_buttons[i].rect.collidepoint(event.pos):
                    state.special_buttons[i].click()
                    return


            if state.controls_section == "controls":
                for i in range(33, 35): # Second bindings page
                    if state.special_buttons[i].rect.collidepoint(event.pos):
                        state.special_buttons[i].click()
                        return

                if not state.second_binding_page: # Controls 1
                    for i in range(27, 33):
                        if state.special_buttons[i].rect.collidepoint(event.pos):
                            state.special_buttons[i].click()
                            return
                else:
                    for i in range(35, 41): # Controls 2
                        if state.special_buttons[i].rect.collidepoint(event.pos):
                            state.special_buttons[i].click()
                            return

            elif state.controls_section == "colonies":
                for button in state.toggle_colonies:
                    if button.rect.collidepoint(event.pos):
                        button.click()
                        return

            elif state.controls_section == "misc":
                for i in range(41, 44):
                    if state.special_buttons[i].rect.collidepoint(event.pos):
                        state.special_buttons[i].click()
                        return

                if state.special_buttons[46].rect.collidepoint(event.pos):
                    state.special_buttons[46].click()
                    return

            elif state.controls_section == "debug":
                for i in range(47, 49):
                    if state.special_buttons[i].rect.collidepoint(event.pos):
                        state.special_buttons[i].click()
                        return
            
                if state.special_buttons[54].rect.collidepoint(event.pos):
                    state.special_buttons[54].click()
                    return

        elif state.current_area is MenuArea.SIMULATION and state.world:
            origin = state.SIM_RECT.topleft + state.offset

            cell_size = int((state.SIM_RECT.width / state.world.size) * state.zoom)
            world_rect = pygame.Rect(origin.x, origin.y, state.world.size * cell_size, state.world.size * cell_size)

            if world_rect.collidepoint(event.pos) and state.SIM_RECT.collidepoint(event.pos):
                col = int((event.pos[0] - origin.x) / cell_size)
                row = int((event.pos[1] - origin.y) / cell_size)

                pos = get_pos((row, col))
                cell = state.world.get_cell(pos)

                if cell and ((cell.name in state.disabled_cells and state.second_render_page) or (cell.name in state.disabled_cells and not state.second_render_page)): return

                state.selected_cell = state.world.get_cell(pos)
                state.selected_id = state.world.get_id(pos)
                return
            else:
                state.selected_cell = None
            
            for button in state.timeline_buttons:
                if button.rect.collidepoint(event.pos):
                    button.click()
                    return

        elif state.current_area is MenuArea.CATALOGUE:
            for i in range(49, 54):
                button = state.special_buttons[i]
                if button.rect.collidepoint(event.pos):
                    button.click()
            
            button = state.special_buttons[58]
            if button.rect.collidepoint(event.pos):
                button.click()

        elif state.current_area is MenuArea.CREDITS:
            for i in range(55, 58):
                button = state.special_buttons[i]
                if button.rect.collidepoint(event.pos):
                    button.click()
                    return

        return


    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if state.tps_change > 0: state.tps_change = 0
        if state.homebase_change: state.homebase_change = 0
        if state.health_change: state.health_change = 0
        if state.spawn_change: state.spawn_change = 0
        if state.wall_change: state.wall_change = 0
        if state.size_change: state.size_change = 0
    

    elif ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 2) or (event.type == pygame.KEYDOWN and event.key == state.bindings[KeyActions.PAN_ALIAS])) and not state.panning: #mc
        mouse_pos = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
        if state.current_area is MenuArea.SIMULATION and state.SIM_RECT.collidepoint(mouse_pos):
            pygame.event.set_grab(True); 
            pygame.mouse.set_cursor(assets.grab_cursor)
            pygame.mouse.get_rel()

            state.old_cursor_pos = mouse_pos
            state.panning = True
            return
    elif ((event.type == pygame.MOUSEBUTTONUP and event.button == 2) or (event.type == pygame.KEYUP and event.key == state.bindings[KeyActions.PAN_ALIAS])) and state.panning:
        pygame.event.set_grab(False)

        if state.current_area is MenuArea.SIMULATION and state.world and state.SIM_RECT.collidepoint(assets.get_scale_mouse_pos(pygame.mouse.get_pos())): pygame.mouse.set_cursor(assets.crosshair_cursor)
        else: pygame.mouse.set_cursor(assets.arrow_cursor)

        state.panning = False
        return
    
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # rc
        if state.current_area is MenuArea.OPTIONS:
            if state.controls_section == "controls":
                if not state.second_binding_page:
                    for i in range(27, 33):
                        if state.special_buttons[i].rect.collidepoint(event.pos):
                            state.special_buttons[i].right_click()
                else:
                    for i in range(35, 41):
                        if state.special_buttons[i].rect.collidepoint(event.pos):
                            state.special_buttons[i].right_click()
            
            elif state.controls_section == "misc":
                for i in range(41, 44):
                    if state.special_buttons[i].rect.collidepoint(event.pos):
                        state.special_buttons[i].right_click()

    elif event.type == pygame.MOUSEMOTION :
        if state.current_area is MenuArea.SIMULATION and state.world:
            if state.panning:
                if state.waiting_for_pan and not state.panned: state.panned = True

                rel = pygame.mouse.get_rel()
                dx, dy = int(rel[0] * assets.MOUSE_SCALE_X), int(rel[1] * assets.MOUSE_SCALE_Y)
                state.offset += (dx, dy)

                limit = state.SIM_RECT.width * state.zoom + (3 * state.SIM_RECT.width) / 7

                # wrap
                if state.offset.x > limit: state.offset.x -= 2 * limit
                if state.offset.x < -limit: state.offset.x += 2 * limit

                if state.offset.y > limit: state.offset.y -= 2 * limit
                if state.offset.y < -limit: state.offset.y += 2 * limit

                return
            
            mouse_pos = event.pos
            if state.SIM_RECT.collidepoint(mouse_pos) and not state.changing_seed: 
                pygame.mouse.set_cursor(assets.crosshair_cursor)

                origin = state.SIM_RECT.topleft + state.offset

                cell_size = int((state.SIM_RECT.width / state.sim_size) * state.zoom)
                world_rect = pygame.Rect(origin.x, origin.y, state.sim_size * cell_size, state.sim_size * cell_size)

                if world_rect.collidepoint(event.pos):
                    col = int((event.pos[0] - origin.x) / cell_size)
                    row = int((event.pos[1] - origin.y) / cell_size)

                    state.hovered_pos = get_pos((row, col))
                else:
                    state.hovered_pos = None
            elif state.typing_box and state.typing_box.collidepoint(mouse_pos): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else: pygame.mouse.set_cursor(assets.arrow_cursor)
        
    elif event.type == pygame.MOUSEWHEEL:
        mouse = assets.get_scale_mouse_pos(pygame.mouse.get_pos())
        _team_color_length = len(state.allowed_colonies)

        if state.current_area is MenuArea.SIMULATION and state.world and state.SIM_RECT.collidepoint(mouse) and not state.changing_seed: # Zoom
            if event.y > 0: # Up
                if state.waiting_for_pan and not state.zoomed: state.zoomed = True

                old_zoom = state.zoom_levels[state.zoom_index]
                state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index + 1))
                new_zoom = state.zoom_levels[state.zoom_index]

                # anchor to
                mouse_pos = pygame.Vector2(assets.get_scale_mouse_pos(pygame.mouse.get_pos()))
                base_cell = state.SIM_RECT.width / state.world.size
                origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
                world_pt = (mouse_pos - origin) / (base_cell * old_zoom)
                state.offset = mouse_pos - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
                state.zoom = new_zoom
                return


            if event.y < 0: # Down
                if state.waiting_for_pan and not state.zoomed: state.zoomed = True

                old_zoom = state.zoom_levels[state.zoom_index]
                state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index - 1))
                new_zoom = state.zoom_levels[state.zoom_index]

                # anchor to
                mouse_pos = pygame.Vector2(assets.get_scale_mouse_pos(pygame.mouse.get_pos()))
                base_cell = state.SIM_RECT.width / state.world.size
                origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
                world_pt = (mouse_pos - origin) / (base_cell * old_zoom)
                state.offset = mouse_pos - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
                state.zoom = new_zoom
                return
            
        elif state.current_area is MenuArea.SIMULATION and state.tps_button and state.tps_slider and (state.tps_button.rect.collidepoint(mouse) or state.tps_slider.rect.collidepoint(mouse)) and state.tps_button and not state.changing_seed:
            if event.y > 0 and state.target_tps < 40.0: # Up
                state.target_tps = round(min(state.target_tps + (event.y / 4), 40.0), 1)

                state.tps_slider.value = state.target_tps

                if state.tps_down and state.tps_down.disabled: state.tps_down.toggle()
                if state.target_tps >= 40.0 and state.tps_up and not state.tps_up.disabled: state.tps_up.toggle()

                state.tps_button.label = f"{state.target_tps}"
                state.tps_button.initialize()
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                return

            if event.y < 0 and state.target_tps > 0.1: # Down
                state.target_tps = round(max(state.target_tps + (event.y / 4), 0.1), 1)

                state.tps_slider.value = state.target_tps

                if state.tps_up and state.tps_up.disabled: state.tps_up.toggle()
                if state.target_tps <= 0.1 and state.tps_down and not state.tps_down.disabled: state.tps_down.toggle()

                state.tps_button.label = f"{state.target_tps}"
                state.tps_button.initialize()
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 0)
                pygame.time.set_timer(assets.CLEAR_TPS_TEXT, 1000, loops=1)

                return
    
        elif state.current_area is MenuArea.SIMULATION and state.changing_seed:
            if event.y > 0:
                if state.special_buttons[4].rect.collidepoint(mouse) and state.sim_homebases < min(_team_color_length, state.sim_size**2 - state.sim_walls): 
                    state.sim_homebases = max(min(state.sim_size**2 - state.sim_walls, state.sim_homebases + event.y, _team_color_length), 2)
                    check_walls()


                    button = state.special_buttons[9]
                    if state.sim_homebases >= min(_team_color_length, state.sim_size**2 - state.sim_walls) and not button.disabled: button.toggle()
                    elif state.sim_homebases < min(_team_color_length, state.sim_size**2 - state.sim_walls) and button.disabled: button.toggle()

                    button = state.special_buttons[10]
                    if state.sim_homebases <= 2 and not button.disabled: button.toggle()
                    elif state.sim_homebases > 2 and button.disabled: button.toggle()

                elif state.special_buttons[5].rect.collidepoint(mouse) and state.health_multiplier < 5.0: 
                    state.health_multiplier = max(min(5.0, round(state.health_multiplier + event.y / 10, 1)), 0.1)

                    button = state.special_buttons[11]
                    if state.health_multiplier >= 5.0 and not button.disabled: button.toggle()
                    elif state.health_multiplier < 5.0 and button.disabled: button.toggle()

                    button = state.special_buttons[12]
                    if state.health_multiplier <= 0.1 and not button.disabled: button.toggle()
                    elif state.health_multiplier > 0.1 and button.disabled: button.toggle()

                elif state.special_buttons[6].rect.collidepoint(mouse) and state.spawn_rate < 8: 
                    state.spawn_rate = max(min(8, state.spawn_rate + event.y), 1)

                    button = state.special_buttons[13]
                    if state.spawn_rate >= 8 and not button.disabled: button.toggle()
                    elif state.spawn_rate < 8 and button.disabled: button.toggle()

                    button = state.special_buttons[14]
                    if state.spawn_rate <= 1 and not button.disabled: button.toggle()
                    elif state.spawn_rate > 1 and button.disabled: button.toggle()

                elif state.special_buttons[7].rect.collidepoint(mouse) and state.sim_walls < state.sim_size**2 - state.sim_homebases: 
                    state.sim_walls = max(min(state.sim_size**2 - state.sim_homebases, state.sim_walls + event.y), 0)
                    check_homebases()

                    button = state.special_buttons[15]
                    if state.sim_walls >= state.sim_size**2 - state.sim_homebases and not button.disabled: button.toggle()
                    elif state.sim_walls < state.sim_size**2 - state.sim_homebases and button.disabled: button.toggle()

                    button = state.special_buttons[16]
                    if state.sim_walls <= 0 and not button.disabled: button.toggle()
                    elif state.sim_walls > 0 and button.disabled: button.toggle()

                elif state.special_buttons[8].rect.collidepoint(mouse) and state.sim_size < 100: 
                    state.sim_size = max(min(100, state.sim_size + event.y), 2)
                    check_walls()
                    check_homebases()

                    button = state.special_buttons[17]
                    if state.sim_size >= 100 and not button.disabled: button.toggle()
                    elif state.sim_size < 100 and button.disabled: button.toggle()

                    button = state.special_buttons[18]
                    if state.sim_size <= 0 and not button.disabled: button.toggle()
                    elif state.sim_size > 0 and button.disabled: button.toggle()

            if event.y < 0:
                if state.special_buttons[4].rect.collidepoint(mouse) and 2 < state.sim_homebases: 
                    state.sim_homebases = max(min(state.sim_size**2 - state.sim_walls, state.sim_homebases + event.y, _team_color_length), 2)
                    check_walls()


                    button = state.special_buttons[9]
                    if state.sim_homebases >= min(_team_color_length, state.sim_size**2 - state.sim_walls) and not button.disabled: button.toggle()
                    elif state.sim_homebases < min(_team_color_length, state.sim_size**2 - state.sim_walls) and button.disabled: button.toggle()

                    button = state.special_buttons[10]
                    if state.sim_homebases <= 2 and not button.disabled: button.toggle()
                    elif state.sim_homebases > 2 and button.disabled: button.toggle()

                elif state.special_buttons[5].rect.collidepoint(mouse) and 0.1 < state.health_multiplier: 
                    state.health_multiplier = max(min(5.0, round(state.health_multiplier + event.y / 10, 1)), 0.1)

                    button = state.special_buttons[11]
                    if state.health_multiplier >= 5.0 and not button.disabled: button.toggle()
                    elif state.health_multiplier < 5.0 and button.disabled: button.toggle()

                    button = state.special_buttons[12]
                    if state.health_multiplier <= 0.1 and not button.disabled: button.toggle()
                    elif state.health_multiplier > 0.1 and button.disabled: button.toggle()

                elif state.special_buttons[6].rect.collidepoint(mouse) and 1 < state.spawn_rate: 
                    state.spawn_rate = max(min(8, state.spawn_rate + event.y), 1)

                    button = state.special_buttons[13]
                    if state.spawn_rate >= 8 and not button.disabled: button.toggle()
                    elif state.spawn_rate < 8 and button.disabled: button.toggle()

                    button = state.special_buttons[14]
                    if state.spawn_rate <= 1 and not button.disabled: button.toggle()
                    elif state.spawn_rate > 1 and button.disabled: button.toggle()

                elif state.special_buttons[7].rect.collidepoint(mouse) and 0 < state.sim_walls: 
                    state.sim_walls = max(min(state.sim_size**2 - state.sim_homebases, state.sim_walls + event.y), 0)
                    check_homebases()

                    button = state.special_buttons[15]
                    if state.sim_walls >= state.sim_size**2 - state.sim_homebases and not button.disabled: button.toggle()
                    elif state.sim_walls < state.sim_size**2 - state.sim_homebases and button.disabled: button.toggle()

                    button = state.special_buttons[16]
                    if state.sim_walls <= 0 and not button.disabled: button.toggle()
                    elif state.sim_walls > 0 and button.disabled: button.toggle()

                elif state.special_buttons[8].rect.collidepoint(mouse) and 2 < state.sim_size: 
                    state.sim_size = max(min(100, state.sim_size + event.y), 2)
                    check_walls()
                    check_homebases()

                    button = state.special_buttons[17]
                    if state.sim_size >= 100 and not button.disabled: button.toggle()
                    elif state.sim_size < 100 and button.disabled: button.toggle()

                    button = state.special_buttons[18]
                    if state.sim_size <= 0 and not button.disabled: button.toggle()
                    elif state.sim_size > 0 and button.disabled: button.toggle()

        elif state.current_area is MenuArea.SIMULATION and state.world and state.TIMELINE_RECT.collidepoint(mouse) and not state.changing_seed:
            M = 50

            if event.y > 0: state.y_offset = min(state.y_offset + event.y * 40, 15)
            elif event.y < 0: state.y_offset = max(state.y_offset + event.y * 40, M * (min(10 - state.world.current_tick, 0)) + 15)


    # Below are basically just keybinds
    elif event.type == pygame.KEYDOWN and state.current_area is MenuArea.SIMULATION and state.world:
        if event.key == state.bindings[KeyActions.ZOOM_IN_ALIAS] and not state.changing_seed and not state.show_tps:
            if state.waiting_for_pan and not state.zoomed: state.zoomed = True

            old_zoom = state.zoom_levels[state.zoom_index]
            state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index + 2))
            new_zoom = state.zoom_levels[state.zoom_index]

            # anchor to
            sim_center = pygame.Vector2(state.SIM_RECT.center)

            base_cell = state.SIM_RECT.width / state.world.size
            origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
            world_pt = (sim_center - origin) / (base_cell * old_zoom)
            state.offset = sim_center - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
            state.zoom = new_zoom
            return
        
        elif event.key == state.bindings[KeyActions.ZOOM_OUT_ALIAS] and not state.changing_seed and not state.show_tps:
            if state.waiting_for_pan and not state.zoomed: state.zoomed = True

            old_zoom = state.zoom_levels[state.zoom_index]
            state.zoom_index = max(0, min(len(state.zoom_levels) - 1, state.zoom_index - 2))
            new_zoom = state.zoom_levels[state.zoom_index]

            # anchor to
            sim_center = pygame.Vector2(state.SIM_RECT.center)

            base_cell = state.SIM_RECT.width / state.world.size
            origin = pygame.Vector2(state.SIM_RECT.topleft) + state.offset
            world_pt = (sim_center - origin) / (base_cell * old_zoom)
            state.offset = sim_center - pygame.Vector2(state.SIM_RECT.topleft) - world_pt * (base_cell * new_zoom)
            state.zoom = new_zoom
            return
        
        elif event.key == state.bindings[KeyActions.REGENERATE_WORLD] and not state.changing_seed: create_world(seed=state.world.seed if state.world else None)
        
        elif event.key == state.bindings[KeyActions.PAUSE_UNPAUSE] and not state.changing_seed: toggle_pause_simulation(None)
        
        elif event.key == state.bindings[KeyActions.STEP_FORWARD] and not pygame.key.get_pressed()[pygame.K_LSHIFT] and not state.changing_seed and state.sim_pause and not state.game_end: forward(None)
        elif event.key == state.bindings[KeyActions.STEP_FORWARD] and pygame.key.get_pressed()[pygame.K_LSHIFT] and not state.changing_seed and state.sim_pause and not state.game_end: fast_forward(None)
        elif event.key == state.bindings[KeyActions.STEP_BACKWARD] and not pygame.key.get_pressed()[pygame.K_LSHIFT] and not state.changing_seed and state.sim_pause and state.world.get_snapshot(1)[0]: rewind(None)
        elif event.key == state.bindings[KeyActions.STEP_BACKWARD] and pygame.key.get_pressed()[pygame.K_LSHIFT] and not state.changing_seed and state.sim_pause and state.world.get_snapshot(2)[0]: fast_rewind(None)