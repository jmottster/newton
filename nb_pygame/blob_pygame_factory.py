"""
Newton's Laws, a simulator of physics at the scale of space



by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, cast

from newtons_blobs.globals import *
from newtons_blobs.blob_surface import BlobSurface
from newtons_blobs.blob_display import BlobDisplay
from newtons_blobs.blob_universe import BlobUniverse
from .blob_universe_pygame import BlobUniversePygame
from .blob_display_pygame import BlobDisplayPygame
from .blob_surface_pygame import BlobSurfacePygame


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPygameFactory:

    def __init__(self: Self):
        self.py_universe: BlobUniversePygame = BlobUniversePygame(
            UNIVERSE_SIZE_W, UNIVERSE_SIZE_H
        )
        self.py_display: BlobDisplayPygame = BlobDisplayPygame(
            DISPLAY_SIZE_W, DISPLAY_SIZE_H
        )

    def new_blob_surface(
        self: Self, radius: float, color: Tuple[int, int, int]
    ) -> BlobSurface:
        """Factory method for instantiating instances, as implementation is not known at runtime"""
        return cast(
            BlobSurface, BlobSurfacePygame(radius, color, self.get_blob_universe())
        )

    def get_blob_universe(self: Self) -> BlobUniverse:
        return cast(BlobUniverse, self.py_universe)

    def get_blob_display(self: Self) -> BlobDisplay:
        return cast(BlobDisplay, self.py_display)
