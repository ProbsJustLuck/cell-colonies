from dataclasses import dataclass
import pygame

from classes.position import Position
from util.assets import TEXT_BUBBLE, BOB_ROSS
from util.game_states import States as state
from util.ui_helpers import get_font, draw_text


@dataclass
class Message:
    lines: list[str]
    id: int = -1


class Typewriter:
    def __init__(self, font_size: int, speed: int = 30):
        self.__font_size = font_size
        self.__speed = speed

        self.__queue: list[Message] = []
        self.__current: Message | None = None
        self.__lines: list[str] = []

        self.__progress = 0
        self.__accum = 0

        self.__done = True


    @property
    def done(self) -> bool: return self.__done


    @property
    def id(self) -> int: return self.__current.id if self.__current else -1


    def has_lines_left(self) -> bool: return True if self.__queue or self.__lines else False


    def finished_line(self) -> bool: return self.__progress >= self.__get_length()


    def not_rude(self) -> bool: return True if self.__current and (self.__current.id == -2 or self.__current.id == -3 or self.__current.id == -4) else False


    def tps_reset(self) -> bool: return True if self.__current and (self.__current.id == -3 or self.__current.id == -4) else False


    def tps_reset_2(self) -> bool: return True if self.__current and self.__current.id == -4 else False


    def tps_reset_3(self) -> bool: return True if self.__current and self.__current.id == -5 else False


    def clear(self) -> None:
        self.__queue = []
        self.__current = None
        self.__lines = []


    def reset_to_queue(self) -> None:
        if self.__current: 
            self.__queue.insert(0, self.__current)
            self.__lines = []
            self.__current = None


    def queue(self, message: Message) -> None:
        if not message.lines: return
        
        self.__queue.append(message)
        if self.__done: self.next()


    def prepend(self, message: Message) -> None:
        if not message.lines: return

        self.__queue.insert(0, message)
        self.next()

    def next(self) -> None:
        state.finished_timer = 0

        if not self.__queue:
            self.__done = True
            self.__current = None
            self.__lines = []
            return
        
        self.__current = self.__queue.pop(0)
        self.__lines = self.__current.lines
        self.__progress = 0
        self.__done = False


    def __get_length(self) -> int:
        sum = 0
        for line in self.__lines:
            sum += len(line)

        return sum
    

    def skip(self) -> None:
        if self.__done: return

        self.__progress = self.__get_length()


    def reset_progress(self) -> None: 
        self.__progress = 0
        if self.__done: self.__done = False


    def update(self, downtime: int) -> None:
        if self.__done: return

        self.__accum += downtime * self.__speed
        chars = self.__accum // 1000

        if chars:
            self.__accum -= chars * 1000
            self.__progress += chars

            length = self.__get_length()

            if self.__progress >= length:
                self.__progress = length
                self.__done = True


    def draw(self, screen: pygame.Surface, pos: tuple[int, int], line_spacing: int = 32) -> None:
        if not self.__lines: return
        remaining = self.__progress

        screen.blit(TEXT_BUBBLE, (pos[0] - 25, pos[1] - 20))

        screen.blit(BOB_ROSS, (pos[0] + 300, pos[1] + 20))

        draw_text(Position(pos[0], pos[1] + 4), "Bob Ross", "#4F1212", 50)
        draw_text(Position(pos[0] + 2, pos[1] + 4), "Bob Ross", "#4F1212", 50)

        y = pos[1] + 40
        for line in self.__lines:
            l = min(len(line), remaining)
            text = line[:l]

            surf = get_font(self.__font_size).render(text, False, "black")
            screen.blit(surf, (pos[0], y))
            remaining -= l
            y += line_spacing