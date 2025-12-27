# Used to stop the messy circular imports

import pygame
from util.game_states import States as state
from util import assets
from classes.position import Position


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
    textbox = text.get_rect(topleft = (pos.x, pos.y))

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


def add_background_to_text(text: pygame.Surface, bg_color: tuple[int, int, int] | str, padding: int=1) -> pygame.Surface:
    """
    Adds a background color to text with a specific padding.
    
    Args:
        text (pygame.Surface): The text surface to be adjusted.
        bg_color (tuple | str): The background color to be set to
        padding (int, optional): The padding of the background text (multiplied by a factor of 2). Defaults to 1
    
    Returns:
        pygame.Surface: The updated text with a new background
    """
    bounds = text.get_bounding_rect()    
    width, height = bounds.size
    
    width += 2 * padding
    height += 2 * padding
    surf = pygame.Surface((width, height))

    surf.fill(bg_color)
    surf.blit(text, (padding, padding), area=bounds) # Only grab pixels from the bounds
    return surf


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


def add_bg_to_text_dimensions(text: pygame.Surface, bg_color: tuple[int, int ,int] | str, width: int, height: int, padding: int=1) -> pygame.Surface:   
    """
    Adds a background to text with a specific background width.

    Args:
        text (pygame.Surface): The text to add a background to
        bg_color (tuple | str): The background color of the text
        width (int): The width of the background
        padding (int, optional): The padding of the background. Defaults to 1
    """
    bounds = text.get_bounding_rect()
    bounds_width, bounds_height = bounds.size

    surf = pygame.Surface((width, height))
    surf.fill(bg_color)

    padding_width = width - 2 * padding
    padding_height = height - 2 * padding
    x = padding + (padding_width - bounds_width) // 2    # allow negative to truly center
    y = padding + (padding_height - bounds_height) // 2    # allow negative to truly center

    surf.blit(text, (x, y), area=bounds)
    return surf