"""
Newton's Laws, a simulator of physics at the scale of space

Global constants

by Jason Mott, copyright 2025
"""

__author__ = "Jason Mott"
__copyright__ = "Copyright 2026"
__license__ = "GPL 3.0"
__version__ = "0.2.4"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


# Global constants

from typing import List

VERSION: str = __version__

# No need to ever change these
G: float = 6.67430 * 10**-11  # Gravitational constant

# Sizes in Meters
AU: float = 1.495978707 * 10**11  # 1 Astronomical Unit
S: float = 6.957 * 10**8  # Radius of the Sun
J: float = 7.1492 * 10**7  # Radius of Jupiter
E: float = 6.3781 * 10**6  # Radius of the Earth

# Moons
GAN: float = 2.6341 * 10**6  # Radius of Ganymede (largest moon in solar system)
M: float = 1.7381 * 10**6  # Radius of the Moon
ENC: float = 0.2521 * 10**6  # Radius of Enceladus (small moon in solar system)
MIM: float = 0.1982 * 10**6  # Radius of Mimas (smallest round moon in solar system)

# Masses in Kilograms
# black hole, don't do it, your machine will collapse into itself!
B_MASS: float = 8.54 * 10**36  # Mass of Sagittarius A*

S_MASS: float = 1.98892 * 10**30  # Mass of the Sun
J_MASS: float = 1.899 * 10**27  # Mass of Jupiter
E_MASS: float = 5.972 * 10**24  # Mass of Earth

# Moons
GAN_MASS: float = 1.4819 * 10**23  # Mass of Ganymede (largest moon in solar system)
M_MASS: float = 7.342 * 10**22  # Mass of the Moon
ENC_MASS: float = 1.080318 * 10**20  # Mass of Enceladus (small moon in solar system)
MIM_MASS: float = (
    3.75094 * 10**19
)  # Mass of Mimas (smallest round moon in solar system)


LOW_VRAM: bool = False
TEXTURES_3D: bool = True
AU_SCALE_FACTOR: float = 12500  # Number of pixels to equal 1 AU

# Number of AU to equal universe size
UNIVERSE_SCALE: float = 100

# To see more than 1 blob at a time, make blobs this times bigger than real proportion to AU
CENTER_BLOB_SCALE: int = 20

BLOB_SCALE: int = 20

SCALE_DOWN: float = AU_SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
SCALE_UP: float = AU / AU_SCALE_FACTOR  # SCALE_FACTOR pixels = 1 AU

FRAME_RATE: int = 60  # there are FRAME_RATE frames per second
CLOCK_FPS: bool = False

SECONDS: int = 1
MINUTES: int = SECONDS * 60
HOURS: int = MINUTES * 60
DAYS: int = HOURS * 24
YEARS: float = DAYS * 365.25

TIMESCALE: int = HOURS * 6  # elapsed time per second, in seconds

AUTO_SAVE_LOAD: bool = True
LIGHTING: bool = True


# Constants for creating blobs somewhat randomly
NUM_BLOBS: int = 51

# number of NUM_BLOBS that are planets
NUM_PLANETS: int = 5

# If true all blobs will start
# with a perfect orbital velocity
START_PERFECT_ORBIT: bool = True

# whether or not to start orbit with a perpendicular push
START_ANGULAR_CHAOS: bool = False

# Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
SQUARE_BLOB_PLOTTER: bool = False

# If true, blobs can escape the bounds of the Universe (thus removing them permanently)
CENTER_BLOB_ESCAPE: bool = True

# whether to wrap objects at edge detection or bounce them, if escape is False
WRAP_IF_NO_ESCAPE: bool = True and not CENTER_BLOB_ESCAPE

# Height and with of display (monitor)
DISPLAY_SIZE_H: int = 1000
DISPLAY_SIZE_W: int = 1000
# Cube size of Universe in pixels
UNIVERSE_SIZE: float = AU_SCALE_FACTOR * UNIVERSE_SCALE

CENTER_BLOB_MASS: float = S_MASS
CENTER_BLOB_RADIUS: float = (AU_SCALE_FACTOR * (S / AU)) * CENTER_BLOB_SCALE
CENTER_BLOB_COLOR: tuple = (255, 210, 63)
CENTER_BLOB_NAME: str = "sun"
CENTER_BLOB_SHADOW_RESOLUTION: int = 8192

MIN_RADIUS: float = (AU_SCALE_FACTOR * (E / AU)) * BLOB_SCALE
MAX_RADIUS: float = (AU_SCALE_FACTOR * (J / AU)) * BLOB_SCALE
BLOB_SHADOW_RESOLUTION: int = 8192

MIN_MOON_RADIUS: float = (AU_SCALE_FACTOR * (ENC / AU)) * BLOB_SCALE
MAX_MOON_RADIUS: float = (AU_SCALE_FACTOR * (GAN / AU)) * BLOB_SCALE

MIN_MASS: float = E_MASS
MAX_MASS: float = J_MASS

MIN_MOON_MASS: float = ENC_MASS
MAX_MOON_MASS: float = GAN_MASS

FIRST_PERSON_SCALE: float = MAX_RADIUS * 2.5
BACKGROUND_SCALE: float = FIRST_PERSON_SCALE * 10000
GRID_CELLS_PER_AU: float = 0.5
GRID_CELL_SIZE: int = int(UNIVERSE_SIZE / (UNIVERSE_SCALE * GRID_CELLS_PER_AU))
GRID_KEY_UPPER_BOUND: int = int(UNIVERSE_SIZE / GRID_CELL_SIZE)
GRID_KEY_CHECK_BOUND: int = GRID_KEY_UPPER_BOUND - 1

COLORS: List[tuple] = [
    (221, 110, 66),  # rgb(221, 110, 66)
    (33, 118, 174),  # rgb(33, 118, 174)
    (51, 115, 87),  # rgb(51, 115, 87)
    (147, 3, 46),  # rgb(147, 3, 46)
    (255, 133, 82),  # rgb(255, 133, 82)
    (255, 81, 84),  # rgb(255, 81, 84)
    (177, 15, 46),  # rgb(177, 15, 46)
    (35, 116, 171),  # rgb(35, 116, 171)
    (179, 0, 27),  # rgb(179, 0, 27)
    (242, 100, 25),  # rgb(242, 100, 25)
    (20, 92, 158),  # rgb(20, 92, 158)
    (255, 125, 0),  # rgb(255, 125, 0)
    # (21, 97, 109),  # rgb(21, 97, 109)
    # (186, 31, 51),  # rgb(186, 31, 51)
    # (145, 23, 31),  # rgb(145, 23, 31)
    # (116, 66, 83),  # rgb(116, 66, 83)
    # (166, 161, 94),  # rgb(166, 161, 94)
    # (78, 56, 34),  # rgb(78, 56, 34)
    # (56, 63, 81),  # rgb(56, 63, 81)
    # (115, 87, 81),  # rgb(115, 87, 81)
    # (140, 28, 19),  # rgb(140, 28, 19)
    # (73, 17, 28),  # rgb(73, 17, 28)
    (186, 90, 49),  # rgb(186, 90, 49)
    # (46, 41, 78),  # rgb(46, 41, 78)
    (41, 115, 115),  # rgb(41, 115, 115)
    # (57, 57, 58),  # rgb(57, 57, 58)
    # (3, 71, 50),  # rgb(3, 71, 50)
    (114, 155, 121),  # rgb(114, 155, 121)
    # (81, 52, 77),  # rgb(81, 52, 77)
    # (44, 66, 63),  # rgb(44, 66, 63)
    # (64, 4, 6),  # rgb(64, 4, 6)
    # (41, 51, 92),  # rgb(41, 51, 92)
    (105, 122, 33),  # rgb(105, 122, 33)
    (109, 26, 54),  # rgb(109, 26, 54)
]
BACKGROUND_COLOR: tuple = (0, 21, 36)  # screen background color
# night black (19, 21, 21)
# jet grey (43, 44, 40)
# rich black (0, 21, 36)
DISPLAY_FONT: str = "newtons_blobs/font/Rushfordclean-rgz89.otf"
WINDOW_ICON: str = "newtons_blobs/img/newton_icon.ico"
WINDOW_TITLE: str = "Newton's Blobs"
STAT_FONT_SIZE: float = 0.24
BLOB_FONT_SIZE: float = 0.16
