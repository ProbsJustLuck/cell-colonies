from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class ColorInfo:
    name: str
    primary: tuple[int, int, int, int]


class TeamColor(Enum):
    RED = ColorInfo(
        name="Red",
        primary=(220, 40, 40, 255),
    )

    ORANGE = ColorInfo(
        name="Orange",
        primary=(255, 140, 40, 255),
    )

    YELLOW = ColorInfo(
        name="Yellow",
        primary=(240, 220, 60, 255)
    )

    LIME = ColorInfo(
        name="Lime",
        primary=(170, 230, 70, 255)
    )

    GREEN = ColorInfo(
        name="Green",
        primary=(50, 180, 90, 255),
    )

    LIGHT_BLUE = ColorInfo(
        name="Light Blue",
        primary=(90, 190, 255, 255),
    )

    BLUE = ColorInfo(
        name="Blue",
        primary=(60, 90, 220, 255),
    )

    MAGENTA = ColorInfo(
        name="Magenta",
        primary=(200, 60, 200, 255),
    )

    INDIGO = ColorInfo(
        name="Indigo",
        primary=(90, 70, 180, 255),
    )

    VIOLET = ColorInfo(
        name="Violet",
        primary=(170, 90, 220, 255),
    )

    GREY = ColorInfo(
        name="Grey",
        primary=(140, 140, 140, 255),
    )

    WHITE = ColorInfo(
        name="White",
        primary=(235, 235, 235, 255),
    )

    BLACK = ColorInfo(
        name="Black",
        primary=(40, 40, 40, 255),
    )
