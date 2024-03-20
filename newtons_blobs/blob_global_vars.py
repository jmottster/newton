"""
Newton's Laws, a simulator of physics at the scale of space

Global variable class -- use this for changing global values

by Jason Mott, copyright 2024
"""

from typing import ClassVar
from .globals import *


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobGlobalVars:
    """
    Global variable static class -- use this for changing global values

    Attributes
    ----------
    timescale: ClassVar[int] - number of seconds to pass with each frame
    true_3d: ClassVar[bool] - whether or not the display engine uses real 3D
    au_scale_factor: ClassVar[float] - how many pixels are equal to one astronomical unit

    scale_down: ClassVar[float] - multiply real world space distance (in meters) by this to get the pixel value

    scale_up: ClassVar[float] - multiply pixel value by this to get real world space distance (in meters)

    universe_size: ClassVar[float] - size of universe in pixels
    universe_size_h: ClassVar[float] - height of universe in pixels
    universe_size_w: ClassVar[float] - width of universe in pixels
    universe_size_d: ClassVar[float] - depth of universe in pixels

    scaled_universe_size: ClassVar[float] - size of universe in meters (universe_size * scale_up)

    center_blob_radius: ClassVar[float] - radius (in pixels) of the center blob

    min_radius: ClassVar[float] - minimum radius (in pixels) that a blob can be
    max_radius: ClassVar[float] - maximum radius (in pixels) that a blob can be

    first_person_scale: ClassVar[float] - size (in pixels) that the first person view object is, especially in relation to center_blob_radius
    background_scale: ClassVar[float] - the distance (in pixels) that the first person viewer can see
    grid_cell_size: ClassVar[int] - the size (in pixels) the each cell in the proximity grid should be (see BlobPlotter.update_blobs())
    grid_key_upper_bound: ClassVar[int] - the number of cells in each direction of the 3d proximity grid (see BlobPlotter.update_blobs())
    grid_key_check_bound: ClassVar[int] - The second to last grid position

    Methods
    -------
    BlobGlobalVars.set_true_3d(true_3d: bool) -> None
        Class method to set BlobGlobalVars.true_3d

    BlobGlobalVars.set_au_scale_factor(au_scale_factor: float) -> None
        Class method to set BlobGlobalVars.au_scale_factor. This also
        resets all variables that are set using BlobGlobalVars.au_scale_factor

    """

    timescale: ClassVar[int] = TIMESCALE
    true_3d: ClassVar[bool] = TRUE_3D
    au_scale_factor: ClassVar[float] = AU_SCALE_FACTOR

    # 1 AU = SCALE_FACTOR pixels
    scale_down: ClassVar[float] = SCALE_DOWN

    # SCALE_FACTOR pixels = 1 AU
    scale_up: ClassVar[float] = SCALE_UP

    universe_size: ClassVar[float] = UNIVERSE_SIZE
    universe_size_h: ClassVar[float] = UNIVERSE_SIZE_H
    universe_size_w: ClassVar[float] = UNIVERSE_SIZE_W
    universe_size_d: ClassVar[float] = UNIVERSE_SIZE_D

    scaled_universe_size: ClassVar[float] = SCALED_UNIVERSE_SIZE

    center_blob_radius: ClassVar[float] = CENTER_BLOB_RADIUS

    min_radius: ClassVar[float] = MIN_RADIUS
    max_radius: ClassVar[float] = MAX_RADIUS

    first_person_scale: ClassVar[float] = FIRST_PERSON_SCALE
    background_scale: ClassVar[float] = BACKGROUND_SCALE
    grid_cell_size: ClassVar[int] = GRID_CELL_SIZE
    grid_key_upper_bound: ClassVar[int] = GRID_KEY_UPPER_BOUND
    grid_key_check_bound: ClassVar[int] = GRID_KEY_CHECK_BOUND

    @classmethod
    def set_true_3d(cls, true_3d: bool) -> None:
        """Class method to set BlobGlobalVars.true_3d"""
        cls.true_3d = true_3d

    @classmethod
    def set_au_scale_factor(cls, au_scale_factor: float) -> None:
        """
        Class method to set BlobGlobalVars.au_scale_factor. This also
        resets all variables that are set using BlobGlobalVars.au_scale_factor
        """
        cls.au_scale_factor = au_scale_factor

        cls.scale_down = cls.au_scale_factor / AU
        cls.scale_up = AU / cls.au_scale_factor

        cls.universe_size = cls.au_scale_factor * 3
        cls.universe_size_h = cls.universe_size
        cls.universe_size_w = cls.universe_size
        cls.universe_size_d = cls.universe_size

        cls.scaled_universe_size = cls.universe_size * cls.scale_up

        cls.center_blob_radius = (cls.au_scale_factor * 20) * (S / AU)

        cls.min_radius = cls.center_blob_radius * (E / S)
        cls.max_radius = cls.center_blob_radius * (J / S)

        cls.first_person_scale = cls.center_blob_radius * 0.1
        cls.background_scale = cls.center_blob_radius * 1000

        cls.grid_cell_size = int(cls.universe_size / 10)
        cls.grid_key_upper_bound = int(cls.universe_size / cls.grid_cell_size)
        cls.grid_key_check_bound = cls.grid_key_upper_bound - 1

        print(f"cls.min_radius={cls.min_radius}  cls.max_radius={cls.max_radius}")
