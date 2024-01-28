"""
Newton's Laws, a simulator of physics at the scale of space

Global contants

by Jason Mott, copyright 2024
"""

import math
from os import path

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


# Global constants

# No need to ever change these
G = 6.67428e-11  # Gravitational constant
AU = 149.6e6 * 1000  # 1 Astronomical Unit

# Change to scale the size of universe (thus window)
SCALE_PERCENT = 1
AU_SCALE_FACTOR = 500 * SCALE_PERCENT  # Number of pixles to equal 1 AU
TIMESCALE = 3600 * 12 * SCALE_PERCENT  # elapsed time per frame, in seconds
# Height and with of display (monitor)
DISPLAY_SIZE_H = 1000
DISPLAY_SIZE_W = 1000
# Height and width of screen (square is best for orbits, can be bigger than display)
SCREEN_SIZE = 2000 * SCALE_PERCENT
SCREEN_SIZE_H = SCREEN_SIZE
SCREEN_SIZE_W = SCREEN_SIZE
SCREEN_SIZE_D = SCREEN_SIZE
MIN_RADIUS = 5 * SCALE_PERCENT
MAX_RADIUS = 20 * SCALE_PERCENT
SCALE = AU_SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
SCALED_SCREEN_SIZE = (SCREEN_SIZE / AU_SCALE_FACTOR) * AU  # Real height and width in AU
FRAME_RATE = 120  # there are FRAME_RATE frames per second

# Constants for creating blobs somewhat randomly
NUM_BLOBS = 100
# If true all blobs will start
# with a perfect orbital velocity
START_PERFECT_ORBIT = True
START_PERFECT_FLOOR_BOUNCE = False
# Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
SQUARE_BLOB_PLOTTER = False
MIN_VELOCITY = 47.4 * 1000  # Only if START_PERFECT_ORBIT is False
MAX_VELOCITY = 50.217 * 300  # 29.783 * 1000 Only if START_PERFECT_ORBIT is False
MIN_MASS = 7.34767309 * 10**22  # Mass of Moon
# 3.30 * 10**23 * 0.75  # currently set with 75% of mass of Mercury
MAX_MASS = 6.9742 * 10**24  # currently set slightly larger than mass of Earth
FLOOR_MASS = 1.98892 * 10**28
CENTER_BLOB_MASS = 1.98892 * 10**30  # currently set with mass of the sun
# 8.54 * 10**36 <-- black hole, don't do it, your machine will colapse into itself!
CENTER_BLOB_RADIUS = 30 * SCALE_PERCENT
CENTER_BLOB_COLOR = (255, 210, 63)
CENTER_BLOB_NAME = "sun"
COLORS = [
    (221, 110, 66),
    (33, 118, 174),
    (51, 115, 87),
    (147, 3, 46),
    (255, 133, 82),
    (157, 195, 194),
    (171, 146, 191),
    (255, 81, 84),
    (177, 15, 46),
    (35, 116, 171),
    (120, 188, 97),
    (179, 0, 27),
    (242, 100, 25),
    (20, 92, 158),
    (255, 125, 0),
    (21, 97, 109),
    (186, 31, 51),
    (145, 23, 31),
    (116, 66, 83),
    (166, 161, 94),
    (194, 151, 184),
]
BACKGROUND_COLOR = (0, 21, 36)  # screen background color
# night black (19, 21, 21)
# jet grey (43, 44, 40)
# rich black (0, 21, 36)
DISPLAY_FONT = path.join("resources", "Rushfordclean-rgz89.otf")
WINDOW_ICON = path.join("resources", "newton_icon.png")
STAT_FONT_SIZE = round(24 * SCALE_PERCENT)
BLOB_FONT_SIZE = round(16 * SCALE_PERCENT)


# TODO get this working, keep false for now
wrap = False  # whether to wrap objects at edge detection or bounce them
