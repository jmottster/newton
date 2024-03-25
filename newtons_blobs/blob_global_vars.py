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
    au_scale_factor: ClassVar[float] - how many pixels are equal to one astronomical unit

    universe_scale: ClassVar[float] - Number of AU to equal universe size

    center_blob_scale: ClassVar[float] - To see more than 1 blob at a time, make blobs this times bigger than real proportion to AU
    blob_scale: ClassVar[float] - Max and min blob sizes, proportional to (normal would be S,
                                  but that makes them quite small, to fix this divide S by something)

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

    start_pos_rotate_x: ClassVar[bool] - whether or not to swap y and z in the starting plot of blobs
    start_pos_rotate_y: ClassVar[bool] - whether or not to swap x and z in the starting plot of blobs
    start_pos_rotate_z: ClassVar[bool] - whether or not to swap x and y in the starting plot of blobs

    timescale: ClassVar[int] - number of seconds to pass with each frame
    true_3d: ClassVar[bool] - whether or not the display engine uses real 3D
    start_perfect_orbit: ClassVar[bool] - whether or not to start with a perfect orbit of blobs
    start_angular_chaos: ClassVar[bool] - whether or not to start orbit with a perpendicular push
    square_blob_plotter: ClassVar[bool] - whether to start blobs in a square formation

    Methods
    -------
    BlobGlobalVars.set_center_blob_scale(center_blob_scale: float) -> None
        Class method to set BlobGlobalVars.center_blob_scale

    BlobGlobalVars.set_universe_scale(universe_scale: float) -> None
        Class method to set BlobGlobalVars.universe_scale

    BlobGlobalVars.set_blob_scale(blob_scale: float) -> None
        Class method to set BlobGlobalVars.blob_scale

    BlobGlobalVars.set_au_scale_factor(au_scale_factor: float) -> None
        Class method to set BlobGlobalVars.au_scale_factor. This also
        resets all variables that are set using BlobGlobalVars.au_scale_factor

    BlobGlobalVars.apply_configure() -> None
        Resets all variables that are calculated based on other variables
        Automatically called after making changes to relevant vars

    BlobGlobalVars.set_start_pos_rotate_x(start_pos_rotate_x: bool) -> None
        Class method to set whether or not to swap y and z in the starting plot of blobs

    BlobGlobalVars.set_start_pos_rotate_y(start_pos_rotate_y: bool) -> None
        Class method to set whether or not to swap x and z in the starting plot of blobs

    BlobGlobalVars.set_start_pos_rotate_z(start_pos_rotate_z: bool) -> None
        Class method to set whether or not to swap x and y in the starting plot of blobs

    BlobGlobalVars.set_true_3d(true_3d: bool) -> None
        Class method to set BlobGlobalVars.true_3d

    BlobGlobalVars.set_timescale(cls, timescale: int) -> None
        Class method to set BlobGlobalVars.timescale

    BlobGlobalVars.set_start_perfect_orbit(start_perfect_orbit: bool) -> None
        Class method to set whether or not to start with a perfect orbit of blobs

    BlobGlobalVars.set_start_angular_chaos(start_angular_chaos: bool) -> None
        Class method to set whether or not to start orbit with a perpendicular push

    BlobGlobalVars.set_square_blob_plotter(square_blob_plotter: bool) -> None
        Class method to set whether to start blobs in a square formation

    """

    au_scale_factor: ClassVar[float] = AU_SCALE_FACTOR

    universe_scale: ClassVar[float] = UNIVERSE_SCALE

    center_blob_scale: ClassVar[float] = CENTER_BLOB_SCALE
    blob_scale: ClassVar[float] = BLOB_SCALE

    # 1 AU = SCALE_FACTOR pixels
    scale_down: ClassVar[float] = SCALE_DOWN

    # SCALE_FACTOR pixels = 1 AU
    scale_up: ClassVar[float] = SCALE_UP

    universe_size: ClassVar[float] = UNIVERSE_SIZE
    universe_size_h: ClassVar[float] = UNIVERSE_SIZE_H
    universe_size_w: ClassVar[float] = UNIVERSE_SIZE_W
    universe_size_d: ClassVar[float] = UNIVERSE_SIZE_D

    center_blob_radius: ClassVar[float] = CENTER_BLOB_RADIUS

    min_radius: ClassVar[float] = MIN_RADIUS
    max_radius: ClassVar[float] = MAX_RADIUS

    first_person_scale: ClassVar[float] = FIRST_PERSON_SCALE
    background_scale: ClassVar[float] = BACKGROUND_SCALE
    grid_cell_size: ClassVar[int] = GRID_CELL_SIZE
    grid_key_upper_bound: ClassVar[int] = GRID_KEY_UPPER_BOUND
    grid_key_check_bound: ClassVar[int] = GRID_KEY_CHECK_BOUND

    start_pos_rotate_x: ClassVar[bool] = START_POS_ROTATE_X
    start_pos_rotate_y: ClassVar[bool] = START_POS_ROTATE_Y
    start_pos_rotate_z: ClassVar[bool] = START_POS_ROTATE_Z

    timescale: ClassVar[int] = TIMESCALE
    true_3d: ClassVar[bool] = TRUE_3D
    start_perfect_orbit: ClassVar[bool] = START_PERFECT_ORBIT
    start_angular_chaos: ClassVar[bool] = START_ANGULAR_CHAOS
    square_blob_plotter: ClassVar[bool] = SQUARE_BLOB_PLOTTER

    @classmethod
    def set_center_blob_scale(cls, center_blob_scale: float) -> None:
        """Class method to set BlobGlobalVars.center_blob_scale"""
        cls.center_blob_scale = center_blob_scale
        cls.apply_configure()

    @classmethod
    def set_universe_scale(cls, universe_scale: float) -> None:
        """Class method to set BlobGlobalVars.universe_scale"""
        cls.universe_scale = universe_scale
        cls.apply_configure()

    @classmethod
    def set_blob_scale(cls, blob_scale: float) -> None:
        """Class method to set BlobGlobalVars.blob_scale"""
        cls.blob_scale = blob_scale
        cls.apply_configure()

    @classmethod
    def set_au_scale_factor(cls, au_scale_factor: float) -> None:
        """
        Class method to set BlobGlobalVars.au_scale_factor.
        """
        cls.au_scale_factor = au_scale_factor
        cls.apply_configure()

    @classmethod
    def apply_configure(cls) -> None:
        """This resets all variables that are calculated based on other variables (use after making changes to vars)"""

        cls.scale_down = cls.au_scale_factor / AU
        cls.scale_up = AU / cls.au_scale_factor

        cls.universe_size = cls.au_scale_factor * cls.universe_scale
        cls.universe_size_h = cls.universe_size
        cls.universe_size_w = cls.universe_size
        cls.universe_size_d = cls.universe_size

        cls.center_blob_radius = (cls.au_scale_factor * cls.center_blob_scale) * (
            S / AU
        )

        cls.min_radius = cls.center_blob_radius * (E / cls.blob_scale)
        cls.max_radius = cls.center_blob_radius * (J / cls.blob_scale)

        cls.first_person_scale = cls.center_blob_radius * 0.1
        cls.background_scale = cls.center_blob_radius * 1000

        cls.grid_cell_size = int(cls.universe_size / (cls.universe_scale * 10))
        cls.grid_key_upper_bound = int(cls.universe_size / cls.grid_cell_size)
        cls.grid_key_check_bound = cls.grid_key_upper_bound - 1

        print(
            f"cls.min_radius={cls.min_radius}  cls.max_radius={cls.max_radius} cls.grid_cell_size={cls.grid_cell_size} cls.grid_key_upper_bound={cls.grid_key_upper_bound}"
        )

    @classmethod
    def set_start_pos_rotate_x(cls, start_pos_rotate_x: bool) -> None:
        """Class method to set whether or not to swap y and z in the starting plot of blobs"""
        cls.start_pos_rotate_x = start_pos_rotate_x

    @classmethod
    def set_start_pos_rotate_y(cls, start_pos_rotate_y: bool) -> None:
        """Class method to set whether or not to swap x and z in the starting plot of blobs"""
        cls.start_pos_rotate_y = start_pos_rotate_y

    @classmethod
    def set_start_pos_rotate_z(cls, start_pos_rotate_z: bool) -> None:
        """Class method to set whether or not to swap x and y in the starting plot of blobs"""
        cls.start_pos_rotate_z = start_pos_rotate_z

    @classmethod
    def set_true_3d(cls, true_3d: bool) -> None:
        """Class method to set BlobGlobalVars.true_3d"""
        cls.true_3d = true_3d

    @classmethod
    def set_timescale(cls, timescale: int) -> None:
        """Class method to set BlobGlobalVars.timescale"""
        cls.timescale = timescale

    @classmethod
    def set_start_perfect_orbit(cls, start_perfect_orbit: bool) -> None:
        """Class method to set whether or not to start with a perfect orbit of blobs"""
        cls.start_perfect_orbit = start_perfect_orbit

    @classmethod
    def set_start_angular_chaos(cls, start_angular_chaos: bool) -> None:
        """Class method to set whether or not to start orbit with a perpendicular push"""
        cls.start_angular_chaos = start_angular_chaos

    @classmethod
    def set_square_blob_plotter(cls, square_blob_plotter: bool) -> None:
        """Class method to set whether to start blobs in a square formation"""
        cls.square_blob_plotter = square_blob_plotter
