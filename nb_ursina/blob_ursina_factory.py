"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class that defines an interface for a plugin object for providing
a graphics/drawing library to this simulator

by Jason Mott, copyright 2024
"""

from typing import Tuple, Self

import ursina  # type: ignore

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_display_ursina import BlobDisplayUrsina
from .blob_surface_ursina import BlobSurfaceUrsina
from newtons_blobs.blob_surface import BlobSurface
from newtons_blobs.blob_display import BlobDisplay
from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUrsinaFactory:
    """
    A Protocol class that defines an interface for a plugin object for providing
    a graphics/drawing library to this simulator

    Methods
    -------
    new_blob_surface(self: Self, radius: float, color: Tuple[int, int, int]) -> BlobSurface
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime

    get_blob_universe(self: Self) -> BlobUniverse
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor

    get_blob_display(self: Self) -> BlobDisplay
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
    """

    def new_blob_surface(
        self: Self, radius: float, color: Tuple[int, int, int]
    ) -> BlobSurface:
        """
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime
        """
        pass

    def get_blob_universe(self: Self) -> BlobUniverse:
        """
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor
        """
        pass

    def get_blob_display(self: Self) -> BlobDisplay:
        """
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
        """
        pass
