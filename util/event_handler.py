
import pygame
import util.game_states as state

def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT:
        state.running = False