"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class that defines an interface for a plugin object for providing
a graphics/drawing library to this simulator

by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, cast

import numpy.typing as npt

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_display_ursina import BlobDisplayUrsina, FirstPersonSurface
from .blob_surface_ursina import BlobSurfaceUrsina
from newtons_blobs import MassiveBlob
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
    new_blob_surface(radius: float, color: Tuple[int, int, int], texture: str = None, rotation_speed: float = None, rotation_pos: Tuple[int, int, int] = None) -> BlobSurface
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime

    get_blob_universe() -> BlobUniverse
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor

    get_blob_display() -> BlobDisplay
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor

    grid_check(proximity_grid: npt.NDArray):
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
    """

    def __init__(self: Self):
        self.urs_display: BlobDisplayUrsina = BlobDisplayUrsina(
            DISPLAY_SIZE_W, DISPLAY_SIZE_H
        )

        self.urs_universe: BlobUniverseUrsina = BlobUniverseUrsina(
            UNIVERSE_SIZE_W, UNIVERSE_SIZE_H
        )

        self.urs_display.first_person_surface = FirstPersonSurface(
            -(DISPLAY_SIZE_H * 3),
            (0, 0, 0),
            self.urs_universe,
        )

        self.first_person_blob: MassiveBlob = MassiveBlob(
            UNIVERSE_SIZE_H,
            "first_person",
            cast(BlobSurface, self.urs_display.first_person_surface),
            MIN_MASS,
            0,
            0,
            -(DISPLAY_SIZE_H * 3) * SCALE_UP,
            0,
            0,
            0,
        )

    def new_blob_surface(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ) -> BlobSurface:
        """
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime
        """
        return cast(
            BlobSurface,
            BlobSurfaceUrsina(
                radius,
                color,
                self.get_blob_universe(),
                texture,
                rotation_speed,
                rotation_pos,
            ),
        )

    def get_blob_universe(self: Self) -> BlobUniverse:
        """
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor
        """
        return cast(BlobUniverse, self.urs_universe)

    def get_blob_display(self: Self) -> BlobDisplay:
        """
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
        """
        return cast(BlobDisplay, self.urs_display)

    def grid_check(self: Self, proximity_grid: npt.NDArray):
        """
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
        """
        pass
