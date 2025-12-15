from __future__ import annotations
from typing import TYPE_CHECKING

import position

if TYPE_CHECKING:
    import world_manager

class Entity:
    category = None # What category this entity is (from "type").
    icon = None # The icon that this entity uses.
    
    def __init__(self, x: int, y: int):
        self.pos = position.Position(x, y)

        self._alive: bool = True # Whether this entity is laive or not.

    def tick(self) -> None:
        return None # Generic tick function
    
    def get_pos(self) -> tuple[int, int]:
        return ( self.pos.get_x(), self.pos.get_y() )
    
    def _deregister(self, worldmanager: world_manager.WorldManager):
        pass