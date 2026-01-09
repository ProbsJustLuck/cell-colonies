from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from classes import teleporter
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
        self.__health: float = 1.0

        self.__color = self.homebase.color
        self.__icon = self.homebase.attacker_icon

        self.__damage: float = round(world_manager.rng.randint(7, 12) / 10, 2)

        self.__ticks_since_valid_path: int = 0 # The amount of ticks that this attacker has lived for since its path was empty. Used to prevent "stuck" attackers

        self.__rotated: bool = False # Whether this attacker has been rotated recently (resets upon a wall collision)

        self.__hurt_until: int = 0

        self.__skip = False

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
                self.deregister(world_manager)

            return

        choices = choices = sorted((homebase for homebase in world_manager.homebases if homebase is not self.homebase), key=lambda hb: (hb.pos.x, hb.pos.y))
        while choices: # Sets a random Homebase as its target, if it can't find a valid path to any homebase then kill it
            self.__target = world_manager.rng.choice(choices)

            for _ in range(5):
                self.__path = pathfinding.pathfind(
                    pos, 
                    self.__target.pos, 
                    lambda pos: world_manager.in_bounds(pos), 
                    lambda pos: self.__is_blocking(pos, world_manager)
                )
                if self.__path: break

            if self.__path:
                self.__direction = self.__set_starting_dir(self.__target.pos) # The direction that this Attacker is facing.
                self.__reset_target_count()
                return
            else:
                choices.remove(self.__target)
        self.deregister(world_manager)


    @classmethod
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Attacker: return cls(pos, homebase, world_manager, target)


    @property
    def name(self) -> str: return self.__NAME


    @property
    def health(self) -> float: return self.__health


    @property
    def hurt(self) -> bool: return self._hurt


    @hurt.setter
    def hurt(self, value: bool) -> None: self._hurt = value


    @property
    def damage(self) -> float: return self.__damage


    @property
    def direction(self) -> Direction: return self.__direction


    @direction.setter
    def direction(self, value: Direction) -> None: self.__direction = value


    @property
    def type(self) -> str: return self.__TYPE # Returns this attacker's type
    

    @property
    def icon(self) -> pygame.Surface: # Returns the icon for this attacker.
        if self._hurt: return self.__icon["hurt"][self.direction]
        return self.__icon["base"][self.direction]


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


    @property
    def hurt_until(self) -> int: return self.__hurt_until

    
    @hurt_until.setter
    def hurt_until(self, value: int): self.__hurt_until = value


    @property
    def skip(self) -> bool: return self.__skip


    @skip.setter
    def skip(self, value: bool) -> None: self.__skip = value


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


    def set_teleported(self) -> None: 
        self._spawned = True
        self.__path.clear()


    def change_health(self, delta: float) -> None:
        self.__health = max(self.__health + delta, 0.0)
        self._hurt = True
        self.__skip = True



    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.spawned:
            self.spawned = False
            return
        
        if self.__skip: self.__skip = False

        if self.__health <= 0.0:
            self.deregister(world_manager)
            return


        pos = Constants.DIRECTION_MAPPINGS[self.direction]
        cell = world_manager.get_cell(Position(self.pos.x + pos[0], self.pos.y + pos[1]))
        if cell is self.__target:
            assert isinstance(cell, homebase.Homebase)
            cell.change_health(-self.__damage)

            self.__hurt_until = world_manager.current_tick
            self.change_health(-self.health)
            return

        if not self.__path: # gets rid of stuck attackers
            self.__ticks_since_valid_path += 1
        else:
            self.__ticks_since_valid_path = 0
        if self.__ticks_since_valid_path > 4:
            self.hurt_until = world_manager.current_tick
            self.change_health(-self.damage)
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

        if isinstance(cell, (homebase.Homebase, wall.Wall)): return True

        if isinstance(cell, (rotator.Rotator, Attacker, teleporter.Teleporter)) and cell.homebase is self.homebase: return True

        return False


    def __move(self, next_pos: Position, world_manager: "world_manager.WorldManager") -> None:
        used_path = True
        if self.__rotated: # if we're rotated, make the next pos the place we're looking
            dx, dy = Constants.DIRECTION_MAPPINGS[self.direction]
            next_pos = Position(self.pos.x + dx, self.pos.y + dy)
            used_path = False

        cell = world_manager.get_cell(next_pos)
        if isinstance(cell, (rotator.Rotator, homebase.Homebase, teleporter.Teleporter)): 
            self.__path.clear()
            if self.__rotated: self.__rotated = False
            return
        elif isinstance(cell, Attacker) and cell.homebase is self.homebase:
            self.__path.clear() # repath
            self.__rotated = False
            return
        elif isinstance(cell, Attacker):
            if cell.alive and cell.health > 0.0:
                cell.hurt_until = world_manager.current_tick
                cell.change_health(-self.damage)

                self.hurt_until = world_manager.current_tick
                self.change_health(-cell.__damage)
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