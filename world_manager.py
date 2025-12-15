from __future__ import annotations
from typing import TYPE_CHECKING
import position

if TYPE_CHECKING:
    import entity

class WorldManager:
    
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30):
        self._world_map: list[list[None]] = [[None for _ in range(size)] for _ in range(size)]

        self._current_tick: int = 0

        self._homebases: list[entity.Entity] = []
        self._rotators: list[entity.Entity] = []
        self._attackers: list[entity.Entity] = []


        # for i in range(homebases):
        #     pass
        

    def _get_empty_cells(self) -> list[position.Position]:
        l: list[position.Position] = []

        for i in range(len(self._world_map)):
            for j in range(len(self._world_map[i])):
                if self._world_map[i][j] == None:
                    l.append(position.Position(i, j))
        return l
    
    def run(self) -> None:
        pass # Main loop of the world manager.

    def get_homebases(self) -> list[entity.Entity]:
        return self._homebases # Returns the alive homebases.
    
    def get_map(self) -> list[list[None]]:
        return self._world_map # Returns the world map.
    
    def deregister(self, cell: entity.Entity) -> None:
        self._world_map[cell.get_pos()[0]][cell.get_pos()[1]] = None