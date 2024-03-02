"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

import random
from typing import ClassVar, Tuple, Self, cast

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.globals import *
from newtons_blobs import relative_resource_path_str
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import BLOB_TEXTURES_SMALL, BLOB_TEXTURES_LARGE

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class Rotator(urs.Entity):

    def __init__(self, **kwargs):
        super().__init__()

        self.rotation_speed = kwargs.get("rotation_speed")

        for key in (
            "model",
            "origin",
            "origin_x",
            "origin_y",
            "origin_z",
            "collider",
            "shader",
            "texture",
            "texture_scale",
            "texture_offset",
        ):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.world_rotation_x = random.random() * 360
        self.world_rotation_y = random.random() * 360
        self.world_rotation_z = random.random() * 360

        if self.rotation_speed is None:
            self.rotation_speed = (random.random() * 5.00) + 1

    def update(self):
        self.rotate((0, self.rotation_speed, 0))

    def on_destroy(self: Self):
        self.hide()


class BlobSurfaceUrsina:
    """
    A Protocol class used to represent an object that draws a blob, with a distinction of the center blob

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : tuple
        a three value tuple for RGB color value of blob
    universe: BlobUniverse
        The universe instance the blobs will be drawn on
    texture : str
        For 3d rendering, this is optional (implement as texture = None in __init__)


    Methods
    -------

    resize(radius: float) -> None
        Sets a new radius for this blob

    update_center_blob(x: float, y: float, z: float) -> None
        Update the x,y,z of the center blob (for lighting effects, etc.,
        all blobs are informed where the center blob is)

    draw(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects

    draw_as_center_blob(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect

    destroy() -> None
        Call to get rid of this instance, so it can clean up
    """

    center_blob_x: ClassVar[float] = 0
    center_blob_y: ClassVar[float] = 0
    center_blob_z: ClassVar[float] = 0

    def __init__(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
    ):

        self.radius: float = radius
        self.color: Tuple[int, int, int] = color
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        if texture is not None:
            self.texture = texture
        else:
            if self.radius >= (MAX_RADIUS * 0.85):
                self.texture = BLOB_TEXTURES_LARGE[
                    random.randint(1, len(BLOB_TEXTURES_LARGE) - 1)
                ]
            else:
                self.texture = BLOB_TEXTURES_SMALL[
                    random.randint(1, len(BLOB_TEXTURES_SMALL) - 1)
                ]
        self.rotation_speed = None
        if rotation_speed is not None:
            self.rotation_speed = rotation_speed

        self.ursina_center_blob: urs.PointLight = None
        self.ursina_blob: Rotator = None

        if color == CENTER_BLOB_COLOR:
            self.ursina_blob = Rotator(
                position=(0, 0, 0),
                model=relative_resource_path_str("nb_ursina/models/local_uvsphere", ""),
                scale=radius,
                texture=relative_resource_path_str("nb_ursina/textures/sun03.png", ""),
                rotation_speed=self.rotation_speed,
                texture_scale=(1, 1),
                collider="mesh",
                color=urs.color.rgb(100, 100, 100, 255),
                shader=shd.lit_with_shadows_shader,
            )
            self.ursina_center_blob = urs.PointLight(
                parent=self.ursina_blob,
                position=(0, 0, 0),
                shadows=True,
                shadow_map_resolution=(4096, 4096),
                max_distance=2000,
                attenuation=(0, 0, 1),
                color=(2.5, 2.5, 2.5, 2),
            )
        else:
            self.ursina_blob = Rotator(
                position=(0, 0, 0),
                model=relative_resource_path_str("nb_ursina/models/local_uvsphere", ""),
                scale=radius,
                texture=relative_resource_path_str(self.texture, ""),
                rotation_speed=self.rotation_speed,
                texture_scale=(1, 1),
                collider="mesh",
                shader=shd.lit_with_shadows_shader,
            )
            self.ursina_blob.setShaderAuto()

        self.rotation_speed = self.ursina_blob.rotation_speed

    def resize(self: Self, radius: float) -> None:
        """Sets a new radius for this blob"""
        pass

    def update_center_blob(self: Self, x: float, y: float, z: float) -> None:
        """
        Update the x,y,z of the center blob (for lighting effects, etc.,
        all blobs are informed where the center blob is)
        """
        BlobSurfaceUrsina.center_blob_x = x
        BlobSurfaceUrsina.center_blob_y = y
        BlobSurfaceUrsina.center_blob_z = z

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects
        """
        self.ursina_blob.position = urs.Vec3(pos)

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect
        """
        if lighting:
            # self.universe.center_blob_light_on(self.ursina_blob)
            if not self.ursina_center_blob.enabled:
                self.ursina_center_blob.enabled = True
                # self.ursina_center_blob.position = urs.Vec3(pos)
        else:
            # self.universe.center_blob_light_off()
            if self.ursina_center_blob.enabled:
                self.ursina_center_blob.enabled = False
        # print(f"center blob light: {self.ursina_center_blob.world_position}")

        self.ursina_blob.position = urs.Vec3(pos)

    def destroy(self: Self) -> None:
        if self.ursina_center_blob is not None:
            self.ursina_center_blob.enabled = False
            # self.ursina_center_blob = None

        self.ursina_blob.enabled = False
        # self.ursina_blob = None
