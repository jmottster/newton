"""
Newton's Laws, a simulator of physics at the scale of space

Class to create a quad mesh object

by Jason Mott, copyright 2024
"""

from typing import Dict, List, Self, Tuple

import ursina as urs  # type: ignore

from newtons_blobs.globals import *

cached_quads: Dict[str, "BlobQuad"] = dict()  # type: ignore

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


def createBlobQuad(
    radius: float = 0.1,
    segments: int = 8,
    aspect: float = 1,
    scale: Tuple[float, float, float] = (1, 1, 1),
    mode: str = "ngon",
    thickness: float = 1,
):
    """Creates or gets from cache an instance of BlobQuad. The use of a cache is the reason to use this"""

    if radius == 0 and aspect == 1 and scale == (1, 1, 1) and mode == "ngon":
        return urs.Mesh(
            vertices=[
                urs.Vec3(-0.5, 0.0, -0.5),
                urs.Vec3(0.5, 0.0, -0.5),
                urs.Vec3(0.5, 0.0, 0.5),
                urs.Vec3(-0.5, 0.0, 0.5),
            ],
            triangles=[
                (0, 1, 2, 3),
            ],
            uvs=[
                urs.Vec3(0, 0, 0),
                urs.Vec3(1, 0, 0),
                urs.Vec3(1, 0, 1),
                urs.Vec3(0, 0, 1),
            ],
            mode="triangle",
        )
    # copy a cached quad if a QuadMesh with the same settings have been created before
    quad_identifier: str = (
        f"QuadMesh({radius}, {segments}, {aspect}, {scale}, {mode}, {thickness})"
    )
    if quad_identifier in cached_quads and cached_quads[quad_identifier]:
        # print('load cached')
        return urs.deepcopy(cached_quads[quad_identifier])

    return BlobQuad(radius, segments, aspect, scale, mode, thickness)


class BlobQuad(urs.Mesh):
    """
    A class that creates a quad mesh model

    """

    corner_maker = None
    point_placer = None

    def __init__(
        self: Self,
        radius: float = 0.1,
        segments: int = 8,
        aspect: float = 1,
        scale: Tuple[float, float, float] = (1, 1, 1),
        mode: str = "ngon",
        thickness: float = 1,
    ):
        if not BlobQuad.corner_maker:
            BlobQuad.corner_maker = urs.Entity(
                eternal=True, add_to_scene_entities=False
            )
        if not BlobQuad.point_placer:
            BlobQuad.point_placer = urs.Entity(
                parent=BlobQuad.corner_maker,
                eternal=True,
                add_to_scene_entities=False,
            )

        super().__init__()
        self.vertices = [
            urs.Vec3(0, 0, 0),
            urs.Vec3(1, 0, 0),
            urs.Vec3(1, 0, 1),
            urs.Vec3(0, 0, 1),
        ]
        self.radius: float = radius
        self.degrees: float = 0
        self.mode = mode
        self.thickness = thickness

        _segments: int = segments
        _segments += 1
        if _segments > 1:
            self.degrees = -(90 / _segments)
            new_verts = list()
            BlobQuad.corner_maker.rotation_y = 0
            BlobQuad.corner_maker.position = urs.Vec3(0, 0, 0)
            BlobQuad.corner_maker.setHpr((0, 0, self.degrees))
            BlobQuad.point_placer.position = urs.Vec3(-radius, 0, 0)

            corner_corrections: Tuple[urs.Vec3, urs.Vec3, urs.Vec3, urs.Vec3] = (
                urs.Vec3(radius, 0, radius),
                urs.Vec3(-radius, 0, radius),
                urs.Vec3(-radius, 0, -radius),
                urs.Vec3(radius, 0, -radius),
            )
            for j in range(4):  # 4 corners
                BlobQuad.corner_maker.position = (
                    self.vertices[j] + corner_corrections[j]
                )
                for i in range(_segments):
                    new_verts.append(urs.Vec3(BlobQuad.point_placer.world_position))
                    self.degrees += -(90 / _segments)
                    BlobQuad.corner_maker.setHpr((0, 0, self.degrees))

            self.vertices = new_verts

        # scale corners horizontally with aspect
        for v in self.vertices:
            if v[0] < 0.5:
                v[0] /= aspect
            else:
                v[0] = urs.lerp(v[0], 1, 1 - (1 / aspect))

        # move edges out to keep nice corners
        for v in self.vertices:
            if v[0] > 0.5:
                v[0] += scale[0] - 1
            if v[2] > 0.5:
                v[2] += scale[2] - 1

        self.uvs = list()
        for v in self.vertices:
            self.uvs.append(urs.Vec2(v[0], v[2]))

        # center mesh
        offset: List[urs.Vec3] = urs.sum(self.vertices) / len(self.vertices)
        self.vertices = [
            urs.Vec3(v[0] - offset[0], v[1] - offset[1], v[2] - offset[2])
            for v in self.vertices
        ]

        # make the line connect back to start
        if mode == "line":
            self.vertices.append(self.vertices[0])

        self.generate()
        cached_quads[
            f"QuadMesh({radius}, {segments}, {aspect}, {scale}, {mode}, {thickness})"
        ] = self
