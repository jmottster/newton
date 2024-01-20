"""
Newton's Laws, a simulator of physics at the scale of space

Global variables

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


# Global vars
G = 6.67428e-11  # Gravitational constant
AU = 149.6e6 * 1000  # 1 Astronomical Unit
SCALE_FACTOR = 500  # Number of pixles to equal 1 AU
SCALE = SCALE_FACTOR / AU  # 1 AU = SCALE_FACTOR pixels
FRAME_RATE = 60  # there are FRAME_RATE frames per second
TIMESCALE = 3600 * 12  # elapsed time per frame, in seconds
SCREEN_SIZE = 1000  # Height and width of screen (square is best for orbits)
SCALED_SCREEN_SIZE = (SCREEN_SIZE / SCALE_FACTOR) * AU  # Real height and width in AU
BACKGROUND_COLOR = (0, 21, 36)  # screen background color
# night black (19, 21, 21)
# jet grey (43, 44, 40)
# rich black (0, 21, 36)
DISPLAY_FONT = path.join("resources", "Rushfordclean-rgz89.otf")
WINDOW_ICON = path.join("resources", "newton_icon.png")

# Vars for creating blobs somewhat randomly
NUM_BLOBS = 100
MIN_RADIUS = 5
MAX_RADIUS = 15
START_PERFECT_ORBIT = True  # If true all blobs will start
# with a perfect orbital velocity
SQUARE_BLOB_PLOTTER = False  # Plot blobs in a square grid to start
# (more chaos to start), otherwise a perfect circular grid (less chaos to start) will be used
MIN_VELOCITY = 25.783 * 500  # Only if START_PERFECT_ORBIT is False
MAX_VELOCITY = 29.783 * 500  # Only if START_PERFECT_ORBIT is False
MIN_MASS = 3.30 * 10**23 * 0.75  # currently set with 75% of mass of Mercury
MAX_MASS = 5.9742 * 10**24  # currently set with mass of Earth
CENTER_BLOB_MASS = 1.98892 * 10**30  # currently set with mass of the sun
CENTER_BLOB_RADIUS = 30
CENTER_BLOB_COLOR = (255, 210, 63)
CENTER_BLOB_NAME = "sun"

COLORS = [
    (221, 110, 66),
    (33, 118, 174),
    (51, 115, 87),
    (147, 3, 46),
    (255, 133, 82),
    (230, 230, 230),
    (157, 195, 194),
    (171, 146, 191),
    (255, 81, 84),
    (59, 244, 251),
    (202, 255, 138),
    (177, 15, 46),
    (35, 116, 171),
    (120, 188, 97),
    (179, 0, 27),
    (255, 196, 235),
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


# TODO get this working, keep false for now
wrap = False  # whether to wrap objects at edge detection or bounce them
