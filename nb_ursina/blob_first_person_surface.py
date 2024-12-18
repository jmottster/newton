"""
Newton's Laws, a simulator of physics at the scale of space

A class used to represent an object that draws the first person view Entity

by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, cast

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs import BlobUniverse

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_first_person_ursina import BlobFirstPersonUrsina

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class FirstPersonSurface:
    """

    A class used to represent an object that draws the first person view Entity

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : Tuple[int, int, int]
        a three value tuple for RGB color value of blob
    universe : BlobUniverse
        object representing the universe space to draw blobs onto
    texture : str = None
        Not used, this is a 2d implementation
    rotation_speed : float = None
        Not used, this is a 2d implementation
    rotation_pos : Tuple[float, float, float] = None
        Not used, this is a 2d implementation

    Methods
    -------

    get_position() -> urs.Vec3
        returns the x,y,z position of this blob

    resize(radius: float) -> None
        Sets a new radius for this blob

    update_center_blob(x: float, y: float, z: float) -> None
        Update the x,y,z of the center blob (for lighting effects, etc.,
        all blobs are informed where the center blob is)

    draw(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects

    draw_as_center_blob(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect

    destroy() -> None
        Call to get rid of this instance, so it can clean up
    """

    def __init__(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[float, float, float] = None,
    ):
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.first_person_viewer: BlobFirstPersonUrsina = BlobFirstPersonUrsina(
            name="first_person_viewer",
            scale=bg_vars.first_person_scale,
            universe=self.universe,
            start_y=radius,
            eternal=True,
            mass=bg_vars.min_mass,
            unlit=True,
            shader=shd.unlit_shader,
        )
        self.radius = radius
        self.color = color

    def get_position(self: Self) -> urs.Vec3:
        """returns the x,y,z position of this blob"""
        return self.first_person_viewer.position

    def resize(self: Self, radius: float) -> None:
        """Sets a new radius for this blob"""
        pass

    def update_center_blob(self: Self, x: float, y: float, z: float) -> None:
        """
        Update the x,y,z of the center blob (for lighting effects, etc.,
        all blobs are informed where the center blob is)
        """
        pass

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects
        """
        self.first_person_viewer.position = urs.Vec3(pos)

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect
        """
        pass

    def destroy(self: Self) -> None:
        """Call to get rid of this instance, so it can clean up"""
        if self.first_person_viewer is not None:
            self.first_person_viewer.enabled = False
