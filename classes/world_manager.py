from __future__ import annotations
import random
from typing import TYPE_CHECKING

import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
from classes.position import Position
import classes.entity as entity
import classes.wall as wall
from classes.cell import Cell
import cell_registry


if TYPE_CHECKING:
    pass
    

class WorldManager:
    
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30):
        self.__world_size = size
        self.__world_map: list[list[entity.Entity | None]] = [[None for _ in range(size)] for _ in range(size)]

        self.__current_tick: int = 0

        self.__homebases: list[homebase.Homebase] = []
        self.__rotators: list[rotator.Rotator] = []
        self.__attackers: list[attacker.Attacker] = []


        spaces = self.get_empty_cells()
        for i in range(homebases): # type: ignore
            num = random.randrange(len(spaces))

            self.register(homebase.Homebase(spaces[num]))
            spaces.pop(num)

        spaces = self.get_empty_cells()
        for i in range(walls): # type: ignore
            num = random.randrange(len(spaces))

            self.register(wall.Wall(spaces[num]))
            spaces.pop(num)
        

    def get_empty_cells(self) -> list[Position]:
        l: list[Position] = []

        for i in range(len(self.__world_map)):
            for j in range(len(self.__world_map[i])):
                if self.__world_map[i][j] is None:
                    l.append(Position(i, j))
        return l
    

    def __tick(self) -> bool: # type: ignore
        self.__current_tick += 1

        for homebase in self.__homebases[:]:
            if not homebase.alive: continue
            homebase.tick(self)
        
        for rotator in self.__rotators[:]:
            if not rotator.alive: continue
            rotator.tick(self)
        
        for attacker in self.__attackers[:]:
            if not attacker.alive: continue
            attacker.tick(self)

        if(len(self.__homebases) == 1):
            return False # TODO: end the game
        return True
    

    def run(self) -> None:
        pass # Main loop of the world manager.


    def __draw(self) -> None: # type: ignore
        pass # TODO: Draws the world map to the screen.


    @property
    def homebases(self) -> list[homebase.Homebase]: return self.__homebases # Returns the alive homebases.
    

    @property
    def map(self) -> list[list[entity.Entity | None]]: return self.__world_map # Returns the world map.


    def spawn_cell(self, pos: Position, homebase: homebase.Homebase) -> Cell: # type: ignore
        choice = random.choice(cell_registry.SPAWNABLE_CELLS)
        new_cell = choice.spawn(pos, homebase, self)
        
        self.register(new_cell)
        return new_cell


    def get_cell(self, pos: Position) -> entity.Entity | None:
        if self.in_bounds(pos): return self.__world_map[pos.x][pos.y]
        return None
    

    def in_bounds(self, pos: Position) -> bool: return 0 <= pos.x < self.__world_size and 0 <= pos.y < self.__world_size


    def is_blocking(self, pos: Position) -> bool: return isinstance(self.__world_map[pos.x][pos.y], wall.Wall)


    def deregister(self, cell: entity.Entity) -> None:
        self.__world_map[cell.pos.x][cell.pos.y] = None # Sets the cell to None in the world map.

        if isinstance(cell, homebase.Homebase):
            self.__homebases.remove(cell)
        elif isinstance(cell, attacker.Attacker):
            self.__attackers.remove(cell)
        elif isinstance(cell, rotator.Rotator):
            self.__rotators.remove(cell)


    def register(self, cell: entity.Entity) -> None: # Register the cell to each entity sublist
        self.__world_map[cell.pos.x][cell.pos.y] = cell

        if isinstance(cell, homebase.Homebase):
            self.__homebases.append(cell)
        elif isinstance(cell, attacker.Attacker):
            self.__attackers.append(cell)
        elif isinstance(cell, rotator.Rotator):
            self.__rotators.append(cell)