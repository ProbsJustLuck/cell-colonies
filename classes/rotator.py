from __future__ import annotations
import random
from typing import TYPE_CHECKING

import pygame

from classes.position import Position 
from classes.direction import Direction
import classes.cell as cell
import classes.homebase as homebase
import classes.attacker as attacker
import util.pathfinding as pathfinding


if TYPE_CHECKING:
    import classes.world_manager as world_manager


class Rotator(cell.Cell):
    __type: str = "UTILITY"
    __icon: pygame.Surface | None = None


    def __init__(self, pos: Position, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager", health: int = 2, target: Position | homebase.Homebase | None = None):
        super().__init__(pos, homebase_link, world_manager)

        self.__health: int = health
        self.__homebase: homebase.Homebase = homebase_link

        if not target: self.__target: Position | None = self.__set_target(world_manager=world_manager) # Sets the target to a random space within 5 blocks of its Homebase
        elif isinstance(target, Position):
            self.__target = target
        else:
            raise TypeError("How did we get here?")

        self.__path: list[Position] = []
        if self.__target: self.__path = pathfinding.pathfind(
                self.pos,
                self.__target, 
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: world_manager.is_blocking(pos)
            )

        self.__stationary: bool = False


    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Rotator: return cls(pos, homebase, world_manager)


    def __set_target(self, world_manager: "world_manager.WorldManager") -> Position | None:
        hb = self.__homebase.pos
        empties = world_manager.get_empty_spaces()
        positions: list[Position] = []

        radius = 5
        for dx in range(-radius, radius + 1): # Iterates from -5 to positive 6 (excluding 6)
            rem = radius - abs(dx) # scales from 0 to 5
            for dy in range(-rem, rem + 1): # same deal, from -rem to position rem +1
                pos = Position(hb.x + dx, hb.y + dy)
                if world_manager.in_bounds(pos) and pos in empties: positions.append(pos)

        if positions: return random.choice(positions)
        return None


    def change_health(self, delta: int) -> None: self.__health += delta


    @property
    def type(self) -> str: return self.__type # Returns this homebase's type


    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this homebase.


    @property
    def stationary(self) -> bool: return self.__stationary


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.spawned:
            self.spawned = False
            return

        if self.__health < 0: # If the health is below 0, then its dead
            self._deregister(world_manager)
            return
        
        surroundings = self._get_surroundings(world_manager)
        if surroundings: # Loop through all nearby attackers and rotate them
            for atk in surroundings:
                if not isinstance(atk, attacker.Attacker) or atk.homebase == self.homebase: continue

                self.change_health(-atk.damage)
                self.__rotate_target(atk)
                atk.set_rotated()
        
        if self.__target and not self.__stationary and not self.__path: self.__path = pathfinding.pathfind(
                self.pos,
                self.__target,
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: world_manager.is_blocking(pos)
            )
        if self.__path and not self.__stationary:
            next_pos = self.__path[0]
            self.__move(next_pos, world_manager) # Move

        if self.pos == self.__target and not self.__stationary: self.__stationary = True # If it reached its target at least once, then set it as stationary


    def __move(self, next_pos: Position, world_manager: "world_manager.WorldManager") -> None:
        if not world_manager.in_bounds(next_pos): return
        if world_manager.get_cell(next_pos): 
            self.__path.clear()
            return

        world_manager.move_entity(self, next_pos)
        self.__path.pop(0) # if we're rotated, then don't change the path (because we didn't follow it)


    def __rotate_target(self, cell: attacker.Attacker) -> None:
        dir: Direction = cell.direction
        opposites: dict[Direction, Direction] = { # cleaner than 4 if/elif statements
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST
        }

        cell.direction = opposites[dir]