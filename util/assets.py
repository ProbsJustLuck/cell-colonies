import pygame

from constants import Constants

screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT), display=1)
background = pygame.transform.smoothscale(
    pygame.image.load("assets/menu/background.jpg").convert(),
    screen.get_size()
)

pygame.mixer.init()
pygame.font.init()
game_font = pygame.font.Font("assets/font/Pixeltype.ttf", 20)
scaling_font = pygame.font.Font("assets/font/Pixeltype.ttf", 25)
bold_font = pygame.font.Font("assets/font/Pixeltype.ttf", 29)
bold_font.bold = True
small_font = pygame.font.Font("assets/font/Pixeltype.ttf", 15)