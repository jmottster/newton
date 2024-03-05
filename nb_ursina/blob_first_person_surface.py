"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, cast

import ursina as urs  # type: ignore

from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.globals import *
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

    def __init__(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ):
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.first_person_viewer: BlobFirstPersonUrsina = BlobFirstPersonUrsina(
            scale=CENTER_BLOB_RADIUS / 5,
            universe=self.universe,
            start_z=radius,
            eternal=True,
            mass=MIN_MASS,
        )
        self.radius = radius
        self.color = color

    def get_position(self: Self) -> urs.Vec3:
        return self.first_person_viewer.position

    def resize(self: Self, radius: float) -> None:
        pass

    def update_center_blob(self: Self, x: float, y: float, z: float) -> None:
        pass

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        self.first_person_viewer.position = urs.Vec3(pos)

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        pass

    def destroy(self: Self) -> None:
        if self.first_person_viewer is not None:
            self.first_person_viewer.enabled = False
