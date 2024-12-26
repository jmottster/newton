"""
Newton's Laws, a simulator of physics at the scale of space

Class to represent an object that holds and controls a drawing area for the universe of blobs

by Jason Mott, copyright 2024
"""

from pathlib import Path
from typing import Any, Tuple, Self

from panda3d.core import BitMask32, Shader, TransparencyAttrib  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs.blob_random import blob_random

from .ursina_fix import PlanetMaterial

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

    fill(color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    clear() -> None
        Used to delete and properly clean up blobs (for a start over, for example)

    """

    size_w: float
    size_h: float
    bit_masks: list = [0b0001, 0b0010, 0b0100, 0b1000, 0b10000, 0b100000]

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

        if texture is None:

            self.texture = "backgrounds/multi_nebulae_2.png"
            if (blob_random.random() * 100) < 50:
                self.texture = "backgrounds/8k_stars_milky_way.jpeg"
            if LOW_VRAM:
                self.texture = "backgrounds/multi_nebulae_2-small.png"
                if (blob_random.random() * 100) < 50:
                    self.texture = "backgrounds/8k_stars_milky_way-small.jpeg"
        else:
            self.texture = texture

        glow_map: str = "glow_maps/background_no_glow_map.png"
        if LOW_VRAM:
            glow_map = "glow_maps/background_no_glow_map-small.png"

        if not bg_vars.textures_3d:
            self.texture = None
            glow_map = None

        self.universe = urs.application.base.loader.loadModel(
            self.base_dir.joinpath("models").joinpath("background_sphere.obj")
        )
        self.universe.reparentTo(urs.scene)
        self.universe.setTransparency(TransparencyAttrib.M_none)
        self.universe.setPos(urs.scene, (0, 0, 0))

        self.universe.setColorScaleOff()
        self.universe.setColorScale((1, 1, 1, 1))
        self.universe.setScale(urs.scene, scale)

        if self.texture is not None:
            self.universe.setTexture(
                PlanetMaterial.texture_stage_glow,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(glow_map)
                ),
            )
            self.universe.setTexture(
                PlanetMaterial.texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.texture)
                ),
            )
            self.universe.setShaderAuto(
                BitMask32.allOn() & ~BitMask32.bit(Shader.bit_AutoShaderShadow)
            )

        self.universe.setLightOff(True)
        for bit in range(0, len(BlobUniverseUrsina.bit_masks)):
            self.universe.hide(BlobUniverseUrsina.bit_masks[bit])

        if self.texture == "backgrounds/8k_stars_milky_way.jpeg":
            self.universe.setHpr((0, 66, 0))
        else:
            self.universe.setHpr((0, 0, 90))

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

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        pass

    def clear(self: Self) -> None:
        """Used to delete and properly clean up blobs (for a start over, for example)"""

        urs.scene.clear()
        self.width, self.height = (
            bg_vars.universe_size_w,
            bg_vars.universe_size_h,
        )
        self.set_universe_entity(bg_vars.background_scale)
