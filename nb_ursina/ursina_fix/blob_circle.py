"""
Newton's Laws, a simulator of physics at the scale of space

Class to create a circle mesh object

by Jason Mott, copyright 2025
"""

from typing import Self
import ursina as urs  # type: ignore

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobCircle(urs.Mesh):
    """
    A class to create a circle mesh model

    """

    def __init__(
        self: Self,
        resolution: int = 16,
        radius: float = 0.5,
        mode: str = "ngon",
        thickness: float = 1,
        **kwargs,
    ):
        origin: urs.Entity = urs.Entity()
        point: urs.Entity = urs.Entity(parent=origin)
        point.z = radius
        self.degrees: float = 0

        self.vertices = list()
        for _ in range(resolution):
            self.degrees -= 360 / resolution

            origin.setHpr((0, 0, self.degrees))
            self.vertices.append(point.world_position)

        if mode == "line":  # add the first point to make the circle whole
            self.vertices.append(self.vertices[0])

        urs.destroy(origin)
        super().__init__(
            vertices=self.vertices, mode=mode, thickness=thickness, **kwargs
        )
