from typing import Callable
import pygame

class Lerp:
    """
    A class that performs linear interpolation between two values over a specified duration, with optional easing. Uses "a + (b - a) * w" formula.

    Args:

        start (float): The starting value of the interpolation.
        end (float): The ending value of the interpolation.
        duration_ms (int): The duration of the interpolation in milliseconds.
        ease (Callable[[float], float], optional): An easing function that takes a float between 0 and 1 and returns a float between 0 and 1. Defaults to linear easing.

    Methods:
        value(now_ms: int) -> float: Returns the interpolated value at the given time in milliseconds.
        done() -> bool: Returns True if the interpolation is complete, False otherwise.
        reset(now_ms: int) -> None: Resets the interpolation to start again from the beginning at the given time in milliseconds.

    Easing Functions:
        Linear: ease(t) = t -> steady speed.
        Ease-in: ease(t) = t*t -> starts slow (small w for small t), accelerates.
        Ease-out: ease(t) = 1 - (1 - t)**2 -> starts fast, slows near the end.
        Ease-in-out: ease(t) = 3*t*t - 2*t*t*t (smooth S-curve).
    """

    def __init__(self, start: float, end: float, duration_ms: int, ease: Callable[[float], float] = lambda x: x) -> None:
        self.start = start
        self.end = end
        self.duration = max(1, duration_ms)
        self.ease = ease
        self._start_time: int | None = None

    def value(self, now: int) -> float:
        if self._start_time is None:
            self._start_time = now
        t = (now - self._start_time) / self.duration

        # Clamping
        if t < 0:
            t = 0.0
        elif t > 1:
            t = 1.0

        w = self.ease(t)
        return self.start + (self.end - self.start) * w

    @property
    def done(self) -> bool:
        return self._start_time is not None and pygame.time.get_ticks() - self._start_time >= self.duration

    def reset(self, now_ms: int) -> None:
        self._start_time = now_ms
