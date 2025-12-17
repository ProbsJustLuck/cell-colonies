from __future__ import annotations
from typing import TYPE_CHECKING
from pygame import Surface

import position

if TYPE_CHECKING:
    import world_manager

class Entity:
    category: str = "" # What category this entity is (from "type").
    icon: Surface = None # The icon that this entity uses.
    
    def __init__(self, x: int, y: int):
        self.pos = position.Position(x, y)

        self._alive: bool = True # Whether this entity is laive or not.

    def tick(self) -> None:
        return None # Generic tick function
    
    def get_pos(self) -> tuple[int, int]:
        return ( self.pos.get_x(), self.pos.get_y() )
    
    def _deregister(self, world_manager: world_manager.WorldManager):
        world_manager.deregister(self) # Deregisters this entity from the world manager.

    def _move(self) -> None:
        return None # Generic move function, overridden by child classes.
    
    def _get_surroundings(self) -> list[position.Position]:
        return [] # Generic get_surroundings function, overridden by child classes.