import random
from typing import Optional

import classes.cell as cell
import classes.homebase as homebase
from classes.position import Position
import classes.world_manager
import classes.entity as entity


class Rotator(cell.Cell):
    __type: str = "UTILITY"

    def __init__(self, x: int, y: int, homebase_link: homebase.Homebase, world_manager: classes.world_manager.WorldManager, health: int = 2):
        super().__init__(x, y, homebase_link)

        self.__health: int = health

        self.__homebase: homebase.Homebase = homebase_link

        self.__set_target(world_manager=world_manager) # Sets the target to a random space within 5 blocks of its Homebase

        self.__stationary: bool = False

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

    def change_health(self, delta: int): self.__health += delta

    def __move(self) -> None: # type: ignore
        pass

    def __rotate_target(self) -> None: # type: ignore
        pass

    def __get_surroundings(self, world_manager: classes.world_manager.WorldManager) -> list[Optiona[entity.Entity]]: # type: ignore
        l: list[Optional[entity.Entity]] = []

        x_pos = self.pos.get_x()
        y_pos = self.pos.get_y()

        dir_mapping: dict[str, tuple[int, int]] = world_manager.get_mappings()
        cells: tuple[Optional[entity.Entity], ...] = (
            world_manager.get_map()[x_pos + dir_mapping["N"][0]][y_pos + dir_mapping["N"][1]],
            world_manager.get_map()[x_pos + dir_mapping["S"][0]][y_pos + dir_mapping["S"][1]],
            world_manager.get_map()[x_pos + dir_mapping["E"][0]][y_pos + dir_mapping["E"][1]],
            world_manager.get_map()[x_pos + dir_mapping["W"][0]][y_pos + dir_mapping["W"][1]]
        )

        for cell in cells:
            if cell != None: l.append(cell)

        return l