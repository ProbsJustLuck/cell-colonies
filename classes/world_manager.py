from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from classes.homebase import Homebase # type: ignore
import classes.position as position

if TYPE_CHECKING:
    import classes.entity as entity
    import classes.homebase as homebase
    import classes.attacker as attacker
    import classes.rotator as rotator

class WorldManager:
    
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30):
        self._world_map: list[list[Optional[entity.Entity]]] = [[None for _ in range(size)] for _ in range(size)]

        self._current_tick: int = 0

        self._homebases: list[homebase.Homebase] = []
        self._rotators: list[entity.Entity] = []
        self._attackers: list[entity.Entity] = []

        self._mappings: dict[str, tuple[int, int]] = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)   
        }


        # for i in range(homebases):
        #     pass
        

    def get_empty_cells(self) -> list[position.Position]: # type: ignore
        l: list[position.Position] = []

        for i in range(len(self._world_map)):
            for j in range(len(self._world_map[i])):
                if self._world_map[i][j] == None:
                    l.append(position.Position(i, j))
        return l
    

    def __tick(self) -> None: # type: ignore
        self._current_tick += 1

        for homebase in self._homebases:
            homebase.tick()
        
        for rotator in self._rotators:
            rotator.tick()
        
        for attacker in self._attackers:
            attacker.tick()
    

    def run(self) -> None:
        pass # Main loop of the world manager.


    def __draw(self) -> None: # type: ignore
        pass # Draws the world map to the screen.


    def get_homebases(self) -> list[homebase.Homebase]: return self._homebases # Returns the alive homebases.
    

    def get_map(self) -> list[list[Optional[entity.Entity]]]: return self._world_map # Returns the world map.
    

    def get_mappings(self) -> dict[str, tuple[int, int]]: return self._mappings # Returns the mappings, aka directions in the form of 2d array values
    

    def deregister(self, cell: entity.Entity) -> None:
        self._world_map[cell.get_pos().get_x()][cell.get_pos().get_y()] = None # Sets the cell to None in the world map.


    def add_cell(self, cell: entity.Entity):
        if(type(cell) == homebase.Homebase):
            self._homebases.append(cell)
        elif(type(cell) == attacker.Attacker):
            self._attackers.append(cell)
        elif(type(cell) == rotator.Rotator):
            self._rotators.append(cell)