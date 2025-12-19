from typing import Optional
import pygame

import classes.entity as entity

class Wall(entity.Entity):
    __type: str = "CORE"
    __icon: Optional[pygame.Surface] = None  # Placeholder for wall icon

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    @property
    def type(self) -> str: return self.__type
    
    @property
    def icon(self) -> pygame.Surface | None: return self.__icon