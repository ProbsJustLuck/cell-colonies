from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable
import pygame

from classes.ui.key_actions import KeyActions
from util.game_states import States as state
from util.ui_helpers import create_text, add_bg_to_text_dimensions, add_background_to_text, add_outline_to_image
from util import assets


pending_tooltip: Callable[[], None] | None = None
skip_hover: bool = False


class ButtonType(Enum):
    NORMAL = auto()
    TOGGLE = auto()


@dataclass
class ButtonStyle:
    font_size: int = 35
    padding: int = 9
    border: int = 3

    opacity: int = 255
    disabled_opacity: int = 120
    overwrite_opacity: int = -1 # bandaid solution but it WORKS
    selected_opacity: int = 255

    # Transformations
    width: int | None = None
    height: int | None = None
    scale: float = 1.0

    # Colors
    base: str = "#a5a5a5"
    hover: str = "#707070"
    selected: str = "#515151"
    disabled: str = "#8b8b8b"
    text: str = "black"
    
    tooltip_scale: float = 0.8


    def make_surface(self, label: str, color: tuple[int, int, int] | str, disabled: bool = False, selected: bool = False, double_text: bool = False):
        font_size = max(1, int(self.font_size * self.scale))
        padding = max(1, int(self.padding * self.scale))
        text = create_text(label, self.text, font_size)
        if double_text:
            text1 = create_text(label, self.text, font_size)
            text.blit(text1, (1, 0))

        # background sizing: override width/height if provided
        bg_width = self.width or text.get_width() + 2 * padding
        bg_height = self.height or text.get_height() + 2 * padding

        base = add_bg_to_text_dimensions(text, color, bg_width, bg_height, padding)
        surf = add_outline_to_image(base, self.border, (0, 0, 0))

        if self.overwrite_opacity >= 0:
            surf.set_alpha(self.overwrite_opacity)
        elif disabled:
            surf.set_alpha(self.disabled_opacity)
        elif selected:
            surf.set_alpha(self.selected_opacity)
        else:
            surf.set_alpha(self.opacity)

        return surf
    

    def make_tooltip(self, msg: str) -> pygame.Surface:
        font = max(1, int(self.font_size * self.scale * self.tooltip_scale))
        padding = max(1, int((self.padding + 6) * self.scale * self.tooltip_scale)) 
        text = create_text(msg, self.text, font)
        bg = add_background_to_text(text, "#C5C5C5", padding)

        return add_outline_to_image(bg, self.border, (0, 0, 0))

@dataclass
class Button:
    label: str
    center: tuple[int, int]
    tooltip: str = ""
    type: ButtonType = ButtonType.NORMAL
    style: ButtonStyle = field(default_factory=ButtonStyle)

    clicked: bool = False
    disabled: bool = False
    selected_override: bool = False

    outline_text: bool = False

    id: str | KeyActions | None = None
    on_enter: Callable[["Button"], None] | None = None
    on_leave: Callable[["Button"], None] | None = None

    on_right_click: Callable[["Button"], None] | None = None

    _surfaces: dict[str, pygame.Surface] = field(default_factory=dict[str, pygame.Surface])
    rect: pygame.Rect = field(default_factory=pygame.Rect)

    def initialize(self):  
        self._surfaces = {
            "base": self.style.make_surface(self.label, self.style.base, double_text=self.outline_text),
            "hover": self.style.make_surface(self.label, self.style.hover, double_text=self.outline_text),
            "selected": self.style.make_surface(self.label, self.style.selected, selected=True, double_text=self.outline_text),
            "disabled": self.style.make_surface(self.label, self.style.disabled, True, double_text=self.outline_text)
        }
        self.rect = self._surfaces["base"].get_rect(center=self.center)


    def toggle(self): self.disabled = not self.disabled


    def click(self):
        if self.disabled: return
        if self.type is ButtonType.TOGGLE:
            self.clicked = not self.clicked
            if self.clicked and self.on_enter:
                self.on_enter(self)
            if not self.clicked and self.on_leave:
                self.on_leave(self)
        else: # normal
            if self.on_enter: self.on_enter(self)


    def right_click(self):
        if self.disabled: return
        if self.on_right_click: self.on_right_click(self)


    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]):
        if self.disabled: button_state = "disabled"

        elif self.clicked and not self.selected_override: button_state = "selected"

        elif not state.skip_button_hover and self.rect and self.rect.collidepoint(mouse_pos): button_state = "hover"

        else: button_state = "base"
        surf = self._surfaces[button_state]

        if self.style.overwrite_opacity >= 0:
            surf.set_alpha(self.style.overwrite_opacity)
        elif self.disabled:
            surf.set_alpha(self.style.disabled_opacity)
        elif self.clicked:
            surf.set_alpha(self.style.selected_opacity)
        else:
            surf.set_alpha(self.style.opacity)

        self.rect = surf.get_rect(center=self.center)

        screen.blit(surf, self.rect)
        if self.tooltip and (button_state == "hover" or (button_state == "selected" and self.rect and self.rect.collidepoint(mouse_pos))):
            global pending_tooltip
            pending_tooltip = lambda tooltip=self.tooltip, rect=self.rect.copy(), pos=mouse_pos, style=self.style: render_tooltip(tooltip, rect, pos, style)

def render_tooltip(msg: str, rect: pygame.Rect, mouse_pos: tuple[int, int], style: ButtonStyle):
    tooltip = style.make_tooltip(msg)

    size = max(1, int(style.font_size * 0.5 * style.scale * style.tooltip_scale))
    tooltip.blit(create_text(">>", "#000000", size), (5, 4))

    assets.screen.blit(tooltip, tooltip.get_rect(bottomleft=mouse_pos))
