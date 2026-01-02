from dataclasses import dataclass
import pygame
from enum import Enum, auto

from util.assets import ANGER, CONFUSED, HAPPY, IDLE, SAD, TERROR, TEXT_BUBBLE
from util.ui_helpers import get_font


class Emotion(Enum):
    ANGER = auto()
    CONFUSED = auto()
    HAPPY = auto()
    IDLE = auto()
    SAD = auto()
    TERROR = auto()

@dataclass
class Message:
    emotion: Emotion
    lines: list[str]


class Typewriter:
    def __init__(self, font_size: int, speed: int=30):
        self.__font_size = font_size
        self.__speed = speed

        self.__queue: list[Message] = []
        self.__current: Message | None = None
        self.__lines: list[str] = []

        self.__progress = 0
        self.__accum = 0

        self.__SPRITES = {
            Emotion.ANGER: ANGER,
            Emotion.CONFUSED: CONFUSED,
            Emotion.HAPPY: HAPPY,
            Emotion.IDLE: IDLE,
            Emotion.SAD: SAD,
            Emotion.TERROR: TERROR
        }

        self.__done = True


    def queue(self, emotion: Emotion, lines: list[str]) -> None:
        if not lines: return

        self.__queue.append(Message(emotion, lines))
        if self.__done: self.start()


    def start(self) -> None:
        if not self.__queue:
            self.__done = True
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


    def reset_progress(self) -> None: self.__progress = 0


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

        y = pos[1]
        for line in self.__lines:
            l = min(len(line), remaining)
            text = line[:l]

            surf = get_font(self.__font_size).render(text, False, "black")
            screen.blit(surf, (pos[0], y))
            remaining -= l
            y += line_spacing

        if self.__current:
            screen.blit(self.__SPRITES[self.__current.emotion], (pos[0] + 350, pos[1] + 80))