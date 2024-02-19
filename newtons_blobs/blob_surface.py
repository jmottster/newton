"""
Newton's Laws, a simulator of physics at the scale of space

Class for building the blob objects for display

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
    A Protocol class used to represent an object that draw a blob, with a distinction of the center blob.

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : tuple
        a three value tuple for RGB color value of blob
    universe : A BlobUniverse object representing the universe space to draw blobs onto



    Methods
    -------
    Except for the three below, all the methods are internal use only. Comment annotations explain what's going on
    as best they can. :)

    resize(radius: float) -> None
        Sets a new radius for this blob

    update_center_blob(x: float, y: float, z: float) -> None
        Update the x,y,z of the center blob (the blob all other blobs get lighting from)

    draw(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects

    draw_as_center_blob(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect
    """

    radius: float
    color: tuple
    universe: BlobUniverse

    def resize(self: Self, radius: float) -> None:
        """Update the radius"""
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
        """Draw the blob to the universe surface. Send pos,False to turn off lighting effects"""
        pass

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        pos,False to turn off glowing effect
        """
        pass
