import time
import os
from classes.world_manager import WorldManager
import classes.homebase as homebase
import classes.attacker as attacker
import classes.rotator as rotator
import classes.wall as wall
import classes.entity as entity

EMOJIS: dict[entity.Entity | None, str] = {
    homebase.Homebase: "🏠",
    attacker.Attacker: "👾",
    rotator.Rotator: "🔄",
    wall.Wall: "🧱",
    type(None): "⬛",
} # type: ignore

def render(world: WorldManager) -> None:
    grid = world.map
    size = len(grid)

    print("\n" * 2)
    for x in range(size):
        row = ""
        for y in range(size):
            cell = grid[x][y]
            emoji = EMOJIS.get(type(cell), "❓") # type: ignore
            row += emoji + " " # type: ignore
        print(row) # type: ignore
    print("\n")

def main():
    world = WorldManager(size=30, homebases=2, walls=30)

    tick = 0
    while True:
        os.system("cls")
        print(f"Tick: {tick}")

        ended = world._WorldManager__tick() # type: ignore
        if ended:
            print("Game ended!")
            render(world)
            break
        render(world)

        count = 0
        for hb in world.homebases:
            print(f"Homebase # {count}: {hb.health}")
            count += 1

        tick += 1
        time.sleep(1.5)

if __name__ == "__main__":
    main()
