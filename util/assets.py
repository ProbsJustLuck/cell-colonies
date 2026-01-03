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
big_font = pygame.font.Font("assets/font/Pixeltype.ttf", 50)

# Cursors
mouse_grab = pygame.image.load("assets/menu/cursor_grab.png").convert_alpha()
mouse_grab = pygame.transform.scale(mouse_grab, (32, 32))
grab_hotspot = (16, 10)

grab_cursor = pygame.cursors.Cursor(grab_hotspot, mouse_grab)
arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
crosshair_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

# Cells
cell_scale_sizes= (64, 64)
## Homebases
base_homebase = pygame.image.load("assets/cells/homebase.png").convert_alpha()
base_homebase = pygame.transform.scale(base_homebase, cell_scale_sizes)
HOMEBASE_ICON = pygame.transform.scale(pygame.image.load("assets/menu/homebase_icon.png").convert_alpha(), (48, 48))

## Attackers
base_attacker_up = pygame.image.load("assets/cells/attacker_up.png").convert_alpha()
base_attacker_up = pygame.transform.scale(base_attacker_up, cell_scale_sizes)

base_attacker_down = pygame.image.load("assets/cells/attacker_down.png").convert_alpha()
base_attacker_down = pygame.transform.scale(base_attacker_down, cell_scale_sizes)

base_attacker_right = pygame.image.load("assets/cells/attacker_right.png").convert_alpha()
base_attacker_right = pygame.transform.scale(base_attacker_right, cell_scale_sizes)

base_attacker_left = pygame.image.load("assets/cells/attacker_left.png").convert_alpha()
base_attacker_left = pygame.transform.scale(base_attacker_left, cell_scale_sizes)

## Rotators
base_rotator = pygame.image.load("assets/cells/rotator.png").convert_alpha()
base_rotator = pygame.transform.scale(base_rotator, cell_scale_sizes)

## Walls
wall = pygame.image.load("assets/cells/wall.png").convert_alpha()
wall = pygame.transform.scale(wall, cell_scale_sizes)
WALL_ICON = pygame.transform.scale(pygame.image.load("assets/menu/wall_icon.png").convert_alpha(), (40, 40))

# Icons
COPY_ICON = pygame.transform.scale(pygame.image.load("assets/menu/copy_icon.png").convert_alpha(), (52, 52))
PASTE_ICON = pygame.transform.scale(pygame.image.load("assets/menu/paste_icon.png").convert_alpha(), (48, 48))
REGENERATE_ICON = pygame.transform.scale(pygame.image.load("assets/menu/regenerate_icon.png").convert_alpha(), (32, 32))
HEART_ICON = pygame.transform.scale(pygame.image.load("assets/menu/pixel_heart.png").convert_alpha(), (35, 35))
HOURGLASS_ICON = pygame.transform.scale(pygame.image.load("assets/menu/hourglass.png").convert_alpha(), (38, 38))


# Yellowboss
TEXT_BUBBLE = pygame.transform.scale(pygame.image.load("assets/yellowboss/chat_bubble.png").convert_alpha(), (500, 250))
BOB_ROSS = pygame.transform.scale(pygame.image.load("assets/yellowboss/bob_ross.png").convert_alpha(), (204 * 1.3, 340 * 1.3))


# Events
CLEAR_TPS_TEXT = pygame.USEREVENT + 1
CLEAR_HOMEBASE_TEXT = pygame.USEREVENT + 2
CLEAR_HEALTH_TEXT = pygame.USEREVENT + 3
CLEAR_SPAWN_TEXT = pygame.USEREVENT + 4
CLEAR_WALL_TEXT = pygame.USEREVENT + 5
CLEAR_SIZE_TEXT = pygame.USEREVENT + 6

ROSS_CALL = pygame.USEREVENT + 7
ROSS_PAN = pygame.USEREVENT + 8
ROSS_PAN_REMINDER = pygame.USEREVENT + 9