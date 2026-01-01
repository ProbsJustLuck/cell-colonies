from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from classes.position import Position 
from classes.direction import Direction
import classes.cell as cell
import classes.homebase as homebase
import classes.attacker as attacker

from classes.ui.colors import ColorInfo
from util.game_states import States
import util.pathfinding as pathfinding

if TYPE_CHECKING:
    import classes.world_manager as world_manager



class Rotator(cell.Cell):
    __TYPE: str = "UTILITY"
    __NAME: str = "Rotator"


    def __init__(self, pos: Position, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager", health: int = 2, target: Position | homebase.Homebase | None = None):
        super().__init__(pos, homebase_link, world_manager)

        self.__max_health: int = round(health * States.health_multiplier)
        self.__health: int = round(health * States.health_multiplier)

        self.__color = homebase_link.color
        self.__icon = self.homebase.rotator_icon

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
        self.__hurt: bool = False


    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Rotator: return cls(pos, homebase, world_manager)


    def __set_target(self, world_manager: "world_manager.WorldManager") -> Position | None:
        hb = self.homebase.pos
        empties = world_manager.empty_spaces
        positions: list[Position] = []

        radius = 5
        for dx in range(-radius, radius + 1): # Iterates from -5 to positive 6 (excluding 6)
            rem = radius - abs(dx) # scales from 0 to 5
            for dy in range(-rem, rem + 1): # same deal, from -rem to position rem +1
                pos = Position(hb.x + dx, hb.y + dy)
                if world_manager.in_bounds(pos) and pos in empties: positions.append(pos)

        if positions: return world_manager.rng.choice(positions)
        return None


    def change_health(self, delta: int) -> None: 
        self.__health += delta
        self.__hurt = True


    @property
    def name(self) -> str: return self.__NAME


    @property
    def type(self) -> str: return self.__TYPE # Returns this homebase's type


    @property
    def icon(self) -> pygame.Surface: # Returns the icon for this homebase.
        if self.__hurt: return self.__icon["hurt"] 
        else: return self.__icon["base"]


    @property
    def stationary(self) -> bool: return self.__stationary


    @property
    def color(self) -> ColorInfo: return self.__color


    @property
    def health(self) -> int: return self.__health


    @property
    def max_health(self) -> int: return self.__max_health


    @property
    def target(self) -> Position | None: return self.__target


    @property
    def path(self) -> list[Position]: return self.__path


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.spawned:
            self.spawned = False
            return
        
        if self.__hurt: self.__hurt = False

        if self.age > max(10, (round(world_manager.size * 1.5) - world_manager.walls_amount // 6)) and self.age % 2 == 0: self.change_health(-max(1, self.max_health // 5)) # take 20% of its max health as damage every other tick if its old
        

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