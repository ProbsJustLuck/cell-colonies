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
    def __init__(self, rect: pygame.Rect, orientation: Literal["h", "v"] = "h", min_value: float = 0.0, max_value: float = 1.0, steps: Optional[int] = None, value: float = 0.0, on_change: Optional[Callable[[float], None]] = None, snap_on_release: bool = True, style: SliderStyle = SliderStyle()):
        self.rect = rect

        self.orientation = orientation

        self.min_value = min_value
        self.max_value = max_value

        self.steps = steps
        self.value = value

        self.on_change = on_change
        self.snap_on_release = snap_on_release

        if style: self.style = style

        self.__dragging = False

    @property
    def progress(self) -> float:
        span = self.max_value - self.min_value
        if span == 0: return 0.0
        else: return(self.value - self.min_value) / span

    def set_value(self, progress: float, on_change: bool) -> None:
        progress = max(0.0, min(1.0, progress))

        if self.steps and self.snap_on_release and not self.__dragging: progress = round(progress * (self.steps-1)) / (self.steps-1) # snap to steps

        val = self.min_value + progress * (self.max_value - self.min_value)
        if val != self.value:
            self.value = val
            if on_change and self.on_change: self.on_change(self.value)


    def __pos_to_progress(self, pos: tuple[int, int]) -> float:
        if self.orientation == "h":
            rel = pos[0] - self.rect.left
            length = self.rect.width
        else:
            rel = pos[1] - self.rect.top
            length = self.rect.height

        return 0.0 if length <= 1 else rel / (length - 1)


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.__dragging = True
                self.set_value(self.__pos_to_progress(event.pos), on_change=True)

        elif event.type == pygame.MOUSEMOTION and self.__dragging:
            self.set_value(self.__pos_to_progress(event.pos), on_change=True)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.__dragging:
            self.__dragging = False
            if self.steps and self.snap_on_release:
                self.set_value(self.__pos_to_progress(event.pos), on_change=True)


    def draw(self, surface: pygame.Surface) -> None:
        # track line
        if self.orientation == "h": pygame.draw.line(surface, self.style.track_color, (self.rect.left, self.rect.centery), (self.rect.right, self.rect.centery), 3)
        else: pygame.draw.line(surface, self.style.track_color, (self.rect.centerx, self.rect.top), (self.rect.centerx, self.rect.bottom), 3)

        # ticks
        if self.steps:
            for i in range(self.steps):
                if self.orientation == "h":
                    x = self.rect.left + i / (self.steps - 1) * (self.rect.width - 1)
                    pygame.draw.line(surface, self.style.track_color, (x, self.rect.centery - 1), (x, self.rect.centery + self.style.tick_size), 3)
                else:
                    y = self.rect.top + i / (self.steps - 1) * (self.rect.height - 1)
                    pygame.draw.line(surface, self.style.track_color, (self.rect.centerx - 1, y), (self.rect.centerx + self.style.tick_size, y), 3)

        # head
        head_rect = pygame.Rect(0, 0, self.style.head_radius * 2, self.style.head_radius * 2)
        border_rect = pygame.Rect(0, 0, self.style.head_radius * 2 + 6, self.style.head_radius * 2 + 6)
        if self.orientation == "h":
            head_rect.center = (int(self.rect.left + self.progress * (self.rect.width - 1)), int(self.rect.centery))
            border_rect.center = (int(self.rect.left + self.progress * (self.rect.width - 1)), int(self.rect.centery))
        else:
            head_rect.center = (int(self.rect.centerx), int(self.rect.top + self.progress * (self.rect.height - 1)))
            border_rect.center = (int(self.rect.centerx), int(self.rect.top + self.progress * (self.rect.height - 1)))

        pygame.draw.rect(surface, "#000000", border_rect)
        pygame.draw.rect(surface, self.style.head_color, head_rect)
        
