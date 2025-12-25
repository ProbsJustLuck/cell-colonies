from __future__ import annotations
import random
from typing import TYPE_CHECKING

from classes.game_state import GameState
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
from classes.position import Position
import classes.entity as entity
import classes.wall as wall
from classes.cell import Cell
import util.cell_registry as cell_registry


if TYPE_CHECKING:
    pass
    

class WorldManager:
    
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30):
        self.__world_size = size
        self.__world_map: list[list[entity.Entity | None]] = [[None for _ in range(size)] for _ in range(size)]

        self.__current_tick: int = 0
        self.__debug = True # Whether or not to check if the empty set is empty (im paranoid but want efficiency)

        self.__homebases: list[homebase.Homebase] = []
        self.__rotators: list[rotator.Rotator] = []
        self.__attackers: list[attacker.Attacker] = []

        self.__empty_spaces: set[Position] = {
            Position(i, j)
            for i in range(size)
            for j in range(size)
        }
        
        for _ in range(homebases): # Randomly spawn homebases
            homebase.Homebase(self.__random_empty(), self, health=1)

        for _ in range(walls): # Randomly spawn walls
            wall.Wall(self.__random_empty(), self)        


    def get_empty_spaces(self) -> frozenset[Position]: return frozenset(self.__empty_spaces)


    def __assert_empty(self) -> None: # Testing to make sure the empty set is synced
        empty_spaces = {
            Position(i, j)
            for i in range(self.__world_size)
            for j in range(self.__world_size)
            if self.__world_map[i][j] is None
        }
        assert empty_spaces == self.__empty_spaces, "Empty-space set was desynced! Something is making ghost spaces..."



    def __random_empty(self) -> Position:
        if not self.__empty_spaces: raise RuntimeError("Uh oh. No more empty spaces remaining!")

        pos = random.choice(tuple(self.__empty_spaces))
        self.__empty_spaces.remove(pos)
        return pos
    

    def move_entity(self, entity: entity.Entity, pos: Position) -> None:
        if not self.in_bounds(pos): raise ValueError(f"Move was out of bounds! At {pos}")
        if self.__world_map[pos.x][pos.y]: raise ValueError(f"Destination was occupied! At {pos}")

        if pos == entity.pos: return

        self.__world_map[entity.pos.x][entity.pos.y] = None
        self.__empty_spaces.add(entity.pos)

        self.__world_map[pos.x][pos.y] = entity
        self.__empty_spaces.discard(pos)

        entity.pos = pos
    

    def __tick(self) -> GameState: # type: ignore
        self.__current_tick += 1

        if self.__debug and self.__current_tick % 20 == 0: self.__assert_empty()


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
            return GameState.WIN # TODO: end the game, will be 
        elif(len(self.__homebases) == 0):
            return GameState.LOSS
        return GameState.CONTINUE
    

    def run(self) -> bool:
        ended: GameState = GameState.CONTINUE
        while ended is GameState.CONTINUE:
            ended = self.__tick()
        return True


    @property
    def homebases(self) -> list[homebase.Homebase]: return self.__homebases # Returns the alive homebases.
    

    @property
    def map(self) -> list[list[entity.Entity | None]]: return self.__world_map # Returns the world map.


    def spawn_cell(self, pos: Position, homebase: homebase.Homebase, type: Cell | None = None, target: Position | homebase.Homebase | None = None) -> entity.Entity: # type: ignore
        if not type:
            choice = random.choices(
                population= [val for val in cell_registry.SPAWNABLE_CELLS],
                weights=[85, 15],   # attacker, rotator
                k=1
            )[0]
            new_cell: entity.Entity = choice.spawn(pos, homebase, self, target)
        else:
            new_cell: entity.Entity = type.spawn(pos, homebase, self, target)
        
        return new_cell


    def get_cell(self, pos: Position) -> entity.Entity | None:
        if self.in_bounds(pos): return self.__world_map[pos.x][pos.y]
        return None
    

    def in_bounds(self, pos: Position) -> bool: return 0 <= pos.x < self.__world_size and 0 <= pos.y < self.__world_size


    def is_blocking(self, pos: Position) -> bool: 
        if not self.in_bounds(pos): return True
        return isinstance(self.__world_map[pos.x][pos.y], (homebase.Homebase, wall.Wall))


    def deregister(self, cell: entity.Entity) -> None:
        self.__world_map[cell.pos.x][cell.pos.y] = None # Sets the cell to None in the world map.
        self.__empty_spaces.add(cell.pos)

        if isinstance(cell, homebase.Homebase):
            if cell in self.__homebases: self.__homebases.remove(cell)
        elif isinstance(cell, attacker.Attacker):
            if cell in self.__attackers: self.__attackers.remove(cell)
        elif isinstance(cell, rotator.Rotator):
            if cell in self.__rotators: self.__rotators.remove(cell)


    def register(self, cell: entity.Entity) -> None: # Register the cell to each entity sublist
        if self.__world_map[cell.pos.x][cell.pos.y] is not None:
            raise ValueError(f"Space is occupied at {cell.pos}")
        
        self.__world_map[cell.pos.x][cell.pos.y] = cell
        self.__empty_spaces.discard(cell.pos)

        if isinstance(cell, homebase.Homebase):
            self.__homebases.append(cell)
        elif isinstance(cell, attacker.Attacker):
            self.__attackers.append(cell)
        elif isinstance(cell, rotator.Rotator):
            self.__rotators.append(cell)