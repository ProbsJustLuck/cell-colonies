from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class ColorInfo:
    """
    Holds color information for a team color.
    """
    name: str
    primary: tuple[int, int, int]
    border: tuple[int, int, int]
    highlight: tuple[int, int, int]

class TeamColor(Enum):
    """
    Represents different team colors with their associated color information. Hardedcoded colors for every team.
    """
    RED = ColorInfo(
        name="Red",
        primary=(220, 40, 40),
        border=(140, 20, 20),
        highlight=(255, 120, 120),
    )

    ORANGE = ColorInfo(
        name="Orange",
        primary=(255, 140, 40),
        border=(170, 90, 20),
        highlight=(255, 200, 120),
    )

    YELLOW = ColorInfo(
        name="Yellow",
        primary=(240, 220, 60),
        border=(170, 150, 30),
        highlight=(255, 245, 150),
    )

    LIME = ColorInfo(
        name="Lime",
        primary=(170, 230, 70),
        border=(110, 160, 40),
        highlight=(220, 255, 150),
    )

    GREEN = ColorInfo(
        name="Green",
        primary=(50, 180, 90),
        border=(30, 110, 60),
        highlight=(120, 240, 170),
    )

    LIGHT_BLUE = ColorInfo(
        name="Light Blue",
        primary=(90, 190, 255),
        border=(50, 120, 180),
        highlight=(170, 230, 255),
    )

    BLUE = ColorInfo(
        name="Blue",
        primary=(60, 90, 220),
        border=(30, 50, 140),
        highlight=(130, 160, 255),
    )

    MAGENTA = ColorInfo(
        name="Magenta",
        primary=(200, 60, 200),
        border=(120, 30, 120),
        highlight=(255, 140, 255),
    )

    INDIGO = ColorInfo(
        name="Indigo",
        primary=(90, 70, 180),
        border=(50, 40, 120),
        highlight=(160, 140, 255),
    )

    VIOLET = ColorInfo(
        name="Violet",
        primary=(170, 90, 220),
        border=(100, 50, 140),
        highlight=(220, 160, 255),
    )

    GRAY = ColorInfo(
        name="Gray",
        primary=(140, 140, 140),
        border=(90, 90, 90),
        highlight=(200, 200, 200),
    )

    WHITE = ColorInfo(
        name="White",
        primary=(235, 235, 235),
        border=(160, 160, 160),
        highlight=(255, 255, 255),
    )

    BLACK = ColorInfo(
        name="Black",
        primary=(40, 40, 40),
        border=(15, 15, 15),
        highlight=(90, 90, 90),
    )
