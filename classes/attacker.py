from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

import classes.cell as cell
import classes.homebase as homebase
from classes.ui.colors import ColorInfo
import classes.wall as wall
import classes.rotator as rotator
from classes.position import Position
from classes.direction import Direction
import util.pathfinding as pathfinding
from constants import Constants

if TYPE_CHECKING:
    import classes.world_manager as world_manager
    

class Attacker(cell.Cell):
    __TYPE: str = "HOSTILE"
    __NAME: str = "Attacker"


    def __init__(self, pos: Position, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None):
        super().__init__(pos, homebase_link, world_manager)

        self.__color = self.homebase.color
        self.__icon = self.homebase.attacker_icon

        self.__damage: int = 1 # The amount of damage this cell deals to other cells. A variable in case I make a damage setting

        self.__ticks_since_valid_path: int = 0 # The amount of ticks that this attacker has lived for since its path was empty. Used to prevent "stuck" attackers

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)

        self.__direction: Direction = Direction.NORTH # Starting/default direction

        self.__path: list[Position] = [] # Default path, nothing

        self.__target: homebase.Homebase = self.homebase
        if isinstance(target, homebase.Homebase): # Used to force an attacker to target a specific homebase
            self.__target = target

            self.__path = pathfinding.pathfind(
                pos, 
                self.__target.pos, 
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: self.__is_blocking(pos, world_manager)
            )

            if self.__path: 
                self.__direction = self.__set_starting_dir(self.__target.pos) # The direction that this Attacker is facing.
                self.__reset_target_count()
            else:
                self._deregister(world_manager)

            return

        choices = [homebase for homebase in world_manager.homebases if homebase is not self.homebase]
        while choices: # Sets a random Homebase as its target, if it can't find a valid path to any homebase then kill it
            self.__target = world_manager.rng.choice(choices)

            self.__path = pathfinding.pathfind(
                pos, 
                self.__target.pos, 
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: self.__is_blocking(pos, world_manager)
            )

            if self.__path:
                self.__direction = self.__set_starting_dir(self.__target.pos) # The direction that this Attacker is facing.
                self.__reset_target_count()
                return
            else:
                choices.remove(self.__target)
        self._deregister(world_manager)


    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Attacker: return cls(pos, homebase, world_manager, target)


    @property
    def name(self) -> str: return self.__NAME


    @property
    def damage(self) -> int: return self.__damage


    @property
    def direction(self) -> Direction: return self.__direction


    @direction.setter
    def direction(self, value: Direction) -> None: self.__direction = value


    @property
    def type(self) -> str: return self.__TYPE # Returns this attacker's type
    

    @property
    def icon(self) -> pygame.Surface: return self.__icon[self.direction] # Returns the icon for this attacker.


    @property
    def color(self) -> ColorInfo: return self.__color


    @property
    def target(self) -> homebase.Homebase: return self.__target


    @property
    def rotated(self) -> bool: return self.__rotated


    @property
    def ticks_since_valid_path(self) -> int: return self.__ticks_since_valid_path


    @property
    def path(self) -> list[Position]: return self.__path


    def __set_starting_dir(self, target: Position) -> Direction:
        attacker: Position = self.pos

        if target.y < attacker.y: return Direction.NORTH
        elif target.y > attacker.y: return Direction.SOUTH
        elif target.x > attacker.x: return Direction.EAST
        else: return Direction.WEST


    def __reset_target_count(self) -> None:
        self.__target.reset_target_count()
        self.homebase.reset_target_count()


    def set_rotated(self) -> None: self.__rotated = True


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.spawned:
            self.spawned = False
            return

        pos = Constants.DIRECTION_MAPPINGS[self.direction]
        cell = world_manager.get_cell(Position(self.pos.x + pos[0], self.pos.y + pos[1]))
        if cell is self.__target:
            assert isinstance(cell, homebase.Homebase)
            cell.change_health(-self.__damage)
            self._deregister(world_manager)
            return

        if not self.__path: # gets rid of stuck attackers
            self.__ticks_since_valid_path += 1
        else:
            self.__ticks_since_valid_path = 0
        if self.__ticks_since_valid_path > 4:
            self._deregister(world_manager)
            return
        

        if not self.__path:
            self.__path = pathfinding.pathfind(
                self.pos,
                self.__target.pos,
                lambda pos: world_manager.in_bounds(pos),
                lambda pos: self.__is_blocking(pos, world_manager)
            )
            if not self.__rotated: return
            next_pos = self.pos # "placeholder" because move() overrides it         
        else: next_pos = self.__path[0]

        delta = (next_pos.x - self.pos.x, next_pos.y - self.pos.y)
        if delta == (0, 0):
            # we're at the homebase, or it bugged out
            surroundings = self._get_surroundings(world_manager)
            for hb in surroundings:
                if hb is not self.__target: continue

                delta = (hb.pos.x - self.pos.x, hb.pos.y - self.pos.y)
                if delta not in Constants.DIRECTION_MAPPINGS.values(): raise RuntimeError("Uh oh, attacker couldn't find a delta!")

        if not self.__rotated:
            dir = Constants.POSITION_MAPPINGS[delta]
            if self.__direction != dir:
                self.__direction = dir
                return

        self.__move(next_pos, world_manager)


    def __is_blocking(self, pos: Position, world_manager: "world_manager.WorldManager") -> bool:
        cell = world_manager.get_cell(pos)

        if isinstance(cell, (homebase.Homebase, wall.Wall)):
            return True

        if isinstance(cell, (rotator.Rotator, Attacker)) and cell.homebase is self.homebase:
            return True

        return False


    def __move(self, next_pos: Position, world_manager: "world_manager.WorldManager") -> None:
        used_path = True
        if self.__rotated: # if we're rotated, make the next pos the place we're looking
            dx, dy = Constants.DIRECTION_MAPPINGS[self.direction]
            next_pos = Position(self.pos.x + dx, self.pos.y + dy)
            used_path = False

        cell = world_manager.get_cell(next_pos)
        if isinstance(cell, rotator.Rotator) and cell.homebase is self.homebase:
            self.__path.clear()
            return
        elif isinstance(cell, (rotator.Rotator, homebase.Homebase)): return
        elif isinstance(cell, Attacker) and cell.homebase is self.homebase:
            self.__path.clear()   # force recompute next tick
            self.__rotated = False
            return
        elif isinstance(cell, Attacker):
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
                lambda pos: self.__is_blocking(pos, world_manager)
            )
            return

        world_manager.move_entity(self, next_pos)
        if used_path: self.__path.pop(0) # if we're rotated, then don't change the path (because we didn't follow it)