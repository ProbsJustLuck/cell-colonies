import classes.entity as entity
import classes.homebase as homebase

class Cell(entity.Entity):
    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase):
        super().__init__(x, y)

        self._homebase: homebase.Homebase = homebase_link # The homebase that this cell belongs to.

    def _get_homebase(self) -> homebase.Homebase:
        return self._homebase # Returns the homebase that this cell belongs to.
    
    def _pathfind(self) -> None:
        pass # Pathfinding logic for the cell, A* algorithm later

    def _move(self) -> None:
        pass # Moves the cell toward its target, each cell implements this differently. Uses the pathfind() method

    