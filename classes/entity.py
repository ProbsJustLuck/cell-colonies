from __future__ import annotations
from typing import TYPE_CHECKING
from pygame import Surface

from classes.position import Position
from classes.ui.colors import ColorInfo

if TYPE_CHECKING:
    import classes.world_manager as world_manager

class Entity:    
    def __init__(self, pos: Position, world_manager: "world_manager.WorldManager"):
        self._pos = pos
        self._id = world_manager.new_id()

        self._alive: bool = True # Whether this entity is alive or not.
        world_manager.register(self)


    def tick(self, world_manager: "world_manager.WorldManager") -> None: return None # Generic tick function
    

    @property
    def pos(self) -> Position: return self._pos


    @property
    def name(self) -> str: raise NotImplementedError


    @pos.setter
    def pos(self, pos: Position): self._pos = pos


    @property
    def alive(self) -> bool: return self._alive


    @property
    def type(self) -> str: return "" # Generic type property, overridden by child classes.


    @property
    def icon(self) -> Surface: raise NotImplementedError # Generic get_icon function, overridden by child classes.


    @property
    def color(self) -> ColorInfo: raise NotImplementedError


    @property
    def id(self) -> int: return self._id


    def _deregister(self, world_manager: "world_manager.WorldManager") -> None:
        self._alive = False
        world_manager.deregister(self) # Deregisters this entity from the world manager.


    def _move(self) -> None: return None # Generic move function, overridden by child classes.