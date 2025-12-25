import time
start_time = time.time()

import pygame

import util.assets as assets # type: ignore
import util.game_states as states
from util.event_handler import event_handler
from classes.world_manager import WorldManager # type: ignore

pygame.init()
pygame.display.set_caption("What's up danger")
clock = pygame.Clock()

print(f"Load took {time.time() - start_time: .4f}s")

while states.running:
    for event in pygame.event.get(): event_handler(event)

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS