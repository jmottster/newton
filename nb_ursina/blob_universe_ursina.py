"""
Newton's Laws, a simulator of physics at the scale of space

Class to represent an object that holds and controls a drawing area for the universe of blobs

by Jason Mott, copyright 2025
"""

from pathlib import Path
from typing import Any, Tuple, Self

from panda3d.core import BitMask32, Shader, TransparencyAttrib  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs.blob_random import blob_random

from .blob_textures import (
    BLOB_BACKGROUND_LARGE,
    BLOB_BACKGROUND_SMALL,
    BLOB_BACKGROUND_ROTATION,
)

from .ursina_fix import PlanetMaterial

from .blob_utils_ursina import MathFunctions as mf, LightUtils as lu

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
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
    set_universe_entity(scale: float) -> None
        Creates the Entity that renders the dome of the background image (stars)

    get_framework() -> Any
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_width() -> float
        Returns the current width of the universe object

    get_height() -> float
        Returns the current height of the universe object

    get_center_blob_start_pos() -> Tuple[float,float,float]
        Returns a tuple of the center point x,y,z

    get_center_offset(x: float, y: float, z: float) -> Tuple[float, float, float]
        Returns a tuple of offset values from center to given x,y,z

    clear() -> None
        Used to delete and properly clean up blobs (for a start over, for example)

    """

    size_w: float
    size_h: float

    def __init__(self: Self, size_w: float, size_h: float):

        self.width = size_w
        self.height = size_h

        self.universe: urs.Entity = None
        self.base_dir: Path = urs.application.asset_folder
        self.texture: str = None
        self.set_universe_entity(bg_vars.background_scale)

    def set_universe_entity(self: Self, scale: float, texture: str = None) -> None:
        """Creates the Entity that renders the dome of the background image (stars)"""

        if self.universe is not None:
            self.universe.removeNode()
            self.universe = None

        texture_index: int = None

        if texture is None:
            texture_index = blob_random.randint(0, len(BLOB_BACKGROUND_LARGE) - 1)
            # texture_index = 1
            if LOW_VRAM:
                self.texture = BLOB_BACKGROUND_SMALL[texture_index]
            else:
                self.texture = BLOB_BACKGROUND_LARGE[texture_index]

        else:
            self.texture = texture

            try:
                if LOW_VRAM:
                    texture_index = BLOB_BACKGROUND_SMALL.index(texture)
                else:
                    texture_index = BLOB_BACKGROUND_LARGE.index(texture)
            except:
                texture_index = None

        if not bg_vars.textures_3d:
            self.texture = None

        self.universe = urs.application.base.loader.loadModel(
            self.base_dir.joinpath("models").joinpath("background_sphere.obj")
        )

        self.universe.reparentTo(urs.scene)
        self.universe.setTransparency(TransparencyAttrib.M_none)
        self.universe.setPos(urs.scene, (0, 0, 0))

        self.universe.setColorScaleOff()
        self.universe.setColorScale((1, 1, 1, 1))
        self.universe.setColor((0.65, 0.65, 0.65, 1))
        self.universe.setScale(urs.scene, scale)

        if self.texture is not None:
            self.universe.setTexture(
                PlanetMaterial.texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.texture)
                ),
            )

        self.universe.setLightOff()
        for bit in range(0, len(lu.bit_masks)):
            self.universe.hide(lu.bit_masks[bit])

        if texture_index is not None:
            self.universe.setHpr(BLOB_BACKGROUND_ROTATION[texture_index])

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
        x = self.get_width() * bg_vars.scale_up
        y = self.get_height() * bg_vars.scale_up
        z = self.get_height() * bg_vars.scale_up
        return (x / 2, y / 2, z / 2)

    def get_center_offset(
        self: Self, x: float, y: float, z: float
    ) -> Tuple[float, float, float]:
        """Returns a tuple of offset values from center to given x,y,z"""
        center_x, center_y, center_z = self.get_center_blob_start_pos()

        return (center_x - x, center_y - y, center_z - z)

    def clear(self: Self) -> None:
        """Used to delete and properly clean up blobs (for a start over, for example)"""

        urs.scene.clear()
        self.width, self.height = (
            bg_vars.universe_size_w,
            bg_vars.universe_size_h,
        )
        self.set_universe_entity(bg_vars.background_scale)
