import pygame
from util.game_states import States as state
from util.game_actions import quit
from util.menu_assets import main_menu_buttons
from classes.ui.button import Button


def _get_current_buttons_list() -> list[Button]:
    if state.in_main_menu: return main_menu_buttons
    return []


def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT: quit()

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for button in _get_current_buttons_list():
                if not button.rect: continue
                if button.rect.collidepoint(event.pos):
                    button.click()
                    break
            return
