from __future__ import annotations
from typing import TYPE_CHECKING, Self

import classes.entity as entity
import classes.homebase as homebase
from classes.position import Position

if TYPE_CHECKING:
    import classes.world_manager as world_manager

class Cell(entity.Entity):
    def __init__(self, pos: Position, homebase_link: homebase.Homebase):
        super().__init__(pos)
        self._homebase: homebase.Homebase = homebase_link # The homebase that this cell belongs to.

    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager") -> Self:
        return cls(pos, homebase)


    @property
    def homebase(self) -> homebase.Homebase:
        return self._homebase # Returns the homebase that this cell belongs to.
    

    def _pathfind(self) -> None:
        pass # Pathfinding logic for the cell, A* algorithm later


    def _move(self) -> None:
        pass # Moves the cell toward its target, each cell implements this differently. Uses the pathfind() method