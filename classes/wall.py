from typing import TYPE_CHECKING, Optional
import pygame

import classes.entity as entity
from classes.position import Position

if TYPE_CHECKING:
    from classes.world_manager import WorldManager

class Wall(entity.Entity):
    __type: str = "CORE"
    __icon: Optional[pygame.Surface] = None  # Placeholder for wall icon

    def __init__(self, pos: Position, world_manager: "WorldManager"):
        super().__init__(pos, world_manager)

    @property
    def type(self) -> str: return self.__type
    
    @property
    def icon(self) -> pygame.Surface | None: return self.__icon