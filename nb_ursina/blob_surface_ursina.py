"""
Newton's Laws, a simulator of physics at the scale of space

A class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

import math
import random
from typing import ClassVar, Tuple, Self, cast


from panda3d.core import ClockObject  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore


from newtons_blobs import BlobSurface
from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
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


class TrailRenderer(urs.Entity):
    def __init__(
        self,
        size=[1, 1, 1],
        segments=2,
        min_spacing=0.05,
        fade_speed=0,
        color_gradient=[urs.color.white, urs.color.white.tint(-0.5), urs.color.clear],
        **kwargs,
    ):

        super().__init__(**kwargs)
        if color_gradient:
            color_gradient = color_gradient[::-1]

        self.renderer = urs.Entity(
            model=urs.Pipe(
                base_shape=urs.Quad(segments=0, scale=size),
                path=[self.world_position, self.world_position],
                color_gradient=color_gradient,
                static=False,
                cap_ends=False,
            ),
        )

        self._t = 0
        self.segments = segments
        self.update_step = 0.05
        self.min_spacing = min_spacing
        self.fade_speed = fade_speed
        self.render = False

        self.on_enable = self.renderer.enable
        self.on_disable = self.renderer.disable

        # self.enabled = False

    def update(self):
        self._t += urs.time.dt
        if self._t >= self.update_step:

            self._t = 0

            if (
                urs.distance(self.world_position, self.renderer.model.path[-1])
                > self.min_spacing
            ):
                self.renderer.model.path.append(self.world_position)
                if len(self.renderer.model.path) > self.segments:
                    self.renderer.model.path.pop(0)

            if self.fade_speed:
                for i, v in enumerate(self.renderer.model.path):
                    if i >= len(self.renderer.model.path) - 1:
                        continue
                    self.renderer.model.path[i] = urs.lerp(
                        v,
                        self.renderer.model.path[i + 1],
                        urs.time.dt * self.fade_speed,
                    )

            self.renderer.model.generate()

    def on_destroy(self):
        urs.destroy(self.renderer)


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
    set_orbital_pos_vel(orbital: BlobSurface) -> None
        Sets orbital to a position and velocity appropriate for an orbital of this blob

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

    __slots__ = ("mass", "rotation_speed", "rotation_pos", "trail_color", "trail")

    def __init__(self: Self, **kwargs):

        self.rotation_speed: float = None
        self.rotation_pos: Tuple[float, float, float] = None

        self.rotation_speed = kwargs.get("rotation_speed")
        self.rotation_pos = kwargs.get("rotation_pos")

        self.blob_name: str = kwargs.get("name")

        self.mass: float = kwargs.get("mass")

        self.trail_color: urs.Color = kwargs.get("trail_color")

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

        self.trail: TrailRenderer = None

        self.world_rotation_x: float = 0.0
        self.world_rotation_y: float = 0.0
        self.world_rotation_z: float = 0.0

        if self.blob_name == CENTER_BLOB_NAME:
            self.world_rotation_x = 90
        else:
            self.world_rotation_x = 45
            change = random.random() * 90
            self.world_rotation_x += change

        # If rotation_pos coming from saved file, set world rotation values to that
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
            self.rotation_speed = (random.random() * 29.00) + 1

        self.text_entity: urs.Entity = None

        self.info_text: urs.Text = None

        self.text_light: BlobAmbientLight = None

        self.text: str = None

        self.text_scale: urs.Vec3 = urs.Vec3(0.1, 0.1, 0.1)
        self.text_position: float = 11

        if self.scale_x < bg_vars.min_radius:
            self.text_scale = urs.Vec3(0.08, 0.08, 0.08)
        # else:
        #     self.text_position = 100

        self.all_on: bool = False
        self.full_details: bool = False

    def set_orbital_pos_vel(self: Self, orbital: "BlobSurfaceUrsina") -> urs.Vec3:

        self.rotate((0, (random.random() * 360.00), 0))
        orbital.ursina_blob.world_rotation = self.world_rotation
        orbital.ursina_blob.rotation_pos = self.rotation_pos

        orbit_distance: float = (
            random.random() * (self.scale_x * 3)
        ) + self.scale_x * 5
        move: urs.Vec3 = urs.Vec3(self.left.normalized() * orbit_distance)

        orbital.ursina_blob.position = urs.Vec3(self.position + move)
        orbital.position = orbital.ursina_blob.world_position

        dx: float = (self.world_x - orbital.ursina_blob.world_x) * bg_vars.scale_up
        dy: float = (self.world_y - orbital.ursina_blob.world_y) * bg_vars.scale_up
        dz: float = (self.world_z - orbital.ursina_blob.world_z) * bg_vars.scale_up

        distance: float = math.sqrt(dx**2 + dy**2 + dz**2)

        vel: float = math.sqrt(G * self.mass / distance)

        return urs.Vec3(orbital.ursina_blob.forward.normalized() * vel)

    def create_text_overlay(self: Self) -> None:
        """
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()
        """

        if self.text_entity is None:
            self.text_entity = urs.Entity(scale=self.scale)

            self.text = f"{self.blob_name}"

            if self.full_details:
                self.text = f"{self.blob_name}: mass: {float(self.mass)} radius: {round(self.scale_x,2)} x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"

            self.info_text = urs.Text(
                self.text,
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
        self.update_text_background()

    def update_text_background(self: Self):
        if self.info_text is not None:

            self.text = f"{self.blob_name}"

            if self.full_details:
                self.text = f"{self.blob_name}: mass: {float(self.mass)} radius: {round(self.scale_x,2)} x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"

            self.info_text.text = self.text
            self.info_text.create_background(
                self.info_text.size * 0.5,
                self.info_text.size * 0.25,
                urs.color.rgb(
                    BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
                ),
            )
            self.info_text._background.z = 0.5
            self.info_text.setShaderAuto()

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

            self.text = f"{self.blob_name}"

            if self.full_details:
                self.text = f"{self.blob_name}: mass: {float(self.mass)} radius: {round(self.scale_x,2)} x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"

            self.text_entity.position = self.position
            self.text_entity.rotation = urs.camera.parent.rotation
            dx = urs.camera.parent.world_x - self.text_entity.world_x
            dy = urs.camera.parent.world_y - self.text_entity.world_y
            dz = urs.camera.parent.world_z - self.text_entity.world_z
            d = math.sqrt(dx**2 + dy**2 + dz**2)
            self.text_entity.scale = self.text_scale * d
            self.text_entity.position += self.text_entity.up * (
                (self.world_scale_x * self.text_position) / d
            )
            self.info_text.text = self.text

        degrees = self.rotation_speed * (
            (ClockObject.getGlobalClock().getDt() * bg_vars.timescale) / HOURS
        )

        self.rotate((0, degrees, 0))

    def on_click(self: Self) -> None:
        """
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused
        """
        self.full_details = not self.full_details

        if self.full_details:
            self.create_text_overlay()
        else:
            if not self.all_on:
                self.destroy_text_overlay()
            else:
                self.update_text_background()

    def input(self: Self, key: str) -> None:
        """Called by Ursina when a keyboard event happens"""
        if key == "b":
            self.all_on = not self.all_on

            if self.all_on:
                self.create_text_overlay()
            else:
                if not self.full_details:
                    self.destroy_text_overlay()
                else:
                    self.update_text_background()

    def on_disable(self: Self) -> None:
        """
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay
        """
        self.destroy_text_overlay()

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""
        if self.trail is not None:
            self.trail.enabled = False
        urs.destroy(self.trail)
        self.destroy_text_overlay()
        self.hide()


class BlobSurfaceUrsina:
    """
    A class used to represent an object that draws a blob, with a distinction of the center blob

    Attributes
    ----------
    name: str
        A name for the instance
    radius : float
        the size of the blob, by radius value
    mass : float
        the mass of the blob, in kg
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
    position : Tuple[float,float,float] = (0,0,0)
        The x,y,z position for this blob

    Methods
    -------
    set_orbital_pos_vel(orbital: BlobSurface) -> None
        Sets orbital to a position and velocity appropriate for an orbital of this blob

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

    on_destroy() -> None
        Call when getting rid of this instance, so it can clean up

    destroy() -> None
        Call when getting rid of this instance, so it can clean up
    """

    __slots__ = (
        "name",
        "radius",
        "mass",
        "position",
        "color",
        "trail_color",
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
        mass: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[float, float, float] = None,
    ):

        self.name: str = name
        self.radius: float = radius
        self.mass: float = mass
        position: Tuple[float, float, float] = (0, 0, 0)
        self.color: Tuple[int, int, int] = color
        self.trail_color: urs.Color = urs.color.rgba(
            self.color[0], self.color[1], self.color[2], 255
        )
        self.texture: str = None
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)

        urs_color = urs.color.rgba(self.color[0], self.color[1], self.color[2])

        if bg_vars.textures_3d:
            if texture is not None:
                self.texture = texture
            else:
                if self.radius >= (bg_vars.max_radius * 0.75):
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

            urs_color = urs.color.rgba(150, 150, 150, 255)

            enabled: bool = not bg_vars.black_hole_mode
            self.texture = "nb_ursina/textures/sun03.png"

            self.trail_color = urs.color.rgba(
                self.color[0], self.color[1], self.color[2], 255
            )

            if not enabled:
                urs_color = urs.color.rgba(100, 100, 100, 0)

            if not bg_vars.textures_3d:
                urs_color = urs.rgb(
                    CENTER_BLOB_COLOR[0], CENTER_BLOB_COLOR[1], CENTER_BLOB_COLOR[2]
                )
                texture = None
            self.ursina_blob = Rotator(
                blob_name=self.name,
                position=(0, 0, 0),
                model="local_uvsphere",
                scale=(self.radius, self.radius, self.radius),
                mass=self.mass,
                texture=self.texture,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                texture_scale=(1, 1),
                collider="mesh",
                color=urs_color,
                trail_color=self.trail_color,
                shader=shd.lit_with_shadows_shader,
                enabled=enabled,
            )
            self.ursina_center_blob = BlobPointLight(
                # parent=self.ursina_blob,
                scale=(self.radius, self.radius, self.radius),
                position=(0, 0, 0),
                shadows=True,
                shadow_map_resolution=(4096, 4096),
                max_distance=bg_vars.universe_size * 1000,
                attenuation=(1, 0, 0),
                color=(5, 5, 5, 5),
            )
        else:

            self.trail_color = urs.color.rgba(
                self.color[0], self.color[1], self.color[2], 255
            )

            if not bg_vars.textures_3d:
                self.texture = None
            else:
                urs_color = urs.color.rgba(255, 255, 255, 255)

            self.ursina_blob = Rotator(
                blob_name=self.name,
                position=(0, 0, 0),
                model="local_uvsphere",
                scale=(self.radius, self.radius, self.radius),
                mass=self.mass,
                texture=self.texture,
                color=urs_color,
                trail_color=self.trail_color,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                texture_scale=(1, 1),
                collider="mesh",
                shader=shd.lit_with_shadows_shader,
            )
            self.ursina_blob.setShaderAuto()

        self.rotation_speed = self.ursina_blob.rotation_speed
        self.rotation_pos = self.ursina_blob.rotation_pos

    def set_orbital_pos_vel(
        self: Self, orbital: BlobSurface
    ) -> Tuple[float, float, float]:
        """
        Sets orbital to a position appropriate for an orbital of this blob,
        and returns velocity as a tuple
        """
        return self.ursina_blob.set_orbital_pos_vel(cast(BlobSurfaceUrsina, orbital))

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

        self.position = pos
        self.ursina_blob.position = urs.Vec3(pos)

        # if self.ursina_blob.trail is None:
        #     self.create_trail()

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

        self.position = pos
        self.ursina_center_blob.position = urs.Vec3(pos)
        self.ursina_blob.position = urs.Vec3(pos)

        # if self.ursina_blob.trail is None:
        #     self.create_trail()

    def create_trail(self) -> None:

        self.ursina_blob.trail = TrailRenderer(
            size=[
                bg_vars.blob_trail_girth,
                bg_vars.blob_trail_girth,
                bg_vars.blob_trail_girth,
            ],
            segments=4,
            min_spacing=bg_vars.blob_trail_girth,
            fade_speed=0,
            parent=self.ursina_blob,
            # color_gradient=[
            #     self.trail_color,
            #     self.trail_color.tint(-0.75),
            #     urs.color.rgba(0, 0, 0, 100),
            # ],
        )

    def on_destroy(self: Self) -> None:
        """Call when getting rid of this instance, so it can clean up"""
        self.destroy()

    def destroy(self: Self) -> None:
        """Call when getting rid of this instance, so it can clean up"""

        if self.ursina_center_blob is not None:
            # self.ursina_center_blob.color = (0, 0, 0, 0)
            self.ursina_center_blob.destroy()
            urs.destroy(self.ursina_center_blob)
            self.ursina_center_blob = None

        self.ursina_blob.enabled = False
        # self.ursina_blob = None
