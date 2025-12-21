from __future__ import annotations
import random
from typing import TYPE_CHECKING, Optional
import pygame

import classes.cell as cell
import classes.homebase as homebase
from classes.position import Position
from classes.direction import Direction

if TYPE_CHECKING:
    import classes.world_manager as world_manager
    

class Attacker(cell.Cell):
    __type: str = "HOSTILE"
    __icon: Optional[pygame.Surface] = None


    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager"):
        super().__init__(x, y, homebase_link)

        choices = [homebase for homebase in world_manager.get_homebases() if homebase is not homebase_link]
        self.__target: homebase.Homebase = random.choice(choices) if choices else homebase_link # Sets a random Homebase as its target

        self.__direction: Direction = self.__set_starting_dir() # The direction that this Attacker is facing.

        self.__damage: int = 1 # The amount of damage this cell deals to other cells. A variable in case I make a damage setting

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)


    @classmethod
    def spawn(cls, x: int, y: int, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager") -> Attacker:
        return cls(x, y, homebase, world_manager)


    def __set_starting_dir(self) -> Direction:
        target: Position = self.__target.get_pos()
        attacker: Position = self.get_pos()

        if target.y < attacker.y: return Direction.NORTH
        elif target.y > attacker.y: return Direction.SOUTH
        elif target.x > attacker.x: return Direction.EAST
        else: return Direction.WEST


    @property
    def damage(self) -> int: return self.__damage


    @property
    def direction(self) -> Direction: return self.__direction


    @direction.setter
    def direction(self, value: Direction) -> None: self.__direction = value


    def set_rotated(self) -> None: self.__rotated = True


    def tick(self, world_manager: "world_manager.WorldManager") -> None: pass


    @property
    def type(self) -> str: return self.__type # Returns this attacker's type
    

    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this attacker.


    def _move(self) -> None:
        pass