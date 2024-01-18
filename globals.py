"""
Newton's Laws, a simulator of physics at the scale of space

Global variables

by Jason Mott, copyright 2024
"""

import math

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
TIMESCALE = 3600 * 24  # elapsed time per frame, in seconds
SCREEN_SIZE = 1000  # Height and width of screen (square is best for orbits)
SCALED_SCREEN_SIZE = (SCREEN_SIZE / SCALE_FACTOR) * AU  # Real height and width in AU
BACKGROUND_COLOR = (0, 0, 0)  # screen background color

# Vars for creating blobs somewhat randomly
NUM_BLOBS = 90
MIN_RADIUS = 5
MAX_RADIUS = 10
MIN_VELOCITY = 24.783 * 600
MAX_VELOCITY = 28.783 * 600
MIN_MASS = 3.30 * 10**23  # currently set with mass of Mercury
MAX_MASS = 5.9742 * 10**24  # currently set with mass of Earth
CENTER_BLOB_MASS = 2.98892 * 10**29
COLORS = [(155, 155, 255), (155, 255, 155), (255, 155, 155)]


# TODO get this working, keep false for now
wrap = False  # whether to wrap objects at edge detection or bounce them
