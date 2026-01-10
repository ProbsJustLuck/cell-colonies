import pygame

from util.game_states import States as state
from constants import Constants

RESOLUTIONS: dict[int, tuple[int, int]] = {
    0: (720, 420),
    1: (858, 500),
    2: (1029, 600),
    3: (1200, 700),
    4: (1320, 770),
    5: (1714, 1000),
    6: (2057, 1200)
}

screen = pygame.Surface((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
display_screen = pygame.display.set_mode(RESOLUTIONS[3], display=Constants.DISPLAY_MONITOR)

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
cell_scale_sizes= (64, 65)
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

## Teleporters
base_teleporter = pygame.image.load("assets/cells/teleporter.png").convert_alpha()
base_teleporter = pygame.transform.scale(base_teleporter, cell_scale_sizes)

## Annihilator
base_annihilator = pygame.image.load("assets/cells/annihilator.png").convert_alpha()
base_annihilator = pygame.transform.scale(base_annihilator, cell_scale_sizes)


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

## Ross
ROSS_CALL = pygame.USEREVENT + 7
ROSS_PAN = pygame.USEREVENT + 8
ROSS_PAN_REMINDER = pygame.USEREVENT + 9

ROSS_PAUSE = pygame.USEREVENT + 10
ROSS_PAUSE_REMINDER = pygame.USEREVENT + 11

ROSS_REWIND = pygame.USEREVENT + 12
ROSS_REWIND_REMINDER = pygame.USEREVENT + 13

## Misc
REVERT_VIDEO_CHANGES = pygame.USEREVENT + 14
CYCLE_CELL_COLOR = pygame.USEREVENT + 15

# Catalogue
locked_icon = pygame.transform.scale(pygame.image.load("assets/menu/locked.png").convert_alpha(), (30, 40))
unlocked_icon = pygame.transform.scale(pygame.image.load("assets/menu/unlocked.png").convert_alpha(), (30, 40))

# fix mouse scaling for different resolution
MOUSE_SCALE_X = Constants.SCREEN_WIDTH / RESOLUTIONS[state.current_res][0]
MOUSE_SCALE_Y = Constants.SCREEN_HEIGHT / RESOLUTIONS[state.current_res][1]


def get_scale_mouse_pos(pos: tuple[int, int]) -> tuple[int, int]:
    width, height = pygame.display.get_window_size()
    MOUSE_SCALE_X = Constants.SCREEN_WIDTH / width
    MOUSE_SCALE_Y = Constants.SCREEN_HEIGHT / height
    
    return (int(pos[0] * MOUSE_SCALE_X), int(pos[1] * MOUSE_SCALE_Y))