from typing import Optional
import pygame

import classes.entity as entity
from classes.position import Position

class Wall(entity.Entity):
    __type: str = "CORE"
    __icon: Optional[pygame.Surface] = None  # Placeholder for wall icon

    def __init__(self, pos: Position):
        super().__init__(pos)

    @property
    def type(self) -> str: return self.__type
    
    @property
    def icon(self) -> pygame.Surface | None: return self.__icon