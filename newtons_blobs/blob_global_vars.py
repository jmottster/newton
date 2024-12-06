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
    BlobGlobalVars.au_scale_factor: ClassVar[float] - how many pixels are equal to one astronomical unit

    BlobGlobalVars.universe_scale: ClassVar[float] - Number of AU to equal universe size

    BlobGlobalVars.center_blob_scale: ClassVar[float] - To see more than 1 blob at a time, make blobs this times bigger than real proportion to AU
    BlobGlobalVars.scale_center_blob_mass_with_size: ClassVar[bool] - Whether or not to scale the mass in proportion to radius scaling
    BlobGlobalVars.black_hole_mode: ClassVar[bool] - If true, center blob is invisible and mass will not scale


    BlobGlobalVars.blob_scale: ClassVar[float] - Max and min blob sizes, proportional to (normal would be S,
                                  but that makes them quite small, to fix this divide S by something)
    BlobGlobalVars.scale_blob_mass_with_size: ClassVar[bool] - Whether or not to scale the mass in proportion to radius scaling

    BlobGlobalVars.scale_down: ClassVar[float] - multiply real world space distance (in meters) by this to get the pixel value

    BlobGlobalVars.scale_up: ClassVar[float] - multiply pixel value by this to get real world space distance (in meters)

    BlobGlobalVars.universe_size: ClassVar[float] - size of universe in pixels
    BlobGlobalVars.universe_size_h: ClassVar[float] - height of universe in pixels
    BlobGlobalVars.universe_size_w: ClassVar[float] - width of universe in pixels
    BlobGlobalVars.universe_size_d: ClassVar[float] - depth of universe in pixels

    BlobGlobalVars.center_blob_radius: ClassVar[float] - Starting radius (in pixels) of the center blob

    BlobGlobalVars.center_blob_mass: ClassVar[float] -  Starting mass (in kg) of the center blob, subject to change
    BlobGlobalVars.org_center_blob_mass: ClassVar[float] -  Original starting mass (in kg) of the center blob. doesn't change
    BlobGlobalVars.center_blob_shadow_resolution: ClassVar[int] - The resolution for center blob shadow casting
    

    BlobGlobalVars.min_radius: ClassVar[float] - minimum radius (in pixels) that a blob can be
    BlobGlobalVars.max_radius: ClassVar[float] - maximum radius (in pixels) that a blob can be
    BlobGlobalVars.blob_shadow_resolution: ClassVar[int] - The resolution for blob shadow casting (blob's with rings only)
    
    BlobGlobalVars.min_moon_radius: ClassVar[float] - minimum radius (in pixels) that a moon blob can be
    BlobGlobalVars.max_moon_radius: ClassVar[float] - maximum radius (in pixels) that a moon blob can be

    BlobGlobalVars.min_mass: ClassVar[float] - Minimum mass (in kg) of blobs, subject to change
    BlobGlobalVars.max_mass: ClassVar[float] - Maximum mass (in kg) of blobs, subject to change
    BlobGlobalVars.min_moon_mass: ClassVar[float] - Minimum mass (in kg) of moon blobs, subject to change
    BlobGlobalVars.max_moon_mass: ClassVar[float] - Maximum mass (in kg) of moon blobs, subject to change

    BlobGlobalVars.org_min_mass: ClassVar[float] - Original minimum mass (in kg) of blobs, doesn't change
    BlobGlobalVars.org_max_mass: ClassVar[float] - Original maximum mass (in kg) of blobs, doesn't change
    BlobGlobalVars.org_min_moon_mass: ClassVar[float] - Original minimum mass (in kg) of moon blobs, doesn't change
    BlobGlobalVars.org_max_moon_mass: ClassVar[float] - Original maximum mass (in kg) of moon blobs, doesn't change

    BlobGlobalVars.first_person_scale: ClassVar[float] - size (in pixels) that the first person view object is, especially in relation to center_blob_radius
    BlobGlobalVars.background_scale: ClassVar[float] - the distance (in pixels) that the first person viewer can see

    BlobGlobalVars.grid_cells_per_au: ClassVar[float] - the number of cubed grid cells for every AU
    BlobGlobalVars.grid_cell_size: ClassVar[int] - the size (in pixels) the each cell in the proximity grid should be (see BlobPlotter.update_blobs())
    BlobGlobalVars.grid_key_upper_bound: ClassVar[int] - the number of cells in each direction of the 3d proximity grid (see BlobPlotter.update_blobs())
    BlobGlobalVars.grid_key_check_bound: ClassVar[int] - The second to last grid position

    BlobGlobalVars.start_pos_rotate_x: ClassVar[bool] - whether or not to swap y and z in the starting plot of blobs
    BlobGlobalVars.start_pos_rotate_y: ClassVar[bool] - whether or not to swap x and z in the starting plot of blobs
    BlobGlobalVars.start_pos_rotate_z: ClassVar[bool] - whether or not to swap x and y in the starting plot of blobs

    BlobGlobalVars.timescale: ClassVar[int] - number of seconds to pass with each frame
    BlobGlobalVars.orig_timescale: ClassVar[int] - number of seconds to pass with each frame, original value
    BlobGlobalVars.timescale_inc: ClassVar[int] - Amount to increment timescale when controls change it
    BlobGlobalVars.true_3d: ClassVar[bool] - whether or not the display engine uses real 3D
    BlobGlobalVars.blob_moon_percent: ClassVar[float] - Percentage of blobs that are moons (if true_3d)
    BlobGlobalVars.textures_3d: ClassVar[bool] - whether or not blobs have textures applied (or solid colors)
    BlobGlobalVars.start_perfect_orbit: ClassVar[bool] - whether or not to start with a perfect orbit of blobs
    BlobGlobalVars.start_angular_chaos: ClassVar[bool] - whether or not to start orbit with a perpendicular push
    BlobGlobalVars.square_blob_plotter: ClassVar[bool] - whether to start blobs in a square formation
    BlobGlobalVars.center_blob_escape: ClassVar[bool] - whether blobs can escape the center blob or use edge detection
    BlobGlobalVars.wrap_if_no_escape: ClassVar[bool] - whether to wrap around at edges (or bounce) when edge detection is used

    Methods
    -------
    BlobGlobalVars.set_au_scale_factor(au_scale_factor: float) -> None
        Class method to set BlobGlobalVars.au_scale_factor. This also
        resets all variables that are set using BlobGlobalVars.au_scale_factor

    BlobGlobalVars.set_universe_scale(universe_scale: float) -> None
        Class method to set BlobGlobalVars.universe_scale

    BlobGlobalVars.set_center_blob_scale(center_blob_scale: float) -> None
        Class method to set BlobGlobalVars.center_blob_scale

    BlobGlobalVars.set_blob_scale(blob_scale: float) -> None
        Class method to set BlobGlobalVars.blob_scale

    BlobGlobalVars.set_grid_cells_per_au(grid_cells_per_au: float) -> None
        Class method to set BlobGlobalVars.grid_cells_per_au

    BlobGlobalVars.set_center_blob_escape(center_blob_escape: bool) -> None
        Class method to set whether blobs can escape the center blob or use edge detection

    BlobGlobalVars.set_wrap_if_no_escape(wrap_if_no_escape: bool) -> None
        Class method to set whether to wrap around at edges (or bounce) when edge detection is used

    BlobGlobalVars.set_blob_moon_percent(blob_moon_percent: float) -> None
        Class method to set BlobGlobalVars.blob_moon_percent

    BlobGlobalVars.apply_configure() -> None
        Resets all variables that are calculated based on other variables
        Automatically called after making changes to relevant vars

    BlobGlobalVars.print_info() -> None
        Prints info about settings

    BlobGlobalVars.set_scale_center_blob_mass_with_size(scale_center_blob_mass_with_size: bool) -> None
        Class method to set whether or not to scale the mass in proportion to radius scaling

    BlobGlobalVars.set_black_hole_mode(black_hole_mode: bool) -> None
        Class method to set whether or not center blob is invisible and mass will not scale

    BlobGlobalVars.set_center_blob_shadow_resolution(center_blob_shadow_resolution: int) -> None
        Class method to set the shadow resolution for the center blob

    BlobGlobalVars.set_blob_shadow_resolution(blob_shadow_resolution: int) -> None
        Class method to set the shadow resolution for blob's with rings

    BlobGlobalVars.set_scale_blob_mass_with_size(scale_blob_mass_with_size: bool) -> None
        Class method to set whether or not to scale the mass in proportion to radius scaling

    BlobGlobalVars.set_first_person_scale(first_person_scale: float) -> None
        Class method to set the scale of the first person entity

    BlobGlobalVars.set_background_scale(background_scale: float) -> None
        Class method to set the scale of the background entity (which displays the space scene)

    BlobGlobalVars.set_start_pos_rotate_x(start_pos_rotate_x: bool) -> None
        Class method to set whether or not to swap y and z in the starting plot of blobs

    BlobGlobalVars.set_start_pos_rotate_y(start_pos_rotate_y: bool) -> None
        Class method to set whether or not to swap x and z in the starting plot of blobs

    BlobGlobalVars.set_start_pos_rotate_z(start_pos_rotate_z: bool) -> None
        Class method to set whether or not to swap x and y in the starting plot of blobs

    BlobGlobalVars.set_timescale(timescale: int) -> None
        Class method to set BlobGlobalVars.timescale

    BlobGlobalVars.set_orig_timescale(timescale: int) -> None
        Class method to set BlobGlobalVars.orig_timescale

    BlobGlobalVars.set_timescale_inc(timescale_inc: int) -> None
        Class method to set BlobGlobalVars.timescale_inc

    BlobGlobalVars.set_true_3d(true_3d: bool) -> None
        Class method to set BlobGlobalVars.true_3d

    BlobGlobalVars.set_textures_3d(textures_3d: bool) -> None
        Class method to set BlobGlobalVars.textures_3d

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
    scale_center_blob_mass_with_size: ClassVar[bool] = True
    black_hole_mode: ClassVar[bool] = False

    blob_scale: ClassVar[float] = BLOB_SCALE
    scale_blob_mass_with_size: ClassVar[bool] = True

    # 1 AU = SCALE_FACTOR pixels
    scale_down: ClassVar[float] = SCALE_DOWN

    # SCALE_FACTOR pixels = 1 AU
    scale_up: ClassVar[float] = SCALE_UP

    universe_size: ClassVar[float] = UNIVERSE_SIZE
    universe_size_h: ClassVar[float] = UNIVERSE_SIZE_H
    universe_size_w: ClassVar[float] = UNIVERSE_SIZE_W
    universe_size_d: ClassVar[float] = UNIVERSE_SIZE_D

    center_blob_radius: ClassVar[float] = CENTER_BLOB_RADIUS

    center_blob_mass: ClassVar[float] = CENTER_BLOB_MASS
    org_center_blob_mass: ClassVar[float] = center_blob_mass
    center_blob_shadow_resolution: ClassVar[int] = CENTER_BBLOB_SHADOW_RESOLUTION

    min_radius: ClassVar[float] = MIN_RADIUS
    max_radius: ClassVar[float] = MAX_RADIUS
    blob_shadow_resolution: ClassVar[int] = BLOB_SHADOW_RESOLUTION

    min_moon_radius: ClassVar[float] = MIN_MOON_RADIUS
    max_moon_radius: ClassVar[float] = MAX_MOON_RADIUS

    min_mass: ClassVar[float] = MIN_MASS
    max_mass: ClassVar[float] = MAX_MASS
    min_moon_mass: ClassVar[float] = MIN_MOON_MASS
    max_moon_mass: ClassVar[float] = MAX_MOON_MASS

    org_min_mass: ClassVar[float] = min_mass
    org_max_mass: ClassVar[float] = max_mass
    org_min_moon_mass: ClassVar[float] = min_moon_mass
    org_max_moon_mass: ClassVar[float] = max_moon_mass

    first_person_scale: ClassVar[float] = FIRST_PERSON_SCALE
    background_scale: ClassVar[float] = BACKGROUND_SCALE

    grid_cells_per_au: ClassVar[float] = GRID_CELLS_PER_AU
    grid_cell_size: ClassVar[int] = GRID_CELL_SIZE
    grid_key_upper_bound: ClassVar[int] = GRID_KEY_UPPER_BOUND
    grid_key_check_bound: ClassVar[int] = GRID_KEY_CHECK_BOUND

    start_pos_rotate_x: ClassVar[bool] = START_POS_ROTATE_X
    start_pos_rotate_y: ClassVar[bool] = START_POS_ROTATE_Y
    start_pos_rotate_z: ClassVar[bool] = START_POS_ROTATE_Z

    timescale: ClassVar[int] = TIMESCALE
    orig_timescale: ClassVar[int] = TIMESCALE
    timescale_inc: ClassVar[int] = MINUTES
    true_3d: ClassVar[bool] = TRUE_3D
    blob_moon_percent: ClassVar[float] = BLOB_MOON_PERCENT
    textures_3d: ClassVar[bool] = TEXTURES_3D
    start_perfect_orbit: ClassVar[bool] = START_PERFECT_ORBIT
    start_angular_chaos: ClassVar[bool] = START_ANGULAR_CHAOS
    square_blob_plotter: ClassVar[bool] = SQUARE_BLOB_PLOTTER
    center_blob_escape: ClassVar[bool] = CENTER_BLOB_ESCAPE
    wrap_if_no_escape: ClassVar[bool] = WRAP_IF_NO_ESCAPE

    @classmethod
    def set_au_scale_factor(cls, au_scale_factor: float) -> None:
        """
        Class method to set BlobGlobalVars.au_scale_factor.
        """
        cls.au_scale_factor = au_scale_factor
        cls.apply_configure()

    @classmethod
    def set_universe_scale(cls, universe_scale: float) -> None:
        """Class method to set BlobGlobalVars.universe_scale"""
        cls.universe_scale = universe_scale
        cls.apply_configure()

    @classmethod
    def set_center_blob_scale(cls, center_blob_scale: float) -> None:
        """Class method to set BlobGlobalVars.center_blob_scale"""
        cls.center_blob_scale = center_blob_scale
        cls.apply_configure()

    @classmethod
    def set_blob_scale(cls, blob_scale: float) -> None:
        """Class method to set BlobGlobalVars.blob_scale"""
        cls.blob_scale = blob_scale
        cls.apply_configure()

    @classmethod
    def set_grid_cells_per_au(cls, grid_cells_per_au: float) -> None:
        """
        Class method to set BlobGlobalVars.grid_cells_per_au.
        """
        cls.grid_cells_per_au = grid_cells_per_au
        cls.apply_configure()

    @classmethod
    def set_center_blob_escape(cls, center_blob_escape: bool) -> None:
        """Class method to set whether blobs can escape the center blob or use edge detection"""
        cls.center_blob_escape = center_blob_escape
        cls.apply_configure()

    @classmethod
    def set_wrap_if_no_escape(cls, wrap_if_no_escape: bool) -> None:
        """Class method to set whether to wrap around at edges (or bounce) when edge detection is used"""
        cls.wrap_if_no_escape = wrap_if_no_escape
        cls.apply_configure()

    @classmethod
    def set_blob_moon_percent(cls, blob_moon_percent: float) -> None:
        """Class method to set BlobGlobalVars.blob_moon_percent"""
        cls.blob_moon_percent = blob_moon_percent
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

        cls.center_blob_radius = (
            cls.au_scale_factor * (S / AU)
        ) * cls.center_blob_scale

        if cls.scale_center_blob_mass_with_size and not cls.black_hole_mode:
            cls.center_blob_mass = cls.org_center_blob_mass * cls.center_blob_scale

        cls.min_radius = (cls.au_scale_factor * (E / AU)) * cls.blob_scale
        cls.max_radius = (cls.au_scale_factor * (J / AU)) * cls.blob_scale

        cls.min_moon_radius = (cls.au_scale_factor * (MIM / AU)) * cls.blob_scale
        cls.max_moon_radius = (cls.au_scale_factor * (GAN / AU)) * cls.blob_scale

        if cls.scale_blob_mass_with_size:
            cls.min_mass = cls.org_min_mass * cls.blob_scale
            cls.max_mass = cls.org_max_mass * cls.blob_scale
            cls.min_moon_mass = cls.org_min_moon_mass * cls.blob_scale
            cls.max_moon_mass = cls.org_max_moon_mass * cls.blob_scale

        cls.grid_cell_size = int(
            cls.universe_size / (cls.universe_scale * cls.grid_cells_per_au)
        )
        cls.grid_key_upper_bound = int(cls.universe_size / cls.grid_cell_size)
        cls.grid_key_check_bound = cls.grid_key_upper_bound - 1

        cls.wrap_if_no_escape = cls.wrap_if_no_escape and not cls.center_blob_escape

        if not cls.true_3d:
            cls.blob_moon_percent = 0

    @classmethod
    def print_info(cls) -> None:
        """Prints info about settings"""
        print(
            f"cls.min_mass={cls.min_mass}  cls.max_mass={cls.max_mass} cls.min_radius={round(cls.min_radius,2)}  cls.max_radius={round(cls.max_radius,2)}"
        )

        print(
            f"cls.min_moon_mass={cls.min_moon_mass}  cls.max_moon_mass={cls.max_moon_mass} cls.min_moon_radius={round(cls.min_moon_radius,2)}  cls.max_moon_radius={round(cls.max_moon_radius,2)}"
        )

        print(
            f"cls.universe_size={cls.universe_size}  cls.grid_cell_size={cls.grid_cell_size} cls.grid_key_upper_bound={cls.grid_key_upper_bound}"
        )

    @classmethod
    def set_scale_center_blob_mass_with_size(
        cls, scale_center_blob_mass_with_size: bool
    ) -> None:
        """Class method to set whether or not to scale the mass in proportion to radius scaling"""
        cls.scale_center_blob_mass_with_size = scale_center_blob_mass_with_size

    @classmethod
    def set_black_hole_mode(cls, black_hole_mode: bool) -> None:
        """Class method to set whether or not center blob is invisible and mass will not scale"""
        cls.black_hole_mode = black_hole_mode

    @classmethod
    def set_scale_blob_mass_with_size(cls, scale_blob_mass_with_size: bool) -> None:
        """Class method to set whether or not to scale the mass in proportion to radius scaling"""
        cls.scale_blob_mass_with_size = scale_blob_mass_with_size

    @classmethod
    def set_center_blob_shadow_resolution(cls, center_blob_shadow_resolution: int) -> None:
        """ Class method to set the shadow resolution for the center blob """
        cls.center_blob_shadow_resolution = center_blob_shadow_resolution

    @classmethod
    def set_blob_shadow_resolution(cls, blob_shadow_resolution: int) -> None:
        """ Class method to set the shadow resolution for blob's with rings """
        cls.blob_shadow_resolution = blob_shadow_resolution

    @classmethod
    def set_first_person_scale(cls, first_person_scale: float) -> None:
        """Class method to set the scale of the first person entity"""
        cls.first_person_scale = first_person_scale

    @classmethod
    def set_background_scale(cls, background_scale: float) -> None:
        """Class method to set the scale of the background entity (which displays the space scene)"""
        cls.background_scale = background_scale

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
    def set_timescale(cls, timescale: int) -> None:
        """Class method to set BlobGlobalVars.timescale"""
        cls.timescale = timescale

    @classmethod
    def set_orig_timescale(cls, orig_timescale: int) -> None:
        """Class method to set BlobGlobalVars.orig_timescale"""
        cls.orig_timescale = orig_timescale

    @classmethod
    def set_timescale_inc(cls, timescale_inc: int) -> None:
        """Class method to set BlobGlobalVars.timescale_inc"""
        cls.timescale_inc = timescale_inc

    @classmethod
    def set_true_3d(cls, true_3d: bool) -> None:
        """Class method to set BlobGlobalVars.true_3d"""
        cls.true_3d = true_3d

    @classmethod
    def set_textures_3d(cls, textures_3d: bool) -> None:
        """Class method to set BlobGlobalVars.textures_3d"""
        cls.textures_3d = textures_3d

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
