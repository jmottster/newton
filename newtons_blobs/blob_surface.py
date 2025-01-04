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
    index: int
        An order number in a group of blobs
    name: str
        A name for the instance
    radius : float
        the size of the blob, by radius value
    mass : float
        the mass of the blob, in kg
    color : Tuple[int, int, int]
        a three value tuple for RGB color value of blob
    universe: BlobUniverse
        The universe instance the blobs will be drawn on
    texture : str = None
        For 3d rendering, this is optional (implement as texture = None in __init__)
    ring_texture : str = None
        For 3d rendering, this is optional (implement as ring_texture = None in __init__)
    ring_scale : float = None
        Scale of ring relative to blob scale for gas blobs with rings, optional
    rotation_speed : float = None
        For 3d rendering, the speed (degrees per frame) at which the blob will spin
    rotation_pos : Tuple[int, int, int] = None
        For 3d rendering, the z,y,z angles of orientation of the blob (in degrees)
    position : Tuple[float,float,float] = (0,0,0)
        The x,y,z position for this blob
    barycenter_index : int
        The index of the blob that this blob orbits (used for moon blobs)

    Methods
    -------
    set_barycenter(blob: "BlobSurface") -> None:
        Sets the blob that this blob orbits (used for moon blobs)

    set_orbital_pos_vel(orbital: BlobSurface) -> Tuple[float,float,float]
        Sets orbital to a position appropriate for an orbital of this blob, and returns velocity as a tuple

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

    index: int
    name: str
    radius: float
    mass: float
    color: Tuple[int, int, int]
    universe: BlobUniverse
    texture: str = None
    ring_texture: str = None
    ring_scale: float = None
    rotation_speed: float = None
    rotation_pos: Tuple[float, float, float] = None
    position: Tuple[float, float, float] = None
    barycenter_index: int = None

    def set_barycenter(self: Self, blob: "BlobSurface") -> None:
        """Sets the blob that this blob orbits (used for moon blobs)"""
        pass

    def set_orbital_pos_vel(
        self: Self, orbital: "BlobSurface"
    ) -> Tuple[float, float, float]:
        """
        Sets orbital to a position appropriate for an orbital of this blob,
        and returns velocity as a tuple
        """
        pass

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
