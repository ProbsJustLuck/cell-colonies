import pygame

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

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for button in menu_assets.buttons.get(state.current_area, []):
                if not button.rect: continue
                if button.rect.collidepoint(event.pos):
                    button.click()
                    break
            return
