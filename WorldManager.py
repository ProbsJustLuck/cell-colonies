import Position
import Entity

class WorldManager:
    
    def __init__(self, size: int, homebases: int = 4, walls: int = 30):
        self._WorldMap: list[list[None]] = [[None for _ in range(size)] for _ in range(size)]

        # for i in range(homebases):
        #     pass
        

    def _get_empty_cells(self) -> list[Position.Position]:
        l: list[Position.Position] = []

        for i in range(len(self._WorldMap)):
            for j in range(len(self._WorldMap[i])):
                if self._WorldMap[i][j] == None:
                    l.append(Position.Position(i, j))
        return l
    
    def deregister(self, cell: Entity.Entity) -> None:
        pass