"""
Newton's Laws, a simulator of physics at the scale of space

Global contants

by Jason Mott, copyright 2024
"""

from os import path

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.2"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


# Global constants

VERSION = __version__

# No need to ever change these
G = 6.67428e-11  # Gravitational constant
AU = 149.6e6 * 1000  # 1 Astronomical Unit

# Change to scale the size of universe (thus window)
CLOCK_FPS = False
LIGHTING = True
SCALE_PERCENT = 1
AU_SCALE_FACTOR = 500 * SCALE_PERCENT  # Number of pixles to equal 1 AU
TIMESCALE = 3600 * 10 * SCALE_PERCENT  # elapsed time per frame, in seconds
# Height and with of display (monitor)
DISPLAY_SIZE_H = 1000
DISPLAY_SIZE_W = 1000
# Cube size of Universe in pixles
UNIVERSE_SIZE = 2000 * SCALE_PERCENT
UNIVERSE_SIZE_H = UNIVERSE_SIZE
UNIVERSE_SIZE_W = UNIVERSE_SIZE
UNIVERSE_SIZE_D = UNIVERSE_SIZE
MIN_RADIUS = 5 * SCALE_PERCENT
MAX_RADIUS = 25 * SCALE_PERCENT
GRID_CELL_SIZE = MAX_RADIUS * 3
GRID_KEY_UPPER_BOUND = int(UNIVERSE_SIZE / GRID_CELL_SIZE)
GRID_KEY_CHECK_BOUND = GRID_KEY_UPPER_BOUND - 1
SCALE_DOWN = AU_SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
SCALE_UP = AU / AU_SCALE_FACTOR  # SCALE_FACTOR pixels = 1 AU
# Cube size of the universe in real life scale
SCALED_UNIVERSE_SIZE = UNIVERSE_SIZE * SCALE_UP  # Real height and width in AU
FRAME_RATE = 60  # there are FRAME_RATE frames per second

# Constants for creating blobs somewhat randomly
NUM_BLOBS = 150
# If true all blobs will start
# with a perfect orbital velocity
START_PERFECT_ORBIT = True
# Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
SQUARE_BLOB_PLOTTER = False
MIN_VELOCITY = 31.4 * 1000  # Only if START_PERFECT_ORBIT is False
MAX_VELOCITY = 35.783 * 1000  # Only if START_PERFECT_ORBIT is False
MIN_MASS = 7.34767309 * 10**22  # Mass of Moon
# 3.30 * 10**23 * 0.75  # currently set with 75% of mass of Mercury
MAX_MASS = 6.9742 * 10**24  # currently set slightly larger than mass of Earth
CENTER_BLOB_MASS = 1.98892 * 10**30  # currently set with mass of the sun
# 8.54 * 10**36 <-- black hole, don't do it, your machine will colapse into itself!
CENTER_BLOB_RADIUS = 30 * SCALE_PERCENT
CENTER_BLOB_COLOR = (255, 210, 63)
CENTER_BLOB_NAME = "sun"
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
DISPLAY_FONT = path.join(".", "newtons_blobs", "font", "Rushfordclean-rgz89.otf")
WINDOW_ICON = path.join(".", "newtons_blobs", "img", "newton_icon.gif")
STAT_FONT_SIZE = round(24 * SCALE_PERCENT)
BLOB_FONT_SIZE = round(16 * SCALE_PERCENT)


# TODO get this working, keep false for now
wrap = False  # whether to wrap objects at edge detection or bounce them
