from __future__ import annotations
import collections
import copy
import random
from typing import Any

from classes.game_state import GameState
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
from classes.position import Position
import classes.entity as entity
import classes.wall as wall
from classes.cell import Cell
from classes.ui.colors import TeamColor
from classes.ui.typewriter import Typewriter

from util.game_states import States
import util.cell_registry as cell_registry
from util.ui_helpers import get_font


class WorldManager:
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30, seed: int | None = None):
        self.__world_size = size
        self.__world_map: list[list[entity.Entity | None]] = [[None for _ in range(size)] for _ in range(size)]

        # Deterministic rng
        self.__seed = random.randrange(2**32)
        if seed is not None: self.__seed = seed
        self.__rng = random.Random(self.__seed)

        self.__tick_history: collections.deque[dict[str, Any]] = collections.deque(maxlen=States.max_history)

        self.__typewriter: Typewriter = Typewriter(get_font(20), speed=30)

        self.__current_tick: int = 0
        self.__id_counter: int = 0
        self.__debug = True # Whether or not to check if the empty set is empty (im paranoid but want efficiency)

        self.__homebases: list[homebase.Homebase] = []
        self.__rotators: list[rotator.Rotator] = []
        self.__attackers: list[attacker.Attacker] = []
        self.__walls: list[wall.Wall] = []


        self.__empty_spaces: set[Position] = {
            Position(i, j)
            for i in range(size)
            for j in range(size)
        }

        colors = list(TeamColor)
        self.rng.shuffle(colors)
        colors = colors[:homebases] # limit
        
        for i in range(homebases): # Randomly spawn homebases
            color = colors[i].value
            homebase.Homebase(self.__random_empty(), self, color, health=3)

        for _ in range(walls): # Randomly spawn walls
            wall.Wall(self.__random_empty(), self)


    @property
    def rng(self) -> random.Random: return self.__rng


    @property
    def empty_spaces(self) -> frozenset[Position]: return frozenset(self.__empty_spaces)


    @property
    def size(self) -> int: return self.__world_size


    @property
    def homebases(self) -> list[homebase.Homebase]: return self.__homebases # Returns the alive homebases.
    

    @property
    def map(self) -> list[list[entity.Entity | None]]: return self.__world_map # Returns the world map.


    @property
    def current_tick(self) -> int: return self.__current_tick


    @property
    def seed(self) -> int: return self.__seed


    @property
    def walls_amount(self) -> int: return len(self.__walls)


    @property
    def typewriter(self) -> Typewriter: return self.__typewriter
    


    def __snapshot(self) -> Any: # takes a screenshot of the current map (for )
        return {
            "map": copy.deepcopy(self.__world_map),
            "tick": self.__current_tick,
            "rng_state": self.rng.getstate(),
        }
    

    def restore_snapshot(self, steps: int) -> bool:
        snapshot = self.get_snapshot(steps)
        if not snapshot: return False

        for _ in range(steps):
            self.__tick_history.pop()

        self.__world_map = snapshot["map"]
        self.__current_tick = snapshot["tick"]
        self.rng.setstate(snapshot["rng_state"])

        self.__homebases = []
        self.__rotators = []
        self.__attackers = []
        self.__walls = []
        self.__empty_spaces = set()
        for x in range(self.__world_size):
            for y in range(self.__world_size):
                entity = self.__world_map[x][y]
                if entity is None:
                    self.__empty_spaces.add(Position(x, y))
                elif isinstance(entity, homebase.Homebase):
                    self.__homebases.append(entity)
                elif isinstance(entity, rotator.Rotator):
                    self.__rotators.append(entity)
                elif isinstance(entity, attacker.Attacker):
                    self.__attackers.append(entity)
                elif isinstance(entity, wall.Wall):
                    self.__walls.append(entity)

        return True


    def get_snapshot(self, step: int) -> dict[str, Any] | None:
        if step <= 0 or step > len(self.__tick_history): return None
        return self.__tick_history[-step]


    def __check_empty(self) -> None: # Testing to make sure the empty set is synced
        empty_spaces = {
            Position(i, j)
            for i in range(self.__world_size)
            for j in range(self.__world_size)
            if self.__world_map[i][j] is None
        }
        assert empty_spaces == self.__empty_spaces, "The empty space set was desynced! Something is wrong..."


    def new_id(self) -> int:
        self.__id_counter += 1
        return self.__id_counter


    def __random_empty(self) -> Position:
        if not self.__empty_spaces: raise RuntimeError("Uh oh. No more empty spaces remaining!")

        pos = self.rng.choice(sorted(self.__empty_spaces, key=lambda pos: (pos.x, pos.y)))
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
    

    def tick(self) -> GameState:
        self.__tick_history.append(self.__snapshot())
        self.__current_tick += 1

        if self.__debug and self.__current_tick % 20 == 0: self.__check_empty()

        # Kill dead cells
        for atk in sorted(self.__attackers, key=lambda cell: (cell.pos.x, cell.pos.y)):
            if atk.health < 1: atk.deregister(self)
            if atk.hurt: atk.hurt = False

        for rot in sorted(self.__rotators, key=lambda cell: (cell.pos.x, cell.pos.y)):
            if rot.health < 1: rot.deregister(self)

        # Tick normally
        for homebase in sorted(self.__homebases, key=lambda hb: (hb.pos.x, hb.pos.y)):
            if not homebase.alive: continue
            homebase.age += 1
            homebase.tick(self)
        
        for rotator in sorted(self.__rotators, key=lambda rot: (rot.pos.x, rot.pos.y)):
            if not rotator.alive: continue
            rotator.age += 1
            rotator.tick(self)
        
        for attacker in sorted(self.__attackers, key=lambda atk: (atk.pos.x, atk.pos.y)):
            if not attacker.alive: continue
            attacker.age += 1
            attacker.tick(self)

        for wall in sorted(self.__walls, key=lambda wall: (wall.pos.x, wall.pos.y)):
            wall.age += 1

        # Kill dead homebases
        for homebase in self.__homebases[:]:
            if homebase.health <= 0: homebase.deregister(self)

        if(len(self.__homebases) == 1):
            return GameState.WIN
        elif(len(self.__homebases) == 0):
            return GameState.LOSS
        return GameState.CONTINUE


    def spawn_cell(self, pos: Position, homebase: homebase.Homebase, type: Cell | None = None, target: Position | homebase.Homebase | None = None) -> entity.Entity: 
        if not type:
            choice = self.rng.choices(
                population= [val for val in cell_registry.SPAWNABLE_CELLS],
                weights=[85, 15], # attacker, rotator
                k=1
            )[0]
            new_cell: entity.Entity = choice.spawn(pos, homebase, self, target)
        else:
            new_cell: entity.Entity = type.spawn(pos, homebase, self, target)
        
        return new_cell


    def get_cell(self, pos: Position) -> entity.Entity | None:
        if self.in_bounds(pos): return self.__world_map[pos.x][pos.y]
        return None
    

    def get_id(self, pos: Position) -> int | None:
        entity = self.__world_map[pos.x][pos.y]

        if self.in_bounds(pos) and entity: return entity.id
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
        elif isinstance(cell, wall.Wall):
            if cell in self.__walls: self.__walls.remove(cell)


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
        elif isinstance(cell, wall.Wall):
            self.__walls.append(cell)
