"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area for the universe of blobs

by Jason Mott, copyright 2025
"""

from typing import Any, Tuple, Self, Protocol

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2026"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUniverse(Protocol):
    """
    Protocol class to represent an object that holds and controls a drawing area for the universe of blobs

    Methods
    -------
    set_universe_entity(scale: float, texture: str = None) -> None
        Creates the Entity that renders the dome of the background image (stars)

    get_framework(self: Self) -> Any
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_center_blob_start_pos() -> Tuple[float,float,float]
        Returns a tuple of the center point x,y,z

    get_center_offset(x: float, y: float, z: float) -> Tuple[float, float, float]
        Returns a tuple of offset values from center to given x,y,z

    clear() -> None
        Used to delete and properly clean up blobs (for a start over, for example)

    """

    def set_universe_entity(self: Self, scale: float, texture: str = None) -> None:
        """Creates the Entity that renders the dome of the background image (stars)"""
        pass

    def get_framework(self: Self) -> Any:
        """
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access
        """
        pass

    def get_center_blob_start_pos(self: Self) -> Tuple[float, float, float]:
        """Returns a tuple of the center point x,y,z"""
        pass

    def get_center_offset(
        self: Self, x: float, y: float, z: float
    ) -> Tuple[float, float, float]:
        """Returns a tuple of offset values from center to given x,y,z"""
        pass

    def clear(self: Self) -> None:
        """Used to delete and properly clean up blobs (for a start over, for example)"""
        pass
