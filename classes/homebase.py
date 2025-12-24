from __future__ import annotations
import random
from typing import TYPE_CHECKING
import pygame

from classes.direction import Direction
import classes.entity as entity
from classes.position import Position
import constants

if TYPE_CHECKING:
    import classes.world_manager as world_manager


class Homebase(entity.Entity):
    __type: str = "CORE"
    __icon: pygame.Surface | None = None # The icon that this entity uses.
    

    def __init__(self, pos: Position, health: int = 10):
        super().__init__(pos)

        self.__health: int = health # The health of the homebase.
        self.__cells: list[entity.Entity] = [] # The cells that belong to this homebase.

        self.__spawn_ticks: int = 0

        self.__ticks_since_target: int = 0 # The number of ticks since this Homebase had an attacker successfully find a path to it.


    @property
    def type(self) -> str: return self.__type # Returns this homebase's type (always CORE)


    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this homebase.


    def tick(self, world_manager: "world_manager.WorldManager"): 
        if self.__health < 0:
            self._deregister(world_manager)
            return
        
        self.__spawn_ticks += 1
        
        if self.__spawn_ticks == 3:
            self.__spawn_cell(world_manager)
            self.__spawn_ticks = 0


    def change_health(self, delta: int) -> None: self.__health += delta # Changes the health of this homebase


    def reset_target_count(self) -> None: self.__ticks_since_target = 0 # Resets the target count to 0


    def _deregister(self, world_manager: "world_manager.WorldManager"):
        for cell in self.__cells[:]:
            cell._deregister(world_manager)
        self.__cells.clear()

        super()._deregister(world_manager)


    def remove_cell(self, cell: entity.Entity) -> None: self.__cells.remove(cell)


    def __spawn_cell(self, world_manager: "world_manager.WorldManager"): # type: ignore
        base: Position = self.pos
        mapping = constants.DIRECTION_MAPPINGS

        positions: list[Position] = [
            Position(base.x + mapping[Direction.NORTH][0], base.y + mapping[Direction.NORTH][1]),
            Position(base.x + mapping[Direction.SOUTH][0], base.y + mapping[Direction.SOUTH][1]),
            Position(base.x + mapping[Direction.EAST][0], base.y + mapping[Direction.EAST][1]),
            Position(base.x + mapping[Direction.WEST][0], base.y + mapping[Direction.WEST][1])
        ]
        positions = [pos for pos in positions if world_manager.in_bounds(pos)]

        random.shuffle(positions)
        for pos in positions:
            if world_manager.get_cell(pos) is None:
                self.__cells.append(world_manager.spawn_cell(pos, self))
                return
            
        # Fail the spawn attempt is no square is free.