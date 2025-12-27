from __future__ import annotations
import heapq
from typing import Callable

from classes.position import Position
from constants import Constants

def __h(a: Position, b: Position) -> int: return abs(a.x - b.x) + abs(a.y - b.y) # uses manhatten distance


def __reconstruct(current: Position, came_from: dict[Position, Position]) -> list[Position]:
    path: list[Position] = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path[1:] # Don't include the start


def pathfind(start: Position, goal: Position, in_bounds: Callable[[Position], bool], is_blocked: Callable[[Position], bool]) -> list[Position]:
    if start == goal: return [] # If the entity pathfinds to itself

    open_heap: list[tuple[int, int, Position]] = []
    heapq.heappush(open_heap, (0, 0, start))
    came_from: dict[Position, Position] = {}

    g_score: dict[Position, int] = {start: 0}
    f_score: dict[Position, int] = {start: __h(start, goal)}

    open_set = {start}
    counter = 0 # handles tiebreakers

    while open_heap:
        current = heapq.heappop(open_heap)[2]
        open_set.discard(current)

        if current == goal: return __reconstruct(current, came_from)

        for _, (dx, dy) in Constants.DIRECTION_MAPPINGS.items():
            neighbor = Position(current.x + dx, current.y + dy)

            if not in_bounds(neighbor):
                continue
            if is_blocked(neighbor) and neighbor != goal:
                continue

            tentative_g = g_score[current] + 1 # all paths are weighted 1
            if tentative_g < g_score.get(neighbor, 10**9): # inf
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + __h(neighbor, goal)
                f_score[neighbor] = f
                if neighbor not in open_set:
                    counter += 1
                    heapq.heappush(open_heap, (f, counter, neighbor))
                    open_set.add(neighbor)

    return []  # no path
