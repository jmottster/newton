"""
Newton's Laws, a simulator of physics at the scale of space

Class to represent an object that holds and controls a drawing area for the universe of blobs

by Jason Mott, copyright 2024
"""

from typing import Any, Tuple, Self

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars
from newtons_blobs import resource_path

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUniverseUrsina:
    """
    Protocol class to represent an object that holds and controls a drawing area for the universe of blobs

    Attributes
    ----------
    size_w: float
        The desired width of the universe in pixels
    size_h: float
        The desired height of the universe in pixels

    Methods
    -------
    get_framework() -> Any
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_width() -> float
        Returns the current width of the universe object

    get_height() -> float
        Returns the current height of the universe object

    get_center_blob_start_pos() -> Tuple[float,float,float]
        Returns a tuple of the center point x,y,z

    fill(color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    clear() -> None
        Used to delete and properly clean up blobs (for a start over, for example)

    """

    size_w: float
    size_h: float

    def __init__(self: Self, size_w: float, size_h: float):

        self.width = size_w
        self.height = size_h

        self.universe = urs.Entity(
            shader=shd.unlit_shader,
            position=(0, 0, 0),
            model="sky_dome",
            scale=BlobGlobalVars.background_scale,
            texture="nb_ursina/textures/space/solar_system_scope/8k_stars_milky_way.jpg",
            texture_scale=(1, 1),
            rotation_x=90,
            eternal=True,
        )

        # urs.scene.scale = urs.Vec3(self.width, self.height, self.height)

    def get_framework(self: Self) -> Any:
        """
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access
        """
        return self.universe

    def get_width(self: Self) -> float:
        """
        Returns the current width of the universe object
        """
        return self.width

    def get_height(self: Self) -> float:
        """
        Returns the current height of the universe object
        """
        return self.height

    def get_center_blob_start_pos(self: Self) -> Tuple[float, float, float]:
        """Returns a tuple of the center point x,y,z"""
        x = self.get_width() * BlobGlobalVars.scale_up
        y = self.get_height() * BlobGlobalVars.scale_up
        z = self.get_height() * BlobGlobalVars.scale_up
        return (x / 2, y / 2, z / 2)

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        pass

    def clear(self: Self) -> None:
        """Used to delete and properly clean up blobs (for a start over, for example)"""
        urs.scene.clear()
