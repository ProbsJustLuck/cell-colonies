from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from classes.cell import Cell
from classes.direction import Direction
import classes.entity as entity
from classes.position import Position

from util import assets
from constants import Constants

if TYPE_CHECKING:
    from classes.world_manager import WorldManager
    from classes.ui.colors import ColorInfo


class Homebase(entity.Entity):
    __type: str = "CORE"
    

    def __init__(self, pos: Position, world_manager: "WorldManager", color: ColorInfo, health: int = 10):
        super().__init__(pos, world_manager)

        self.__health: int = health # The health of the homebase.
        self.__cells: list[entity.Entity] = [] # The cells that belong to this homebase.

        self.__color = color
        self.__icon = assets.base_homebase.copy()
        self.__icon.fill(self.__color.primary, special_flags=pygame.BLEND_RGBA_MULT)

        self.__attacker_icon = {
            Direction.NORTH: assets.base_attacker_up.copy(),
            Direction.EAST: assets.base_attacker_right.copy(),
            Direction.SOUTH: assets.base_attacker_down.copy(),
            Direction.WEST: assets.base_attacker_left.copy()
        }
        for surf in self.__attacker_icon.values():
            surf.fill(self.__color.primary, special_flags=pygame.BLEND_RGBA_MULT)

        self.__rotator_icon = assets.base_rotator.copy()
        self.__rotator_icon.fill(self.__color.primary, special_flags=pygame.BLEND_RGBA_MULT)

        self.__spawn_ticks: int = 0

        self.__ticks_since_target: int = 0 # The number of ticks since this Homebase had an attacker successfully find a path to it.
        self.__waiting_for_attacker = False

    @property
    def type(self) -> str: return self.__type # Returns this homebase's type (always CORE)


    @property
    def icon(self) -> pygame.Surface: return self.__icon # Returns the icon for this homebase.


    @property
    def attacker_icon(self) -> dict[Direction, pygame.Surface]: return self.__attacker_icon


    @property
    def rotator_icon(self) -> pygame.Surface: return self.__rotator_icon


    @property
    def health(self) -> int: return self.__health # Returns the health for this homebase


    @property
    def color(self) -> ColorInfo: return self.__color


    def tick(self, world_manager: "WorldManager"): 
        if self.__health < 0:
            self._deregister(world_manager)
            print("A HOMEBASE DIED!")
            return
        
        self.__spawn_ticks += 1
        
        if self.__spawn_ticks == 3:
            self.spawn_cell(world_manager)
            self.__spawn_ticks = 0

        if self.__ticks_since_target > 8 and not self.__waiting_for_attacker: # If we haven't been targetted in at least 9 ticks, then force an attacker to spawn
            self.__waiting_for_attacker = True

            choices = [homebase for homebase in world_manager.homebases if homebase is not self]
            if choices: world_manager.rng.choice(choices).spawn_cell(world_manager, target=self)
        if self.__ticks_since_target > 10 and self.__waiting_for_attacker:
            self._deregister(world_manager)
            return            

        self.__ticks_since_target += 1

        


    def change_health(self, delta: int) -> None: self.__health += delta # Changes the health of this homebase


    def reset_target_count(self) -> None: 
        self.__ticks_since_target = 0 # Resets the target count to 0
        self.__waiting_for_attacker = False


    def _deregister(self, world_manager: "WorldManager"):
        for cell in self.__cells[:]:
            if cell.alive:
                cell._deregister(world_manager)
                
        self.__cells.clear()
        super()._deregister(world_manager)


    def remove_cell(self, cell: entity.Entity) -> None: 
        if cell in self.__cells: self.__cells.remove(cell)


    def spawn_cell(self, world_manager: "WorldManager", type: Cell | None = None, target: Position | Homebase | None = None) -> entity.Entity | None:
        base: Position = self.pos
        mapping = Constants.DIRECTION_MAPPINGS

        positions: list[Position] = [
            Position(base.x + mapping[Direction.NORTH][0], base.y + mapping[Direction.NORTH][1]),
            Position(base.x + mapping[Direction.SOUTH][0], base.y + mapping[Direction.SOUTH][1]),
            Position(base.x + mapping[Direction.EAST][0], base.y + mapping[Direction.EAST][1]),
            Position(base.x + mapping[Direction.WEST][0], base.y + mapping[Direction.WEST][1])
        ]
        positions = [pos for pos in positions if world_manager.in_bounds(pos)]

        world_manager.rng.shuffle(positions)
        for pos in positions:
            if world_manager.get_cell(pos) is None:
                cell = world_manager.spawn_cell(pos, self, type, target)
                self.__cells.append(cell)
                return cell
            
        # Fail the spawn attempt is no square is free.