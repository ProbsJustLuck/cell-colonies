import random
from typing import TYPE_CHECKING, Optional
import pygame

import classes.cell as cell
import classes.homebase as homebase

if TYPE_CHECKING:
    import classes.world_manager as world_manager
    

class Attacker(cell.Cell):
    __type: str = "HOSTILE"
    __icon: Optional[pygame.Surface] = None


    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager"):
        super().__init__(x, y, homebase_link)

        self.__target: homebase.Homebase = random.choice([hb for hb in world_manager.get_homebases() if hb is not homebase_link]) # Sets a random Homebase as its target

        self.__direction: str = self.__set_starting_dir() # The direction that this Attacker is facing.

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)


    @classmethod
    def spawn(cls, x: int, y: int, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager") -> Attacker:
        return cls(x, y, homebase, world_manager)


    def __set_starting_dir(self) -> str:
        if self.__target.get_pos().get_y() < self.get_pos().get_y(): return "N"
        elif self.__target.get_pos().get_y() > self.get_pos().get_y(): return "S"
        elif self.__target.get_pos().get_x() > self.get_pos().get_x(): return "E"
        else: return "W"


    def get_direction(self) -> str: return self.__direction


    def set_direction(self, target: str) -> None: self.__direction = target


    def set_rotated(self) -> None: self.__rotated = True


    def tick(self, world_manager: "world_manager.WorldManager") -> None: pass


    @property
    def type(self) -> str: return self.__type # Returns this attacker's type
    

    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this attacker.


    def _move(self) -> None:
        pass