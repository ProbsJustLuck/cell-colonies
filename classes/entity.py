from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from pygame import Surface

from classes.position import Position

if TYPE_CHECKING:
    import classes.world_manager as world_manager

class Entity:    
    def __init__(self, pos: Position):
        self._pos = pos

        self._alive: bool = True # Whether this entity is laive or not.


    def tick(self, world_manager: "world_manager.WorldManager") -> None: return None # Generic tick function
    

    @property
    def pos(self) -> Position: return self._pos


    @pos.setter
    def pos(self, pos: Position): self._pos = pos


    @property
    def alive(self) -> bool: return self._alive


    @property
    def type(self) -> str: return "" # Generic type property, overridden by child classes.


    @property
    def icon(self) -> Optional[Surface]: pass # Generic get_icon function, overridden by child classes.


    def _deregister(self, world_manager: "world_manager.WorldManager") -> None:
        self._alive = False
        world_manager.deregister(self) # Deregisters this entity from the world manager.


    def _move(self) -> None: return None # Generic move function, overridden by child classes.


    def _get_surroundings(self) -> list[Position]: return [] # Generic get_surroundings function, overridden by child classes.
