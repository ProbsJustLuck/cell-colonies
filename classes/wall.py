from typing import TYPE_CHECKING
import pygame

import classes.entity as entity
from classes.position import Position

from util import assets

if TYPE_CHECKING:
    from classes.world_manager import WorldManager

class Wall(entity.Entity):
    __TYPE: str = "CORE"
    __NAME: str = "Wall"

    def __init__(self, pos: Position, world_manager: "WorldManager"):
        super().__init__(pos, world_manager)

        self.__icon = assets.wall

    @property
    def type(self) -> str: return self.__TYPE


    @property
    def name(self) -> str: return self.__NAME


    @property
    def icon(self) -> pygame.Surface: return self.__icon