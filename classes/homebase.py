from typing import Optional
import pygame

import classes.world_manager as world_manager
import classes.entity as entity

class Homebase(entity.Entity):
    __type: str = "CORE"
    __icon: Optional[pygame.Surface] = None # The icon that this entity uses.
    
    def __init__(self, x: int, y: int, health: int = 10):
        super().__init__(x, y)

        self.health: int = health # The health of the homebase.
        self.cells: list[entity.Entity] = [] # The cells that belong to this homebase.


    def get_type(self) -> str: return self.__type # Returns this homebase's type (always CORE)


    def get_icon(self) -> Optional[pygame.Surface]: return self.__icon # Returns the icon for this homebase.

    
    def _deregister(self, world_manager: world_manager.WorldManager):
        world_manager.deregister(self) # Deregisters this homebase from the world manager.