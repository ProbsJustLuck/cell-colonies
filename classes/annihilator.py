from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from classes import rotator, wall
from classes.position import Position 
import classes.cell as cell
import classes.homebase as homebase
import classes.attacker as attacker
import classes.teleporter as teleporter

from classes.ui.colors import ColorInfo
from util.game_states import States
import util.pathfinding as pathfinding

if TYPE_CHECKING:
    import classes.world_manager as world_manager



class Annihilator(cell.Cell):
    __TYPE: str = "HOSTILE"
    __NAME: str = "Annihilator"


    def __init__(self, pos: Position, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager", health: int = 2, target: Position | homebase.Homebase | None = None):
        super().__init__(pos, homebase_link, world_manager)

        self.__max_health: float = max(round(health * States.health_multiplier, 2), 1)
        self.__health: float = max(round(health * States.health_multiplier, 2), 1)

        self.__color = homebase_link.color
        self.__icon = self.homebase.annihilator_icon

        self.__grace_ticks = 0

        if not target: self.__target: Position | None = self.__set_target(world_manager=world_manager)
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
    def spawn(cls, pos: Position, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager", target: Position | homebase.Homebase | None = None) -> Annihilator: return cls(pos, homebase, world_manager)


    def __set_target(self, world_manager: "world_manager.WorldManager") -> Position | None:
        positions: list[Position] = list(world_manager.empty_spaces)

        if positions: return world_manager.rng.choice(positions)
        return None


    def change_health(self, delta: float) -> None: 
        self.__health = max(self.__health + delta, 0.0)
        self.__hurt = True


    @property
    def name(self) -> str: return self.__NAME


    @property
    def type(self) -> str: return self.__TYPE # Returns this cell's type


    @property
    def icon(self) -> pygame.Surface: # Returns the icon for this cell.
        if self.__hurt: return self.__icon["hurt"] 
        elif self.__grace_ticks < 3: return self.__icon["grace"]
        else: return self.__icon["base"]


    @property
    def stationary(self) -> bool: return self.__stationary


    @property
    def color(self) -> ColorInfo: return self.__color


    @property
    def health(self) -> float: return self.__health


    @property
    def max_health(self) -> float: return self.__max_health


    @property
    def target(self) -> Position | None: return self.__target


    @property
    def path(self) -> list[Position]: return self.__path


    @property
    def grace_ticks(self) -> int: return self.__grace_ticks


    def __is_blocking(self, pos: Position, world_manager: "world_manager.WorldManager") -> bool:
        cell = world_manager.get_cell(pos)

        if isinstance(cell, (homebase.Homebase, wall.Wall)): return True

        if isinstance(cell, (rotator.Rotator, attacker.Attacker, Annihilator, teleporter.Teleporter)) and cell.homebase is self.homebase: return True

        return False


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.spawned:
            self.spawned = False
            return
        
        if self.__grace_ticks < 3: self.__grace_ticks += 1
        
        if self.__hurt: self.__hurt = False

        if self.age > max(10, (round(world_manager.size * 2) - world_manager.walls_amount // 6)) and self.age % 2 == 0: self.change_health(-max(0.1, round(self.max_health / 5, 2))) # take 20% of its max health as damage every other tick if its old
        

        surroundings = self._get_surroundings(world_manager)
        if surroundings and self.__grace_ticks > 2: # Loop through all nearby attackers and kill them
            for cell in surroundings:
                if isinstance(cell, wall.Wall) or (isinstance(cell, (attacker.Attacker, rotator.Rotator, teleporter.Teleporter, Annihilator)) and cell.homebase is self.homebase) or cell is self._homebase: continue
                
                if isinstance(cell, (attacker.Attacker, rotator.Rotator, teleporter.Teleporter, Annihilator)): cell.change_health(-cell.health)
                
                if isinstance(cell, attacker.Attacker): self.change_health(-cell.damage)
                elif isinstance(cell, Annihilator): self.change_health(-self.health)
                else: self.change_health(-1.0)

                if self.__health <= 0.0: return
        
        if self.__target and not self.__stationary and not self.__path: self.__path = pathfinding.pathfind(
                self.pos,
                self.__target,
                lambda pos: world_manager.in_bounds(pos), 
                lambda pos: self.__is_blocking(pos, world_manager),
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
        self.__path.pop(0)