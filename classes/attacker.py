from __future__ import annotations
import random
from typing import TYPE_CHECKING, Optional
import pygame

import classes.cell as cell
import classes.homebase as homebase
import classes.wall as wall
import classes.rotator as rotator
from classes.position import Position
from classes.direction import Direction
import pathfinding
import constants

if TYPE_CHECKING:
    import classes.world_manager as world_manager
    

class Attacker(cell.Cell):
    __type: str = "HOSTILE"
    __icon: Optional[pygame.Surface] = None


    def __init__(self, pos: Position, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager"):
        super().__init__(pos, homebase_link)

        choices = [homebase for homebase in world_manager.homebases if homebase is not homebase_link]
        self.__target: homebase.Homebase | None = random.choice(choices) if choices else None # Sets a random Homebase as its target

        self.__direction: Direction = Direction.NORTH
        self.__path: list[Position] = []
        if self.__target:
            self.__target.reset_target_count()
            self.__direction = self.__set_starting_dir(self.__target.pos) # The direction that this Attacker is facing.

            self.__path = pathfinding.pathfind(
                pos, 
                self.__target.pos, 
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: world_manager.is_blocking(pos)
            )
        

        self.__damage: int = 1 # The amount of damage this cell deals to other cells. A variable in case I make a damage setting

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)


    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager") -> Attacker:
        return cls(pos, homebase, world_manager)


    def __set_starting_dir(self, target: Position) -> Direction:
        attacker: Position = self.pos

        if target.y < attacker.y: return Direction.NORTH
        elif target.y > attacker.y: return Direction.SOUTH
        elif target.x > attacker.x: return Direction.EAST
        else: return Direction.WEST


    @property
    def damage(self) -> int: return self.__damage


    @property
    def direction(self) -> Direction: return self.__direction


    @direction.setter
    def direction(self, value: Direction) -> None: self.__direction = value


    def set_rotated(self) -> None: self.__rotated = True


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        mapping = constants.DIRECTION_MAPPINGS

        boundsX = self.pos.x + mapping[self.direction][0]
        boundsY = self.pos.y + mapping[self.direction][1]

        cell = world_manager.get_cell(Position(boundsX, boundsY))
        if isinstance(cell, homebase.Homebase): # If the cell in front of it is a Homebase, deal damage and kill this attacker 
            cell.change_health(-self.__damage)
            self._deregister(world_manager)
            return
        
        if not self.__target:
            self.__rotated = False
            return
        
        if not self.__path and self.__target: self.__path = pathfinding.pathfind(
            self.pos,
            self.__target.pos,
            lambda pos: world_manager.in_bounds(pos),
            lambda pos: world_manager.is_blocking(pos)
        )
        if not self.__path:
            if not self.__rotated: return
            else: next_pos = self.pos
        else: next_pos = self.__path[0]

        if self.__target and not self.__rotated: self.__rotate_to_target(next_pos)

        self.__move(next_pos, world_manager)


    @property
    def type(self) -> str: return self.__type # Returns this attacker's type
    

    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this attacker.


    def __rotate_to_target(self, target: Position) -> None:
        delta: tuple[int, int] = (target.x - self.pos.x, target.y - self.pos.y)
        self.direction = constants.POSITION_MAPPINGS[delta]


    def __move(self, next_pos: Position, world_manager: "world_manager.WorldManager") -> None:
        used_path = True
        if self.__rotated: # if we're rotated, make the next pos the place we're looking
            dx, dy = constants.DIRECTION_MAPPINGS[self.__direction]
            next_pos = Position(self.pos.x + dx, self.pos.y + dy)
            used_path = False

        cell = world_manager.get_cell(next_pos) 
        if isinstance(cell, rotator.Rotator): return
        if isinstance(cell, Attacker):
            cell._deregister(world_manager)
            self._deregister(world_manager)
            return
        elif not world_manager.in_bounds(next_pos) or isinstance(cell, wall.Wall):
            assert self.__target is not None # type checker was buggy, the tick code solves this already tho

            self.__rotated = False
            self.__path = pathfinding.pathfind(
                self.pos,
                self.__target.pos, 
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: world_manager.is_blocking(pos)
            )
            return

        world_manager.map[self.pos.x][self.pos.y] = None
        world_manager.map[next_pos.x][next_pos.y] = self
        self.pos = next_pos
        if used_path: self.__path.pop(0) # if we're rotated, then don't change the path (because we didn't follow it)