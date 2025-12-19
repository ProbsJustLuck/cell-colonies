import classes.entity as entity
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator

CELL_TYPES: list[type[entity.Entity]] = [
    homebase.Homebase,
    attacker.Attacker,
    rotator.Rotator
]

SPAWNABLE_CELLS: list[type[entity.Entity]] = [
    attacker.Attacker,
    rotator.Rotator
]