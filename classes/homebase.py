from typing import TYPE_CHECKING
import pygame

import classes.entity as entity

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


    def tick(self, world_manager: "world_manager.WorldManager"): pass


    def change_health(self, delta: int) -> None: self.__health += delta # Changes the health of this homebase


    def reset_target_count(self) -> None: self.__ticks_since_target = 0 # Resets the target count to 0


    def __deregister(self, world_manager: "world_manager.WorldManager"): # type: ignore
        world_manager.deregister(self) # Deregisters this homebase from the world manager.