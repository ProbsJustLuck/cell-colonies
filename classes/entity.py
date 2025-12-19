from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from pygame import Surface

import classes.position as position

if TYPE_CHECKING:
    import classes.world_manager as world_manager

class Entity:    
    def __init__(self, x: int, y: int):
        self.pos = position.Position(x, y)

        self._alive: bool = True # Whether this entity is laive or not.

    def tick(self, world_manager: "world_manager.WorldManager") -> None: return None # Generic tick function
    
    def get_pos(self) -> position.Position: return position.Position(self.pos.get_x(), self.pos.get_y())
    
    @property
    def type(self) -> str: return "" # Generic type property, overridden by child classes.

    @property
    def icon(self) -> Optional[Surface]: pass # Generic get_icon function, overridden by child classes.
    
    def _deregister(self, world_manager: "world_manager.WorldManager") -> None:
        world_manager.deregister(self) # Deregisters this entity from the world manager.

    def _move(self) -> None: return None # Generic move function, overridden by child classes.
    
    def _get_surroundings(self) -> list[position.Position]: return [] # Generic get_surroundings function, overridden by child classes.
