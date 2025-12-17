import random
from typing import Optional
import pygame

import classes.world_manager
import classes.cell as cell
import classes.homebase as homebase

class Attacker(cell.Cell):
    __type: str = "hostile"
    __icon: Optional[pygame.Surface] = None

    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: classes.world_manager.WorldManager):
        super().__init__(x, y, homebase_link)

        homebases: list[homebase.Homebase] = world_manager.get_homebases()
        self.__target: homebase.Homebase = homebases[random.randint(0, len(homebases))] # Sets a random Homebase as its target

        self.__direction: str = self.__set_starting_dir() # The direction that this Attacker is facing.

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)


    def __set_starting_dir(self) -> str:
        if self.__target.get_pos().get_y() > self.get_pos().get_y(): return "N"
        elif self.__target.get_pos().get_y() < self.get_pos().get_y(): return "S"
        elif self.__target.get_pos().get_x() > self.get_pos().get_x(): return "E"
        else: return "W"

    def get_direction(self) -> str: return self.__direction

    def set_direction(self, target: str) -> None: self.__direction = target

    def set_rotated(self) -> None: self.__rotated = True

    def _move(self) -> None:
        pass