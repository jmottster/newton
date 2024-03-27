"""
Newton's Laws, a simulator of physics at the scale of space

A class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

import random
from typing import ClassVar, Tuple, Self, cast

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore


from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars
from newtons_blobs import BlobUniverse
from newtons_blobs import resource_path

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import BLOB_TEXTURES_SMALL, BLOB_TEXTURES_LARGE
from .blob_lights import BlobPointLight, BlobAmbientLight

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class Rotator(urs.Entity):
    """
    A class to create a blob Entity that rotates

    Attributes
    ----------
    **kwargs
        Specific to this class:
        rotation_speed: float, rotation_pos: Tuple[float, float, float]

    Methods
    -------
    create_text_overlay() -> None
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()

    destroy_text_overlay() -> None
        Cleans up all the objects related to the text overlay. Called by
        on_click()

    update() -> None
        Called by Ursina engine once per frame

    on_click() -> None
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused

    on_disable() -> None
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay

     on_destroy() -> None
        Called when this Entity is destroyed

    """

    __slots__ = (
        "rotation_speed",
        "rotation_pos",
    )

    def __init__(self: Self, **kwargs):

        self.rotation_speed: float = None
        self.rotation_pos: Tuple[float, float, float] = None

        self.rotation_speed = kwargs.get("rotation_speed")
        self.rotation_pos = kwargs.get("rotation_pos")

        self.blob_name: str = kwargs.get("name")

        super().__init__()

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

        self.world_rotation_x: float = 0.0
        self.world_rotation_y: float = 0.0
        self.world_rotation_z: float = 0.0

        if self.blob_name == CENTER_BLOB_NAME:
            self.world_rotation_x = 90
        else:
            self.world_rotation_x = random.random() * 360
            self.world_rotation_y = random.random() * 360
            self.world_rotation_z = random.random() * 360

        if self.rotation_pos is not None:
            self.world_rotation_x, self.world_rotation_y, self.world_rotation_z = (
                self.rotation_pos
            )

        self.rotation_pos = (
            self.world_rotation_x,
            self.world_rotation_y,
            self.world_rotation_z,
        )

        if self.rotation_speed is None:
            self.rotation_speed = (random.random() * 5.00) + 1

        self.text_entity: urs.Entity = None

        self.info_text: urs.Text = None

        self.text_light: BlobAmbientLight = None

    def create_text_overlay(self: Self) -> None:
        """
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()
        """

        if self.text_entity is None:
            self.text_entity = urs.Entity(scale=self.scale)

            self.info_text = urs.Text(
                f"{self.blob_name}: radius: {round(self.scale_x,2)} x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}",
                parent=self.text_entity,
                font=DISPLAY_FONT,
                size=(STAT_FONT_SIZE * 0.1),
                # resolution=(100 * (STAT_FONT_SIZE * 0.1)),
                origin=(0, -0.5),
                position=(0, 0, 0),
                scale=(0.1, 0.1, 0.1),
                color=urs.rgb(255, 255, 255, 255),
                shader=shd.lit_with_shadows_shader,
                enabled=False,
            )
            self.info_text.create_background(
                self.info_text.size * 0.5,
                self.info_text.size * 0.25,
                urs.color.rgb(
                    BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
                ),
            )
            self.info_text._background.z = 0.5
            self.info_text.setShaderAuto()
            self.text_light = BlobAmbientLight(
                parent=self.info_text,
                light_name=self.blob_name,
                entity_set_light=self.info_text,
                position=(0, 0, -1),
                shadows=True,
                shadow_map_resolution=(4096, 4096),
                max_distance=2,
                attenuation=(0, 0, 1),
                color=(2.5, 2.5, 2.5, 2),
            )
        self.text_entity.enabled = True
        self.info_text.enabled = True
        self.text_light.enabled = True

    def destroy_text_overlay(self: Self) -> None:
        """
        Cleans up all the objects related to the text overlay. Called by
        on_click()
        """
        if self.text_entity is not None:
            self.text_light.destroy()
            urs.destroy(self.text_light)
            self.text_light = None
            self.info_text.enabled = False
            urs.destroy(self.info_text)
            self.info_text = None
            self.text_entity.enabled = False
            urs.destroy(self.text_entity)
            self.text_entity = None

    def update(self: Self) -> None:
        """Called by Ursina engine once per frame"""

        if self.text_entity is not None and self.info_text.enabled:

            self.info_text.text = f"{self.blob_name}: radius: {round(self.scale_x,2)} x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"
            self.text_entity.position = self.position
            self.text_entity.rotation = urs.camera.parent.rotation
            self.text_entity.position += self.text_entity.up * 1.1

        self.rotate((0, self.rotation_speed, 0))

    def on_click(self: Self) -> None:
        """
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused
        """

        if self.text_entity is None:
            self.create_text_overlay()
        else:
            self.destroy_text_overlay()

    def on_disable(self: Self) -> None:
        """
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay
        """
        self.destroy_text_overlay()

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""
        self.destroy_text_overlay()
        self.hide()


class BlobSurfaceUrsina:
    """
    A class used to represent an object that draws a blob, with a distinction of the center blob

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
    rotation_speed : float = None
        For 3d rendering, the speed (degrees per frame) at which the blob will spin
    rotation_pos : Tuple[float, float, float] = None
        For 3d rendering, the z,y,z angles of orientation of the blob (in degrees)

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
        Call when getting rid of this instance, so it can clean up
    """

    __slots__ = (
        "name",
        "radius",
        "color",
        "universe",
        "texture",
        "rotation_speed",
        "rotation_pos",
        "ursina_center_blob",
        "ursina_blob",
    )

    center_blob_x: ClassVar[float] = 0
    center_blob_y: ClassVar[float] = 0
    center_blob_z: ClassVar[float] = 0

    def __init__(
        self: Self,
        name: str,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[float, float, float] = None,
    ):

        self.name: str = name
        self.radius: float = radius
        self.color: Tuple[int, int, int] = color
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.texture: str = None

        if texture is not None:
            self.texture = texture
        else:
            if self.radius >= (BlobGlobalVars.max_radius * 0.85):
                self.texture = BLOB_TEXTURES_LARGE[
                    random.randint(1, len(BLOB_TEXTURES_LARGE) - 1)
                ]
            else:
                self.texture = BLOB_TEXTURES_SMALL[
                    random.randint(1, len(BLOB_TEXTURES_SMALL) - 1)
                ]
        self.rotation_speed: float = None
        self.rotation_pos: Tuple[float, float, float] = None

        if rotation_speed is not None:
            self.rotation_speed = rotation_speed
        if rotation_pos is not None:
            self.rotation_pos = rotation_pos

        self.ursina_center_blob: BlobPointLight = None
        self.ursina_blob: Rotator = None

        if color == CENTER_BLOB_COLOR:
            self.texture = "nb_ursina/textures/sun03.png"
            self.ursina_blob = Rotator(
                blob_name=self.name,
                position=(0, 0, 0),
                model="local_uvsphere",
                scale=radius,
                texture=self.texture,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                texture_scale=(1, 1),
                collider="mesh",
                color=urs.color.rgb(100, 100, 100, 255),
                shader=shd.lit_with_shadows_shader,
            )
            self.ursina_center_blob = BlobPointLight(
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
                blob_name=self.name,
                position=(0, 0, 0),
                model="local_uvsphere",
                scale=radius,
                texture=self.texture,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                texture_scale=(1, 1),
                collider="mesh",
                shader=shd.lit_with_shadows_shader,
            )
            self.ursina_blob.setShaderAuto()

        self.rotation_speed = self.ursina_blob.rotation_speed
        self.rotation_pos = self.ursina_blob.rotation_pos

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
        """Call when getting rid of this instance, so it can clean up"""

        if self.ursina_center_blob is not None:
            # self.ursina_center_blob.color = (0, 0, 0, 0)
            self.ursina_center_blob.destroy()
            urs.destroy(self.ursina_center_blob)
            self.ursina_center_blob = None

        self.ursina_blob.enabled = False
        # self.ursina_blob = None
