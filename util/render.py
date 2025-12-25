import pygame

import util.assets as assets
from util.game_states import States as state
from classes.position import Position
from classes.lerp import Lerp
from constants import Constants

STARTING_SIZE = 300
ENDING_SIZE = 160

_base1: pygame.Surface | None = None
_base2: pygame.Surface | None = None

_title_scale_lerp: Lerp | None = None
_title_offset_lerp: Lerp | None = None

def render_start_screen() -> None:
    global _base1, _base2
    if _base1 is None or _base2 is None:
        _base1 = add_outline_to_image(create_text("Cell", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))
        _base2 = add_outline_to_image(create_text("Colonies", "#b7b7b7", STARTING_SIZE), 3, (0, 0, 0))

    assets.screen.blit(assets.background, assets.background.get_rect(topleft = (0, 0)))

    if state.starting_opacity < 255:
        state.starting_opacity += 2

        _base1.set_alpha(state.starting_opacity)
        _base2.set_alpha(state.starting_opacity)
        assets.screen.blit(_base1, _base1.get_rect(center = (Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2 - _base1.get_height() / 2)))
        assets.screen.blit(_base2, _base2.get_rect(center = (Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2 + (STARTING_SIZE / 6))))
        return
    
    global _title_scale_lerp, _title_offset_lerp
    if not _title_scale_lerp or not _title_offset_lerp:
        _title_scale_lerp = Lerp(STARTING_SIZE, ENDING_SIZE, 2000, lambda t: 4*t*t*t if t < 0.5 else 1 - ((-2*t + 2)**3.5) / 2)
        _title_offset_lerp = Lerp(0, 160, 2000, lambda t: 4*t*t*t if t < 0.5 else 1 - ((-2*t + 2)**3.5) / 2)


    now = pygame.time.get_ticks()
    scale = _title_scale_lerp.value(now) / STARTING_SIZE
    offset = _title_offset_lerp.value(now)

    # scale once per frame based on the base sizes
    text1 = pygame.transform.smoothscale(
        _base1,
        (int(_base1.get_width() * scale), int(_base1.get_height() * scale))
    )
    text2 = pygame.transform.smoothscale(
        _base2,
        (int(_base2.get_width() * scale), int(_base2.get_height() * scale))
    )

    mid_y = Constants.SCREEN_HEIGHT // 2
    gap = (_base1.get_height() * scale) / 2  # keeps spacing relative to text scales

    assets.screen.blit(text1, text1.get_rect(center=(Constants.SCREEN_WIDTH // 2, mid_y - gap - offset)))
    assets.screen.blit(text2, text2.get_rect(center=(Constants.SCREEN_WIDTH // 2, mid_y - offset + (STARTING_SIZE / 6) * scale)))

    if not _title_scale_lerp.done: return

    # START GAME
    # state.start_game_rect = create_button(400, 200, "START GAME", state.starting_opacity)

    # # INFOPEDIA
    # state.infopedia_rect = create_button(475, 250, "INFOPEDIA", state.starting_opacity)

    # # CONTROLS
    # state.controls_rect = create_button(325, 250, "OPTIONS", state.starting_opacity)

    # # QUIT
    # state.quit_rect = create_button(400, 300, "QUIT GAME", state.starting_opacity)


def get_font(size: int) -> pygame.font.Font:
    if size not in state.font_cache:
        state.font_cache[size] = pygame.font.Font("assets/font/Pixeltype.ttf", size)
    return state.font_cache[size]


def draw_text(pos: Position, string: str, color: str, size: int = 20, bold: bool=False, italic: bool=False) -> None:
    """
    Draws text at a specific location on screen.

    Automatically generates the font and text properties then renders on screen.

    Args:
        x (int): Represents the x coordinate of the center of the text.
        y (int): Represents the y coordinate of the center of the text.
        string (str): The string to be drawn on screen.
        color (str): The color of the text.
        size (int, optional): The size of the text. Defaults to 20.
        bold (bool, optional): Whether the text is bold or not. Defaults to False.
        italic (bool, optional): Whether the text is in italics or not. Defaults to False

    Returns:
        None
    """

    font = get_font(size)
    font.set_bold(bold)
    font.set_bold(italic)

    text = font.render(string, False, color)
    textbox = text.get_rect(center = (pos.x, pos.y))

    assets.screen.blit(text, textbox)


def create_text(string: str, color: str, size: int = 20, bold: bool=False, italic: bool=False) -> pygame.Surface:
    """
    Creates and returns a text object with certain attributes.

    Args:
        string (str): The text to be created
        color (str): The color of the text
        size (int, optional): The size of the text. Defaults to 20
        bold (bool, optional): Whether the text is bold or not. Defaults to False
        italic (bool, optional): Whether the text is italicized or not. Defaults to False

    Returns:
        pygame.Surface
    """

    font = get_font(size)
    font.set_bold(bold)
    font.set_italic(italic)
    text = font.render(string, False, color)
    return text


def add_outline_to_image(image: pygame.Surface, thickness: int, outline_color: tuple[int, int, int] | str) -> pygame.Surface:
    """
    Outlines a surface with an outline color.

    Args:
        image (pygame.Surface): The original surface to be outlined
        thickness (int): How many pixels thick the outline should be.
        color (tuple | str): The color of the outline (RGB or hex)

    Returns:
        pygame.Surface: A new surface, sized (orig_width + 2*thickness, 
                        orig_height + 2*thickness), containing the outlined image.
    """
    outlined_surf = pygame.Surface((image.get_width()  + 2 * thickness, image.get_height() + 2 * thickness), flags=pygame.SRCALPHA)  # allow per-pixel alpha, blitting without it can be silly
    
    base_copy = image.copy().convert_alpha()
    black_copy = image.copy().convert_alpha()
    color = pygame.Color(outline_color) if isinstance(outline_color, str) else pygame.Color(*outline_color) # allows string support for colors
    black_copy.fill((color.r, color.g, color.b, 255), None, pygame.BLEND_RGBA_MULT)


    # Cool method to add a border around an image
    # Make 8 black copies of the image, then blit the original onto the middle.
    for dx in range(-thickness, thickness + 1): # could be laggy? its 8x around (before it was 4 but looked funny)
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue # skip the center
            outlined_surf.blit(black_copy, (dx + thickness, dy + thickness))

    outlined_surf.blit(base_copy, (thickness, thickness))

    return outlined_surf