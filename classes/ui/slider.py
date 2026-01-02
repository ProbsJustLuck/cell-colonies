import pygame
from typing import Callable, Literal, Optional


class SliderStyle:
    def __init__(self, track_color: tuple[int, int, int] = (60, 60, 60), fill_color: tuple[int, int, int] = (120, 120, 120), head_color: tuple[int, int, int] = (200, 200, 200), head_radius: int = 6, tick_color: tuple[int, int, int] = (100, 100, 100), tick_size: int = 6):
        self.track_color = track_color
        self.fill_color = fill_color
        self.head_color = head_color
        self.head_radius = head_radius
        self.tick_size = tick_size


class Slider:
    def __init__(self, rect: pygame.Rect, orientation: Literal["h", "v"] = "h", min_value: float = 0.0, max_value: float = 1.0, steps: Optional[int] = None, value: float = 0.0, on_change: Optional[Callable[[float], None]] = None, snap: bool = True, style: SliderStyle = SliderStyle()):
        self.__rect = rect

        self.__orientation = orientation

        self.__min_value = min_value
        self.__max_value = max_value

        self.__steps = steps
        self.__value = value

        self.__on_change = on_change
        self.__snap = snap

        if style: self.__style = style

        self.__dragging = False


    @property
    def rect(self) -> pygame.Rect: return self. __rect


    @property
    def value(self) -> float: return self.__value


    @value.setter
    def value(self, value: float) -> None: self.__value = value


    @property
    def style(self) -> SliderStyle: return self.__style


    @property
    def progress(self) -> float:
        span = self.__max_value - self.__min_value
        if span == 0: return 0.0
        else: return(self.__value - self.__min_value) / span


    def set_value(self, progress: float, on_change: bool) -> None:
        progress = max(0.0, min(1.0, progress))

        if self.__steps and self.__snap and not self.__dragging: progress = round(progress * (self.__steps - 1)) / (self.__steps - 1) # snap to steps

        val = self.__min_value + progress * (self.__max_value - self.__min_value)
        if val != self.__value:
            self.__value = val
            if on_change and self.__on_change: self.__on_change(self.__value)


    def __pos_to_progress(self, pos: tuple[int, int]) -> float:
        if self.__orientation == "h":
            rel = pos[0] - self.__rect.left
            length = self.__rect.width
        else:
            rel = pos[1] - self.__rect.top
            length = self.__rect.height

        return 0.0 if length <= 1 else rel / (length - 1)


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.__rect.collidepoint(event.pos):
                self.__dragging = True
                self.set_value(self.__pos_to_progress(event.pos), on_change=True)

        elif event.type == pygame.MOUSEMOTION and self.__dragging:
            self.set_value(self.__pos_to_progress(event.pos), on_change=True)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.__dragging:
            self.__dragging = False
            if self.__steps and self.__snap:
                self.set_value(self.__pos_to_progress(event.pos), on_change=True)


    def draw(self, surface: pygame.Surface) -> None:
        # track line
        if self.__orientation == "h": pygame.draw.line(surface, self.__style.track_color, (self.__rect.left, self.__rect.centery), (self.__rect.right, self.__rect.centery), 3)
        else: pygame.draw.line(surface, self.__style.track_color, (self.__rect.centerx, self.__rect.top), (self.__rect.centerx, self.__rect.bottom), 3)

        # ticks
        if self.__steps:
            for i in range(self.__steps):
                if self.__orientation == "h":
                    x = self.__rect.left + i / (self.__steps - 1) * (self.__rect.width - 1)
                    pygame.draw.line(surface, self.__style.track_color, (x, self.__rect.centery - 1), (x, self.__rect.centery + self.__style.tick_size), 3)
                else:
                    y = self.__rect.top + i / (self.__steps - 1) * (self.__rect.height - 1)
                    pygame.draw.line(surface, self.__style.track_color, (self.__rect.centerx - 1, y), (self.__rect.centerx + self.__style.tick_size, y), 3)

        # head
        head_rect = pygame.Rect(0, 0, self.__style.head_radius * 2, self.__style.head_radius * 2)
        border_rect = pygame.Rect(0, 0, self.__style.head_radius * 2 + 6, self.__style.head_radius * 2 + 6)
        if self.__orientation == "h":
            head_rect.center = (int(self.__rect.left + self.progress * (self.__rect.width - 1)), int(self.__rect.centery))
            border_rect.center = (int(self.__rect.left + self.progress * (self.__rect.width - 1)), int(self.__rect.centery))
        else:
            head_rect.center = (int(self.__rect.centerx), int(self.__rect.top + self.progress * (self.__rect.height - 1)))
            border_rect.center = (int(self.__rect.centerx), int(self.__rect.top + self.progress * (self.__rect.height - 1)))

        pygame.draw.rect(surface, "#000000", border_rect)
        pygame.draw.rect(surface, self.__style.head_color, head_rect)
        
