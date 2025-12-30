import pygame

from constants import Constants

screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT), display=1)

main_menu_background = pygame.transform.smoothscale(
    pygame.image.load("assets/menu/main_menu.jpg").convert(),
    screen.get_size()
)
simulation_background = pygame.transform.smoothscale(
    pygame.image.load("assets/menu/simulation.jpg").convert(),
    screen.get_size()
)

rotation_arrow = pygame.transform.smoothscale(
    pygame.image.load("assets/menu/rotation_arrow.png").convert_alpha(),
    (25, 25)
)

pygame.mixer.init()
pygame.font.init()
game_font = pygame.font.Font("assets/font/Pixeltype.ttf", 20)