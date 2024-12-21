"""
Newton's Laws, a simulator of physics at the scale of space

Global constants

by Jason Mott, copyright 2024
"""

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


# Global constants

VERSION = __version__

# No need to ever change these
G = 6.67428 * 10**-11  # Gravitational constant

# Sizes in Meters
AU = 1.495978707 * 10**11  # 1 Astronomical Unit
S = 6.957 * 10**8  # Radius of the Sun
J = 7.1492 * 10**7  # Radius of Jupiter
E = 6.3781 * 10**6  # Radius of the Earth

# Moons
GAN = 2.6341 * 10**6  # Radius of Ganymede (largest moon in solar system)
M = 1.7381 * 10**6  # Radius of the Moon
MIM = 0.1982 * 10**6  # Radius of Mimas (smallest round moon in solar system)

# Masses in Kilograms
# black hole, don't do it, your machine will collapse into itself!
B_MASS = 8.54 * 10**36  # Mass of Sagittarius A*

S_MASS = 1.98892 * 10**30  # Mass of the Sun
J_MASS = 1.899 * 10**27  # Mass of Jupiter
E_MASS = 5.972 * 10**24  # Mass of Earth

# Moons
GAN_MASS = 1.4819 * 10**23  # Mass of Ganymede (largest moon in solar system)
M_MASS = 7.342 * 10**22  # Mass of the Moon
MIM_MASS = 3.75094 * 10**19  # Mass of Mimas (smallest round moon in solar system)


LOW_VRAM = False
TRUE_3D = True
BLOB_MOON_PERCENT = 0.75  # Percentage of blobs that are moons (if true_3d)
if not TRUE_3D:
    BLOB_MOON_PERCENT = 0
TEXTURES_3D = True
AU_SCALE_FACTOR = 12500  # Number of pixels to equal 1 AU

# Number of AU to equal universe size
UNIVERSE_SCALE = 100

# To see more than 1 blob at a time, make blobs this times bigger than real proportion to AU
CENTER_BLOB_SCALE = 20

BLOB_SCALE = 20

SCALE_DOWN = AU_SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
SCALE_UP = AU / AU_SCALE_FACTOR  # SCALE_FACTOR pixels = 1 AU

FRAME_RATE = 60  # there are FRAME_RATE frames per second
CLOCK_FPS = False

SECONDS = 1
MINUTES = SECONDS * 60
HOURS = MINUTES * 60
DAYS = HOURS * 24
YEARS = DAYS * 365.25

TIMESCALE = HOURS * 6  # elapsed time per second, in seconds

AUTO_SAVE_LOAD = True
LIGHTING = True


# Constants for creating blobs somewhat randomly
NUM_BLOBS = 41

# If true all blobs will start
# with a perfect orbital velocity
START_PERFECT_ORBIT = True

# whether or not to start orbit with a perpendicular push
START_ANGULAR_CHAOS = False

# Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
SQUARE_BLOB_PLOTTER = False

# If true, blobs can escape the bounds of the Universe (thus removing them permanently)
CENTER_BLOB_ESCAPE = True

# whether to wrap objects at edge detection or bounce them, if escape is False
WRAP_IF_NO_ESCAPE = True and not CENTER_BLOB_ESCAPE

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

CENTER_BLOB_MASS = S_MASS
CENTER_BLOB_RADIUS = (AU_SCALE_FACTOR * (S / AU)) * CENTER_BLOB_SCALE
CENTER_BLOB_COLOR = (255, 210, 63)
CENTER_BLOB_NAME = "sun"
CENTER_BLOB_SHADOW_RESOLUTION = 8192

MIN_RADIUS = (AU_SCALE_FACTOR * (E / AU)) * BLOB_SCALE
MAX_RADIUS = (AU_SCALE_FACTOR * (J / AU)) * BLOB_SCALE
BLOB_SHADOW_RESOLUTION = 8192

MIN_MOON_RADIUS = (AU_SCALE_FACTOR * (MIM / AU)) * BLOB_SCALE
MAX_MOON_RADIUS = (AU_SCALE_FACTOR * (GAN / AU)) * BLOB_SCALE

MIN_MASS = E_MASS
MAX_MASS = J_MASS

MIN_MOON_MASS = MIM_MASS
MAX_MOON_MASS = GAN_MASS

FIRST_PERSON_SCALE = MAX_RADIUS * 2.5
BACKGROUND_SCALE = FIRST_PERSON_SCALE * 10000
GRID_CELLS_PER_AU = 0.5
GRID_CELL_SIZE = int(UNIVERSE_SIZE / (UNIVERSE_SCALE * GRID_CELLS_PER_AU))
GRID_KEY_UPPER_BOUND = int(UNIVERSE_SIZE / GRID_CELL_SIZE)
GRID_KEY_CHECK_BOUND = GRID_KEY_UPPER_BOUND - 1

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
BACKGROUND_COLOR = (0, 21, 36)  # screen background color
# night black (19, 21, 21)
# jet grey (43, 44, 40)
# rich black (0, 21, 36)
DISPLAY_FONT = "newtons_blobs/font/Rushfordclean-rgz89.otf"
WINDOW_ICON = "newtons_blobs/img/newton_icon.ico"
WINDOW_TITLE = "Newton's Blobs"
STAT_FONT_SIZE = round(24)
BLOB_FONT_SIZE = round(16)
