from __future__ import annotations
import random
from typing import TYPE_CHECKING

import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
import classes.position as position
import classes.entity as entity
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

        


        # for i in range(homebases):
        #     to be implemented
        

    def get_empty_cells(self) -> list[position.Position]: # type: ignore
        l: list[position.Position] = []

        for i in range(len(self.__world_map)):
            for j in range(len(self.__world_map[i])):
                if self.__world_map[i][j] is None:
                    l.append(position.Position(i, j))
        return l
    

    def __tick(self) -> None: # type: ignore
        self.__current_tick += 1

        for homebase in self.__homebases[:]:
            if not homebase.is_alive(): continue
            homebase.tick(self)
        
        for rotator in self.__rotators[:]:
            if not rotator.is_alive(): continue
            rotator.tick(self)
        
        for attacker in self.__attackers[:]:
            if not attacker.is_alive(): continue
            attacker.tick(self)
    

    def run(self) -> None:
        pass # Main loop of the world manager.


    def __draw(self) -> None: # type: ignore
        pass # Draws the world map to the screen.


    def get_homebases(self) -> list[homebase.Homebase]: return self.__homebases # Returns the alive homebases.
    

    def get_map(self) -> list[list[entity.Entity | None]]: return self.__world_map # Returns the world map.


    def spawn_cell(self, pos: position.Position, homebase: homebase.Homebase) -> Cell: # type: ignore
        choice = random.choice(cell_registry.SPAWNABLE_CELLS)
        new_cell = choice.spawn(pos.x, pos.y, homebase, self)
        
        self.register(new_cell)
        return new_cell


    def get_cell(self, pos: position.Position) -> entity.Entity | None:
        if self.check_in_bounds(pos): return self.__world_map[pos.x][pos.y]
        return None
    

    def check_in_bounds(self, pos: position.Position): return 0 <= pos.x < self.__world_size and 0 <= pos.y < self.__world_size


    def deregister(self, cell: entity.Entity) -> None:
        self.__world_map[cell.get_pos().x][cell.get_pos().y] = None # Sets the cell to None in the world map.

        if isinstance(cell, homebase.Homebase):
            self.__homebases.remove(cell)
        elif isinstance(cell, attacker.Attacker):
            self.__attackers.remove(cell)
        elif isinstance(cell, rotator.Rotator):
            self.__rotators.remove(cell)


    def register(self, cell: entity.Entity) -> None: # Register the cell to each entity sublist
        self.__world_map[cell.get_pos().x][cell.get_pos().y] = cell

        if isinstance(cell, homebase.Homebase):
            self.__homebases.append(cell)
        elif isinstance(cell, attacker.Attacker):
            self.__attackers.append(cell)
        elif isinstance(cell, rotator.Rotator):
            self.__rotators.append(cell)