from __future__ import annotations
from typing import TYPE_CHECKING, Self

from classes.direction import Direction
import classes.entity as entity
import classes.homebase as homebase
from classes.position import Position
import constants

if TYPE_CHECKING:
    import classes.world_manager as world_manager

class Cell(entity.Entity):
    def __init__(self, pos: Position, homebase_link: homebase.Homebase):
        super().__init__(pos)
        self._homebase: homebase.Homebase = homebase_link # The homebase that this cell belongs to
        self._spawned = True # If this entity just spawned, prevents moving on first tick alive.

    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Self:
        return cls(pos, homebase)


    @property
    def homebase(self) -> homebase.Homebase:
        return self._homebase # Returns the homebase that this cell belongs to.
    
    @property
    def spawned(self) -> bool: return self._spawned

    @spawned.setter
    def spawned(self, value: bool) -> None: self._spawned = value
    
    
    def _deregister(self, world_manager: "world_manager.WorldManager") -> None:
        self._alive = False
        self._homebase.remove_cell(self)
        world_manager.deregister(self) # Deregisters this entity from the world manager.


    def _move(self) -> None:
        pass # Moves the cell toward its target, each cell implements this differently. Uses the pathfind() method

    def _get_surroundings(self, world_manager: "world_manager.WorldManager") -> list[entity.Entity]:
        l: list[entity.Entity] = []

        x_pos = self._pos.x
        y_pos = self._pos.y

        dir_mapping: dict[Direction, tuple[int, int]] = constants.DIRECTION_MAPPINGS
        cells: tuple[entity.Entity | None, ...] = (
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.NORTH][0], y_pos + dir_mapping[Direction.NORTH][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.SOUTH][0], y_pos + dir_mapping[Direction.SOUTH][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.EAST][0], y_pos + dir_mapping[Direction.EAST][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.WEST][0], y_pos + dir_mapping[Direction.WEST][1]))
        )

        for cell in cells:
            if cell is not None: l.append(cell)

        return l