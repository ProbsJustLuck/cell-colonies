import pygame
from util.game_states import States as state

def event_handler(event: pygame.Event):
    if event.type == pygame.QUIT:
        state.running = False