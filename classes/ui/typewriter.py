import pygame


class Typewriter:
    def __init__(self, font: pygame.Font, speed: int=30):
        self.__font = font
        self.__speed = speed
        self.__queue: list[list[str]] = []
        self.__lines: list[str] = []
        self.__progress = 0
        self.__timer = 0
        self.__done = True

    def queue(self, lines: list[str]) -> None:
        if not lines: return

        self.__queue.append(lines)
        if self.__done: self.start()

    def start(self) -> None:
        if not self.__queue:
            self.__done = True
            return
        
        self.__lines = self.__queue.pop(0)
        self.__progress = 0
        self.__timer = 0
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


    def update(self, dt: int) -> None:
        if self.__done: return

        self.__timer += dt
        chars = self.__timer // self.__speed
        if chars:
            self.__timer %= self.__speed
            self.__progress += chars

            length = self.__get_length()

            if self.__progress >= length:
                self.__progress = length
                self.__done = True


    def draw(self, screen: pygame.Surface, pos: tuple[int, int], line_spacing: int = 32) -> None:
        if not self.__lines: return
        remaining = self.__progress

        y = pos[1]
        for line in self.__lines:
            l = min(len(line), remaining)
            text = line[:l]

            surf = self.__font.render(text, False, "black")
            screen.blit(surf, (pos[0], y))
            remaining -= l
            y += line_spacing