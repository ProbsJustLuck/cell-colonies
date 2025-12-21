import classes.entity as entity
import classes.cell as cell
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator

CELL_TYPES: tuple[type[entity.Entity], ...] = (
    homebase.Homebase,
    attacker.Attacker,
    rotator.Rotator
)

SPAWNABLE_CELLS: tuple[type[cell.Cell], ...] = (
    attacker.Attacker,
    rotator.Rotator
)