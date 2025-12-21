from __future__ import annotations
import random
from typing import TYPE_CHECKING

import pygame

from classes.position import Position 
from classes.direction import Direction
import classes.cell as cell
import classes.homebase as homebase
import classes.attacker as attacker
import classes.entity as entity
import constants


if TYPE_CHECKING:
    import classes.world_manager as world_manager


class Rotator(cell.Cell):
    __type: str = "UTILITY"
    __icon: pygame.Surface | None = None


    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: "world_manager.WorldManager", health: int = 2):
        super().__init__(x, y, homebase_link)

        self.__health: int = health
        self.__homebase: homebase.Homebase = homebase_link

        self.__target: Position | None = None
        self.__set_target(world_manager=world_manager) # Sets the target to a random space within 5 blocks of its Homebase

        self.__stationary: bool = False


    @classmethod
    def spawn(cls, x: int, y: int, homebase: homebase.Homebase, world_manager: "world_manager.WorldManager") -> Rotator:
        return cls(x, y, homebase, world_manager)


    def __set_target(self, world_manager: "world_manager.WorldManager") -> None:
        free_spaces = [ pos for pos in world_manager.get_empty_cells() if abs(pos.x - self.__homebase.get_pos().x) + abs(pos.y - self.__homebase.get_pos().y) <= 5 ]

        if free_spaces: self.__target = random.choice(free_spaces)


    def change_health(self, delta: int): self.__health += delta


    @property
    def type(self) -> str: return self.__type # Returns this homebase's type (always CORE)


    @property
    def icon(self) -> pygame.Surface | None: return self.__icon # Returns the icon for this homebase.


    def tick(self, world_manager: "world_manager.WorldManager") -> None:
        if self.__health < 0:
            self._deregister(world_manager)
            return
        
        surroundings = self.__get_surroundings(world_manager)
        for atk in surroundings:
            if not isinstance(atk, attacker.Attacker): continue

            self.__health -= atk.damage
            self.__rotate_target(atk)
            atk.set_rotated()


    def __move(self) -> None: # type: ignore
        pass


    def __rotate_target(self, cell: attacker.Attacker) -> None: # type: ignore
        dir: Direction = cell.direction
        opposites: dict[Direction, Direction] = { # cleaner than 4 if/elif statements
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST
        }

        cell.direction = opposites[dir]


    def __get_surroundings(self, world_manager: "world_manager.WorldManager") -> list[entity.Entity]:
        l: list[entity.Entity] = []

        x_pos = self.pos.x
        y_pos = self.pos.y

        dir_mapping: dict[Direction, tuple[int, int]] = constants.MAPPINGS
        cells: tuple[entity.Entity | None, ...] = (
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.NORTH][0], y_pos + dir_mapping[Direction.NORTH][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.SOUTH][0], y_pos + dir_mapping[Direction.SOUTH][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.EAST][0], y_pos + dir_mapping[Direction.EAST][1])),
            world_manager.get_cell(Position(x_pos + dir_mapping[Direction.WEST][0], y_pos + dir_mapping[Direction.WEST][1]))
        )

        for cell in cells:
            if cell is not None: l.append(cell)

        return l
    

    def set_stationary(self) -> None: self.__stationary = True # Sets this rotator to be stationary (has reached its target at least once)