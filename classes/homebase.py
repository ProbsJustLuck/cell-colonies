from __future__ import annotations
import random
from typing import TYPE_CHECKING
import pygame

import classes.entity as entity
from classes.position import Position
import constants

if TYPE_CHECKING:
    import classes.world_manager as world_manager


class Homebase(entity.Entity):
    __type: str = "CORE"
    __icon: pygame.Surface | None = None # The icon that this entity uses.
    

    def __init__(self, x: int, y: int, health: int = 10):
        super().__init__(x, y)

        self.__health: int = health # The health of the homebase.
        self.__cells: list[entity.Entity] = [] # The cells that belong to this homebase.

        self.__ticks_since_target: int = 0 # The number of ticks since this Homebase had an attacker successfully find a path to it.


    @property
    def type(self) -> str: return self.__type # Returns this homebase's type (always CORE)


    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this homebase.


    def tick(self, world_manager: "world_manager.WorldManager"): 
        if self.__health < 0:
            self._deregister(world_manager)
            return
        



    def change_health(self, delta: int) -> None: self.__health += delta # Changes the health of this homebase


    def reset_target_count(self) -> None: self.__ticks_since_target = 0 # Resets the target count to 0


    def _deregister(self, world_manager: "world_manager.WorldManager"):
        for cell in self.__cells[:]:
            cell._deregister(world_manager)
        self.__cells.clear()
        world_manager.deregister(self)

    def __spawn_cell(self, world_manager: "world_manager.WorldManager"): # type: ignore
        base: Position = self.get_pos()

        positions: list[Position] = [
            Position(base.x + constants.MAPPINGS["N"][0], base.y + constants.MAPPINGS["N"][1]),
            Position(base.x + constants.MAPPINGS["S"][0], base.y + constants.MAPPINGS["S"][1]),
            Position(base.x + constants.MAPPINGS["E"][0], base.y + constants.MAPPINGS["E"][1]),
            Position(base.x + constants.MAPPINGS["W"][0], base.y + constants.MAPPINGS["W"][1])
        ]
        positions = [pos for pos in positions if world_manager.check_in_bounds(pos)]

        random.shuffle(positions)
        for pos in positions:
            if world_manager.get_cell(pos) is None:
                self.__cells.append(world_manager.spawn_cell(pos, self))
                return