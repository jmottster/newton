"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, Protocol

from .blob_universe import BlobUniverse
from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobSurface(Protocol):
    """
    A Protocol class used to represent an object that draws a blob, with a distinction of the center blob

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : Tuple[int, int, int]
        a three value tuple for RGB color value of blob
    universe: BlobUniverse
        The universe instance the blobs will be drawn on
    texture : str = None
        For 3d rendering, this is optional (implement as texture = None in __init__)
    rotation_speed : float = None
        For 3d rendering, the speed (degrees per frame) at which the blob will spin
    rotation_pos : Tuple[int, int, int] = None
        For 3d rendering, the z,y,z angles of orientation of the blob (in degrees)

    Methods
    -------

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

    radius: float
    color: Tuple[int, int, int]
    universe: BlobUniverse
    texture: str = None
    rotation_speed: float = None
    rotation_pos: Tuple[int, int, int] = None

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
        pass

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
        pass
