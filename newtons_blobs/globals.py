"""
Newton's Laws, a simulator of physics at the scale of space

Global constants

by Jason Mott, copyright 2024
"""

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.5"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


# Global constants

VERSION = __version__

# No need to ever change these
G = 6.67428e-11  # Gravitational constant
AU = 1.495978707 * 10**11  # 149.6e6 * 1000   1 Astronomical Unit
S = 6.96 * 10**8
J = 7.1492 * 10**7
E = 6.3781 * 10**6

TRUE_3D = True
AU_SCALE_FACTOR = 12500  # Number of pixels to equal 1 AU

# Number of AU to equal universe size
UNIVERSE_SCALE = 4

# To see more than 1 blob at a time, make blobs this times bigger than real proportion to AU
CENTER_BLOB_SCALE = 10

# Max and min blob sizes, proportional to (normal would be S,
# but that makes them quite small, to fix this divide S by something)
BLOB_SCALE = S / 6

SCALE_DOWN = AU_SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
SCALE_UP = AU / AU_SCALE_FACTOR  # SCALE_FACTOR pixels = 1 AU

FRAME_RATE = 60  # there are FRAME_RATE frames per second
CLOCK_FPS = False

SECONDS = 1
MINUTES = SECONDS * 60
HOURS = MINUTES * 60
DAYS = HOURS * 24
YEARS = DAYS * 365.25

TIMESCALE = HOURS * 5  # elapsed time per frame, in seconds

AUTO_SAVE_LOAD = True
LIGHTING = True


# Constants for creating blobs somewhat randomly
NUM_BLOBS = 102

# If true all blobs will start
# with a perfect orbital velocity
START_PERFECT_ORBIT = True
# Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
SQUARE_BLOB_PLOTTER = False

START_POS_ROTATE_X = False
START_POS_ROTATE_Y = False
START_POS_ROTATE_Z = False

# Height and with of display (monitor)
DISPLAY_SIZE_H = 1000
DISPLAY_SIZE_W = 1000
# Cube size of Universe in pixels
UNIVERSE_SIZE = AU_SCALE_FACTOR * UNIVERSE_SCALE
UNIVERSE_SIZE_H = UNIVERSE_SIZE
UNIVERSE_SIZE_W = UNIVERSE_SIZE
UNIVERSE_SIZE_D = UNIVERSE_SIZE

CENTER_BLOB_MASS = 1.98892 * 10**30  # currently set with mass of the sun
# 8.54 * 10**36 <-- black hole, don't do it, your machine will collapse into itself!
CENTER_BLOB_RADIUS = (AU_SCALE_FACTOR * CENTER_BLOB_SCALE) * (S / AU)
CENTER_BLOB_COLOR = (255, 210, 63)
CENTER_BLOB_NAME = "sun"

MIN_RADIUS = CENTER_BLOB_RADIUS * (E / BLOB_SCALE)
MAX_RADIUS = CENTER_BLOB_RADIUS * (J / BLOB_SCALE)
MIN_MASS = 5.972 * 10**24  # Mass of Earth
MAX_MASS = 1.899 * 10**27  # mass of Jupiter

FIRST_PERSON_SCALE = CENTER_BLOB_RADIUS * 0.1
BACKGROUND_SCALE = CENTER_BLOB_RADIUS * 1000
GRID_CELL_SIZE = int(UNIVERSE_SIZE / (UNIVERSE_SCALE * 10))
GRID_KEY_UPPER_BOUND = int(UNIVERSE_SIZE / GRID_CELL_SIZE)
GRID_KEY_CHECK_BOUND = GRID_KEY_UPPER_BOUND - 1

print(
    f"MIN_RADIUS={MIN_RADIUS}  MAX_RADIUS={MAX_RADIUS} GRID_CELL_SIZE={GRID_CELL_SIZE} GRID_KEY_UPPER_BOUND={GRID_KEY_UPPER_BOUND}"
)

COLORS = [
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
    (21, 97, 109),  # rgb(21, 97, 109)
    (186, 31, 51),  # rgb(186, 31, 51)
    (145, 23, 31),  # rgb(145, 23, 31)
    (116, 66, 83),  # rgb(116, 66, 83)
    (166, 161, 94),  # rgb(166, 161, 94)
    (78, 56, 34),  # rgb(78, 56, 34)
    (56, 63, 81),  # rgb(56, 63, 81)
    (115, 87, 81),  # rgb(115, 87, 81)
    (140, 28, 19),  # rgb(140, 28, 19)
    (73, 17, 28),  # rgb(73, 17, 28)
    (186, 90, 49),  # rgb(186, 90, 49)
    (46, 41, 78),  # rgb(46, 41, 78)
    (41, 115, 115),  # rgb(41, 115, 115)
    (57, 57, 58),  # rgb(57, 57, 58)
    (3, 71, 50),  # rgb(3, 71, 50)
    (114, 155, 121),  # rgb(114, 155, 121)
    (81, 52, 77),  # rgb(81, 52, 77)
    (44, 66, 63),  # rgb(44, 66, 63)
    (64, 4, 6),  # rgb(64, 4, 6)
    (41, 51, 92),  # rgb(41, 51, 92)
    (105, 122, 33),  # rgb(105, 122, 33)
    (109, 26, 54),  # rgb(109, 26, 54)
]
BACKGROUND_COLOR = (0, 21, 36)  # screen background color
# night black (19, 21, 21)
# jet grey (43, 44, 40)
# rich black (0, 21, 36)
DISPLAY_FONT = "newtons_blobs/font/Rushfordclean-rgz89.otf"
WINDOW_ICON = "newtons_blobs/img/newton_icon.ico"
WINDOW_TITLE = "Newton's Blobs"
STAT_FONT_SIZE = round(24)
BLOB_FONT_SIZE = round(16)


# TODO get this working, keep false for now
wrap = False  # whether to wrap objects at edge detection or bounce them
