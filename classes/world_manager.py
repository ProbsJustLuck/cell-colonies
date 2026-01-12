from __future__ import annotations
import copy
import random
import bisect
from typing import Any

from classes.game_state import GameState
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
import classes.teleporter as teleporter
from classes.position import Position, get_pos
import classes.entity as entity
import classes.wall as wall
import classes.annihilator as annihilator
from classes.cell import Cell

from util.game_states import States
import util.cell_registry as cell_registry


class WorldManager:
    def __init__(self, size: int = 10, homebases: int = 4, walls: int = 30, seed: int | None = None):
        self.__world_size = size
        self.__world_map: list[list[entity.Entity | None]] = [[None for _ in range(size)] for _ in range(size)]

        # Deterministic rng
        self.__seed = random.randrange(2**32)
        if seed is not None: self.__seed = seed
        self.__rng = random.Random(self.__seed)

        self.__tick_history: dict[int, dict[str, Any]] = {}

        self.__snapshot_frequency = States.snapshot_frequency

        self.__current_tick: int = 0
        self.__id_counter: int = 0

        self.__homebases: list[homebase.Homebase] = []
        self.__rotators: list[rotator.Rotator] = []
        self.__attackers: list[attacker.Attacker] = []
        self.__walls: list[wall.Wall] = []
        self.__teleporters: list[teleporter.Teleporter] = []
        self.__annihilators: list[annihilator.Annihilator] = []


        self.__empty_spaces: set[Position] = {
            get_pos((i, j))
            for i in range(size)
            for j in range(size)
        }

        colors = States.allowed_colonies.copy()
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
    def history(self) -> dict[int, dict[str, Any]]: return self.__tick_history


    @property
    def snapshot_frequency(self) -> int: return self.__snapshot_frequency
    

    def __snapshot(self) -> Any: # takes a screenshot of the current map (for )
        return {
            "map": copy.deepcopy(self.__world_map),
            "tick": self.__current_tick,
            "rng_state": self.rng.getstate(),
            "id_count": self.__id_counter
        }
    

    def restore_snapshot(self, steps: int) -> bool:
        snapshot, rem = self.get_snapshot(steps)
        if not snapshot or rem is None: return False

        self.__world_map = snapshot["map"]
        self.__current_tick = snapshot["tick"]
        self.rng.setstate(snapshot["rng_state"])
        self.__id_counter = snapshot["id_count"]

        self.__homebases = []
        self.__rotators = []
        self.__attackers = []
        self.__walls = []
        self.__teleporters = []
        self.__annihilators = []
        self.__empty_spaces = set()
        for x in range(self.__world_size):
            for y in range(self.__world_size):
                entity = self.__world_map[x][y]
                if entity is None: self.__empty_spaces.add(get_pos((x, y)))
                
                elif isinstance(entity, homebase.Homebase): self.__homebases.append(entity)

                elif isinstance(entity, rotator.Rotator): self.__rotators.append(entity)

                elif isinstance(entity, attacker.Attacker): self.__attackers.append(entity)

                elif isinstance(entity, wall.Wall): self.__walls.append(entity)

                elif isinstance(entity, teleporter.Teleporter): self.__teleporters.append(entity)

                elif isinstance(entity, annihilator.Annihilator): self.__annihilators.append(entity)

        self.__attackers.sort()
        self.__rotators.sort()
        self.__homebases.sort()
        self.__walls.sort()
        self.__teleporters.sort()
        self.__annihilators.sort()

        for _ in range(rem):
            self.tick()

        return True


    def get_snapshot(self, step: int) -> tuple[dict[str, Any], int] | tuple[None, None]:
        if step <= 0 or step > self.__current_tick: return (None, None)

        target_tick = self.__current_tick - step
        rem = target_tick % self.__snapshot_frequency
        return (self.__tick_history[target_tick - rem], rem)


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
        if self.__current_tick % self.__snapshot_frequency == 0: self.__tick_history[self.__current_tick] = self.__snapshot()
        self.__current_tick += 1

        for homebase in self.__homebases[:]:
            if not homebase.alive: continue
            homebase.age += 1
            homebase.tick(self)
        
        for rotator in self.__rotators[:]:
            if not rotator.alive: continue

            if rotator.health <= 0.0:
                rotator.deregister(self)
                continue

            rotator.age += 1
            rotator.tick(self)

        for teleporter in self.__teleporters[:]:
            if not teleporter.alive: continue

            if teleporter.health <= 0.0:
                teleporter.deregister(self)
                continue

            teleporter.age += 1
            teleporter.tick(self)

        for annihilator in self.__annihilators[:]:
            if not annihilator.alive: continue

            if annihilator.health <= 0.0:
                annihilator.deregister(self)
                continue

            annihilator.age += 1
            annihilator.tick(self)
        
        for attacker in self.__attackers[:]:
            if not attacker.alive: continue

            # time spent here: 3 hours
            if attacker.skip:
                if self.__current_tick > attacker.hurt_until: attacker.deregister(self)
                continue

            if attacker.hurt and self.__current_tick > attacker.hurt_until:
                attacker.hurt = False

            if attacker.health <= 0:
                attacker.hurt = True
                attacker.hurt_until = self.__current_tick
                attacker.skip = True
                continue

            attacker.age += 1
            attacker.tick(self)

        for wall in self.__walls[:]: wall.age += 1

        # Kill dead homebases
        for homebase in self.__homebases[:]:
            if homebase.health <= 0.0: homebase.deregister(self)

        if(len(self.__homebases) == 1): return GameState.WIN
        elif(len(self.__homebases) == 0): return GameState.LOSS
        return GameState.CONTINUE


    def spawn_cell(self, pos: Position, homebase: homebase.Homebase, type: Cell | None = None, target: Position | homebase.Homebase | None = None) -> entity.Entity: 
        if not type:
            choice = self.rng.choices(
                population= [val for val in cell_registry.spawnable_cells],
                weights=cell_registry.spawn_rates, # attacker, rotator
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
        if not self.in_bounds(pos): return None
        entity = self.__world_map[pos.x][pos.y]

        if entity: return entity.id
        return None
    

    def in_bounds(self, pos: Position) -> bool: return 0 <= pos.x < self.__world_size and 0 <= pos.y < self.__world_size


    def is_blocking(self, pos: Position) -> bool: 
        if not self.in_bounds(pos): return True
        return isinstance(self.__world_map[pos.x][pos.y], (homebase.Homebase, wall.Wall))


    def deregister(self, cell: entity.Entity) -> None:
        self.__world_map[cell.pos.x][cell.pos.y] = None # Sets the cell to None in the world map.
        self.__empty_spaces.add(cell.pos)

        if isinstance(cell, homebase.Homebase):
            index = bisect.bisect_left(self.__homebases, cell)
            if index < len(self.__homebases) and self.__homebases[index].id == cell.id: self.__homebases.pop(index)

        elif isinstance(cell, attacker.Attacker):
            index = bisect.bisect_left(self.__attackers, cell)
            if index < len(self.__attackers) and self.__attackers[index].id == cell.id: self.__attackers.pop(index)

        elif isinstance(cell, rotator.Rotator):
            index = bisect.bisect_left(self.__rotators, cell)
            if index < len(self.__rotators) and self.__rotators[index].id == cell.id: self.__rotators.pop(index)

        elif isinstance(cell, wall.Wall):
            index = bisect.bisect_left(self.__walls, cell)
            if index < len(self.__walls) and self.__walls[index].id == cell.id: self.__walls.pop(index)

        elif isinstance(cell, teleporter.Teleporter):
            index = bisect.bisect_left(self.__teleporters, cell)
            if index < len(self.__teleporters) and self.__teleporters[index].id == cell.id: self.__teleporters.pop(index)

        elif isinstance(cell, annihilator.Annihilator):
            index = bisect.bisect_left(self.__annihilators, cell)
            if index < len(self.__annihilators) and self.__annihilators[index].id == cell.id: self.__annihilators.pop(index)


    def register(self, cell: entity.Entity) -> None: # Register the cell to each entity sublist
        if self.__world_map[cell.pos.x][cell.pos.y] is not None:
            raise ValueError(f"Space is occupied at {cell.pos}")
        
        self.__world_map[cell.pos.x][cell.pos.y] = cell
        self.__empty_spaces.discard(cell.pos)

        if isinstance(cell, homebase.Homebase):
            index = bisect.bisect_right(self.__homebases, cell)
            self.__homebases.insert(index, cell)

        elif isinstance(cell, attacker.Attacker):
            index = bisect.bisect_right(self.__attackers, cell)
            self.__attackers.insert(index, cell)

        elif isinstance(cell, rotator.Rotator):
            index = bisect.bisect_right(self.__rotators, cell)
            self.__rotators.insert(index, cell)

        elif isinstance(cell, wall.Wall):
            index = bisect.bisect_right(self.__walls, cell)
            self.__walls.insert(index, cell)

        elif isinstance(cell, teleporter.Teleporter):
            index = bisect.bisect_right(self.__teleporters, cell)
            self.__teleporters.insert(index, cell)

        elif isinstance(cell, annihilator.Annihilator):
            index = bisect.bisect_right(self.__annihilators, cell)
            self.__annihilators.insert(index, cell)
