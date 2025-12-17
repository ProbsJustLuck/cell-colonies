import random

import classes.cell as cell
import classes.homebase as homebase
from classes.position import Position
import classes.world_manager


class Rotator(cell.Cell):
    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: classes.world_manager.WorldManager, health: int = 2):
        super().__init__(x, y, homebase_link)

        self.__health = health

        self.__homebase = homebase_link

        self.__set_target(world_manager=world_manager) # Sets the target to a random space within 5 blocks of its Homebase

    def __set_target(self, world_manager: classes.world_manager.WorldManager) -> None:
        free_spaces: list[Position] = world_manager.get_empty_cells()
        for i in range(len(free_spaces)):
            dx: int = abs(free_spaces[i].get_x() - self.__homebase.get_pos().get_x())
            dy: int = abs(free_spaces[i].get_y() - self.__homebase.get_pos().get_y())
            total: int = dx + dy

            if total > 5: free_spaces.pop(i)

        if len(free_spaces) == 0: return
        num: int = random.randint(0, len(free_spaces))
        self.target = Position(free_spaces[num].get_x(), free_spaces[num].get_y())