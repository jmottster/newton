"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area for universe of blobs

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

    size_w: float
    size_h: float

    def get_framework(self: Self) -> Any:
        pass

    def get_width(self: Self) -> float:
        pass

    def get_height(self: Self) -> float:
        pass

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        pass
