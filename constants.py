from classes.direction import Direction

DIRECTION_MAPPINGS: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.SOUTH: (0, 1),
    Direction.EAST: (1, 0),
    Direction.WEST: (-1, 0)   
}

POSITION_MAPPINGS: dict[tuple[int, int], Direction] = {
    value: key for key, value in DIRECTION_MAPPINGS.items()
}