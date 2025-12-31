from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class ColorInfo:
    name: str
    primary: tuple[int, int, int, int]
    border: tuple[int, int, int, int]
    highlight: tuple[int, int, int, int]

class TeamColor(Enum):
    RED = ColorInfo(
        name="Red",
        primary=(220, 40, 40, 150),
        border=(140, 20, 20, 150),
        highlight=(255, 120, 120, 150),
    )

    ORANGE = ColorInfo(
        name="Orange",
        primary=(255, 140, 40, 150),
        border=(170, 90, 20, 150),
        highlight=(255, 200, 120, 150),
    )

    YELLOW = ColorInfo(
        name="Yellow",
        primary=(240, 220, 60, 150),
        border=(170, 150, 30, 150),
        highlight=(255, 245, 150, 150),
    )

    LIME = ColorInfo(
        name="Lime",
        primary=(170, 230, 70, 150),
        border=(110, 160, 40, 150),
        highlight=(220, 255, 150, 150),
    )

    GREEN = ColorInfo(
        name="Green",
        primary=(50, 180, 90, 150),
        border=(30, 110, 60, 150),
        highlight=(120, 240, 170, 150),
    )

    LIGHT_BLUE = ColorInfo(
        name="Light Blue",
        primary=(90, 190, 255, 150),
        border=(50, 120, 180, 150),
        highlight=(170, 230, 255, 150),
    )

    BLUE = ColorInfo(
        name="Blue",
        primary=(60, 90, 220, 150),
        border=(30, 50, 140, 150),
        highlight=(130, 160, 255, 150),
    )

    MAGENTA = ColorInfo(
        name="Magenta",
        primary=(200, 60, 200, 150),
        border=(120, 30, 120, 150),
        highlight=(255, 140, 255, 150),
    )

    INDIGO = ColorInfo(
        name="Indigo",
        primary=(90, 70, 180, 150),
        border=(50, 40, 120, 150),
        highlight=(160, 140, 255, 150),
    )

    VIOLET = ColorInfo(
        name="Violet",
        primary=(170, 90, 220, 150),
        border=(100, 50, 140, 150),
        highlight=(220, 160, 255, 150),
    )

    GRAY = ColorInfo(
        name="Gray",
        primary=(140, 140, 140, 150),
        border=(90, 90, 90, 150),
        highlight=(200, 200, 200, 150),
    )

    WHITE = ColorInfo(
        name="White",
        primary=(235, 235, 235, 150),
        border=(160, 160, 160, 150),
        highlight=(255, 255, 255, 150),
    )

    BLACK = ColorInfo(
        name="Black",
        primary=(40, 40, 40, 150),
        border=(15, 15, 15, 150),
        highlight=(90, 90, 90, 150),
    )
