"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area for the universe of blobs

by Jason Mott, copyright 2024
"""

from typing import Any, Tuple, Self, Protocol

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUniverse(Protocol):
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
    get_framework(self: Self) -> Any
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_width(self: Self) -> float
        Returns the current width of the universe object

    get_height(self: Self) -> float
        Returns the current height of the universe object

    fill(self: Self, color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    """

    size_w: float
    size_h: float

    def get_framework(self: Self) -> Any:
        """
        Returns the underlying framework implementation of the drawing area for the universe, mostly for use
        in an implementation of BlobSurface within the same framework for direct access
        """
        pass

    def get_width(self: Self) -> float:
        """
        Returns the current width of the universe object
        """
        pass

    def get_height(self: Self) -> float:
        """
        Returns the current height of the universe object
        """
        pass

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        pass
