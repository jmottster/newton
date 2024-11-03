"""
Newton's Laws, a simulator of physics at the scale of space

A class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

import math
import random
from typing import ClassVar, Tuple, Self, cast
from collections import deque


from panda3d.core import ClockObject  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore


from newtons_blobs import BlobSurface
from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs import BlobUniverse

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import BLOB_TEXTURES_SMALL, BLOB_TEXTURES_LARGE
from .blob_lights import BlobPointLight, BlobAmbientLight
from .blob_utils_ursina import FPS

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class TrailRenderer(urs.Entity):
    """
    A class to create a trail behind an orbiting blob

    Attributes
    ----------
    **kwargs
        Specific to this class:
        segments: int = 2 - How many "min_spacing" links there are
        min_spacing: float = 0.05 -  How often (in pixels) to place a draw point in the trail

    Methods
    -------
    update() -> None
        Called by Ursina once per frame. This will keep the trial
        current and only min_spacing * segments long

    calibrate_segments(new: bool = False) -> None
        Called when the number of items in self.last_point_distances >= self.spacing_check
        this will adjust self.min_spacing and self.segments to control the length of the trail

    on_enable() -> None
        Called by Ursina when self.enabled is set to True. This passes the True flag on to
        self.line_renderer

    on_disable() -> None
        Called by Ursina when self.enabled is set to False. This passes the False flag on to
        self.line_renderer

    on_destroy() -> None
        Called by Ursina when this Entity is destroyed

    """

    __slots__ = (
        "segments",
        "points",
        "_t",
        "_t2",
        "min_spacing",
        "update_step",
        "thickness",
        "barycenter_blob",
        "barycenter_last_pos",
        "check_barycenter_dist",
        "line_renderer",
    )

    def __init__(
        self: Self,
        segments: int = 2,
        min_spacing: float = 0.05,
        barycenter_blob: "Rotator" = None,
        **kwargs,
    ):

        self.line_renderer: urs.Entity = None

        self.is_moon: bool = kwargs.get("is_moon", False)

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

        self.segments: int = segments

        self._t: float = 0

        self.min_spacing: float = min_spacing
        self.update_step: float = 1
        self.thickness: int = 2
        self.barycenter_blob: Rotator = barycenter_blob
        self.barycenter_last_pos: urs.Vec3 = None
        self.check_barycenter_dist: float = 2
        if self.is_moon:
            if self.barycenter_blob is not None:
                self.barycenter_last_pos = self.barycenter_blob.world_position
            self.thickness = 1
            self.min_spacing = bg_vars.min_moon_radius
            self.update_step = 0
            self.segments = 250

        self.orig_segments: int = self.segments

        self.points: deque[urs.Vec3] = deque(
            [self.world_position for _ in range(0, self.segments)]
        )

        self.last_point_index: int = self.segments - 2

        # self.min_spacing *= 2

        self.spacing_check: int = self.orig_segments - 10
        self.last_point_distances: deque[urs.Vec3] = deque(
            [self.min_spacing for _ in range(0, self.spacing_check)]
        )

        self.line_renderer = urs.Entity(
            model=urs.Mesh(
                vertices=self.points,
                mode="line",
                thickness=self.thickness,
            ),
            color=self.color,
            shader=shd.unlit_shader,
        )

        if self.is_moon:
            self.enabled = False

    def update(self: Self) -> None:
        """
        Called by Ursina once per frame. This will keep the trial
        current and only min_spacing * segments long
        """

        if self.barycenter_blob is not None:

            diff: urs.Vec3 = (
                self.barycenter_blob.world_position - self.barycenter_last_pos
            )
            self.barycenter_last_pos = self.barycenter_blob.world_position

            for i in range(0, len(self.points)):
                self.points[i] = self.points[i] + diff

        self._t += urs.time.dt

        if not FPS.paused and (self._t >= self.update_step):

            if len(self.last_point_distances) >= self.spacing_check:
                self.calibrate_segments()

            self.last_point_distances.append(
                urs.distance(self.points[self.last_point_index], self.points[-1])
            )

            if self.last_point_distances[-1] > self.min_spacing:

                self.points.popleft()
                self.points.append(self.world_position)

            else:
                self.points[-1] = self.world_position

            self._t = 0
        else:
            self.points[-1] = self.world_position

        self.line_renderer.model.generate()

    def calibrate_segments(self: Self, new: bool = False) -> None:
        """
        Called when the number of items in self.last_point_distances >= self.spacing_check
        this will adjust self.min_spacing and self.segments to control the length of the trail
        """

        if self.parent.blob_name == CENTER_BLOB_NAME:
            return

        if new:
            for i in range(0, self.segments):
                self.points[i] = self.world_position

        barycenter = BlobSurfaceUrsina.center_blob

        if self.barycenter_blob is not None:
            barycenter = self.barycenter_blob

        r = urs.distance(self.parent, barycenter)

        self.min_spacing = (r * math.pi) / self.orig_segments

        avg_length = sum(self.last_point_distances) / len(self.last_point_distances)

        self.last_point_distances.clear()

        # print(
        #     f"{self.parent.blob_name}: avg_length < self.min_spacing: {round(avg_length,2)} < {round(self.min_spacing,2)}"
        # )

        if avg_length < self.min_spacing:
            avg_length = self.min_spacing
            self.segments = self.orig_segments
        else:
            arc = r * (math.asin(avg_length / (r * 2)) * 2)
            self.segments = round((r * math.pi) / arc)

        # print(f"{self.parent.blob_name}: self.segments: {self.segments}")

        self.last_point_index = self.segments - 2

        if len(self.points) > self.segments:
            while len(self.points) > self.segments:
                self.points.popleft()

        else:
            if len(self.points) < self.segments:
                while len(self.points) < self.segments:
                    self.points.appendleft(self.points[0])

    def on_enable(self: Self) -> None:
        """
        Called by Ursina when self.enabled is set to True. This passes the True flag on to
        self.line_renderer
        """
        if self.line_renderer is not None:
            if not self.line_renderer.enabled:
                self.line_renderer.enabled = True

                self.calibrate_segments(True)

    def on_disable(self: Self) -> None:
        """
        Called by Ursina when self.enabled is set to False. This passes the False flag on to
        self.line_renderer
        """
        if self.line_renderer is not None:
            self.line_renderer.enabled = False

    def on_destroy(self: Self) -> None:
        """Called by Ursina when this Entity is destroyed"""
        self.line_renderer.enabled = False
        self.line_renderer.model.clear()

        self.points.clear()
        self.points = None

        urs.destroy(self.line_renderer)

        self.barycenter_blob = None


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

    create_trail() -> None
        Creates the orbital trail. Called by input() when the "t" key is pressed if it
        is not running

    create_text_overlay() -> None
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()

    update_text_background() -> None
        This is for when text changes, it will ensure the background size updates accordingly

    destroy_text_overlay() -> None
        Cleans up all the objects related to the text overlay. Called by
        on_click()

    update() -> None
        Called by Ursina engine once per frame

    on_click() -> None
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused

    input(key: str) -> None
        Called by Ursina when a keyboard event happens

    on_disable() -> None
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay

     on_destroy() -> None
        Called when this Entity is destroyed

    """

    __slots__ = (
        "mass",
        "rotation_speed",
        "rotation_pos",
        "trail_color",
        "trail",
        "barycenter_blob",
    )

    def __init__(self: Self, **kwargs):

        self.rotation_speed: float = None
        self.rotation_pos: Tuple[float, float, float] = None

        self.rotation_speed = kwargs.get("rotation_speed")
        self.rotation_pos = kwargs.get("rotation_pos")

        self.blob_name: str = kwargs.get("name")

        self.mass: float = kwargs.get("mass")

        self.trail_color: urs.Color = kwargs.get("trail_color")

        self.radius: urs.Vec3 = urs.Vec3(kwargs.get("scale"))

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
        self.trail_ready: bool = False

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

        self.percent_radius: int = round(
            (
                (self.scale_x - bg_vars.min_radius)
                / (bg_vars.max_radius - bg_vars.min_radius)
            )
            * 100
        )

        self.is_moon = self.scale_x < bg_vars.min_radius

        if self.is_moon:
            self.text_scale = urs.Vec3(0.08, 0.08, 0.08)
            self.percent_radius = round(
                (
                    (self.scale_x - bg_vars.min_moon_radius)
                    / (bg_vars.max_moon_radius - bg_vars.min_moon_radius)
                )
                * 100
            )

        self.all_text_on: bool = False
        self.planet_text_only: bool = False
        self.text_on: bool = False
        self.text_full_details: bool = True

        self.barycenter_blob: Rotator = None

    def set_orbital_pos_vel(self: Self, orbital: "BlobSurfaceUrsina") -> urs.Vec3:
        """Sets orbital to a position and velocity appropriate for an orbital of this blob"""

        self.rotate((0, (random.random() * 360.00), 0))
        orbital.ursina_blob.world_rotation = self.world_rotation
        orbital.ursina_blob.rotation_pos = self.rotation_pos
        orbital.rotation_pos = self.rotation_pos

        orbit_distance: float = (
            random.random() * (self.scale_x * 10)
        ) + self.scale_x * 3
        move: urs.Vec3 = urs.Vec3(self.left.normalized() * orbit_distance)

        orbital.ursina_blob.position = urs.Vec3(self.position + move)
        orbital.position = orbital.ursina_blob.position

        dx: float = (self.world_x - orbital.ursina_blob.world_x) * bg_vars.scale_up
        dy: float = (self.world_y - orbital.ursina_blob.world_y) * bg_vars.scale_up
        dz: float = (self.world_z - orbital.ursina_blob.world_z) * bg_vars.scale_up

        distance: float = math.sqrt(dx**2 + dy**2 + dz**2)

        vel: float = math.sqrt(G * self.mass / distance)

        orbital.ursina_blob.barycenter_blob = self

        return urs.Vec3(orbital.ursina_blob.forward.normalized() * vel)

    def create_trail(self: Self) -> None:
        """
        Creates the orbital trail. Called by input() when the "t" key is pressed if it
        is not running
        """
        self.trail = TrailRenderer(
            segments=250,
            min_spacing=bg_vars.max_radius,
            parent=self,
            color=self.trail_color,
            barycenter_blob=self.barycenter_blob,
            is_moon=self.is_moon,
        )

    def create_text_overlay(self: Self) -> None:
        """
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()
        """

        if self.text_entity is None:
            self.text_entity = urs.Entity(scale=self.scale)  # type: ignore

            self.text = self.short_overlay_text()

            if self.text_on and self.text_full_details:
                self.text = self.full_overlay_text()

            self.info_text = urs.Text(
                self.text,
                parent=self.text_entity,
                font=DISPLAY_FONT,
                size=(STAT_FONT_SIZE * 0.1),
                # resolution=(100 * (STAT_FONT_SIZE * 0.1)),
                origin=(0, -0.5),
                position=(0, 0, 0),
                scale=(0.1, 0.1, 0.1),
                color=urs.color.rgb32(255, 255, 255),
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

    def update_text_background(self: Self) -> None:
        """This is for when text changes, it will ensure the background size updates accordingly"""
        if self.info_text is not None:

            self.text = self.short_overlay_text()

            if self.text_on and self.text_full_details:
                self.text = self.full_overlay_text()

            self.info_text.text = self.text
            self.info_text.create_background(
                self.info_text.size * 0.5,
                self.info_text.size * 0.25,
                urs.color.rgb32(
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

    def full_overlay_text(self: Self) -> str:
        return f"{self.blob_name}: mass: {float(self.mass)} radius: {round(self.scale_x,2)} ({self.percent_radius}%) x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"

    def short_overlay_text(self: Self) -> str:
        return f"{self.blob_name}"

    def update(self: Self) -> None:
        """Called by Ursina engine once per frame"""

        if self.text_entity is not None and self.info_text.enabled:

            self.text = self.short_overlay_text()

            if self.text_on and self.text_full_details:
                self.text = self.full_overlay_text()

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

        if not FPS.paused:

            degrees = self.rotation_speed * (
                (ClockObject.getGlobalClock().getDt() * bg_vars.timescale) / HOURS
            )

            self.rotate((0, degrees, 0))

        if not self.trail_ready:
            from .blob_moon_trail_registry_ursina import (
                BlobMoonTrailRegistryUrsina as moon_registry,
            )

            self.trail_ready = moon_registry.is_ready()

    def on_click(self: Self) -> None:
        """
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused
        """
        self.text_on = not self.text_on

        if self.text_on:
            self.create_text_overlay()
        else:
            if not self.all_text_on:
                self.destroy_text_overlay()
            else:
                self.update_text_background()

    def input(self: Self, key: str) -> None:
        """Called by Ursina when a keyboard event happens"""
        if key == "b":
            self.all_text_on = not self.all_text_on

            if self.all_text_on:
                self.create_text_overlay()
            else:
                self.planet_text_only = False
                if not self.text_on:
                    self.destroy_text_overlay()
                else:
                    self.update_text_background()

        if key == "n" and self.is_moon:

            if self.all_text_on:

                self.planet_text_only = not self.planet_text_only

                if self.planet_text_only:

                    if not self.text_on:
                        self.destroy_text_overlay()
                    else:
                        self.update_text_background()
                else:

                    self.create_text_overlay()

        if key == "h":
            self.text_full_details = not self.text_full_details
            if self.all_text_on or self.text_on:
                self.update_text_background()

        if self.trail_ready and key == "t":
            if self.trail is not None:
                self.trail.enabled = False  # type: ignore
                urs.destroy(self.trail)
                self.trail = None

            elif self.trail is None:
                self.create_trail()

        if not self.blob_name == CENTER_BLOB_NAME and not self.is_moon and key == "y":

            if self.scale == self.radius:  # type: ignore
                self.scale = self.radius * 30
            else:
                self.scale = self.radius

        if not self.blob_name == CENTER_BLOB_NAME and self.is_moon and key == "u":

            if self.scale == self.radius:
                self.scale = self.radius * 5
            else:
                self.scale = self.radius

    def on_disable(self: Self) -> None:
        """
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay
        """
        self.destroy_text_overlay()

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""

        from .blob_moon_trail_registry_ursina import (
            BlobMoonTrailRegistryUrsina as moon_registry,
        )

        if self.trail is not None:
            urs.destroy(self.trail)

        if self.is_moon:
            self.barycenter_blob = None
            moon_registry.remove_moon(self)
        else:
            moon_registry.remove_planet(self)

        self.destroy_text_overlay()

        self.enabled = False


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
        Called when getting rid of this instance, so it can clean up

    destroy() -> None
        Called when getting rid of this instance, so it can clean up
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
    center_blob: urs.Vec3 = urs.Vec3(0, 0, 0)

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
        self.color: Tuple[int, int, int] = color
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.texture: str = texture
        self.rotation_speed: float = None
        self.rotation_pos: Tuple[float, float, float] = None
        self.position: Tuple[float, float, float] = (0, 0, 0)

        self.trail_color: urs.Color = urs.color.rgb32(25, 100, 150)

        urs_color = urs.color.rgb32(self.color[0], self.color[1], self.color[2])

        if bg_vars.textures_3d:

            if self.texture is None:

                halfway_max_halfway: float = (
                    ((bg_vars.min_radius + bg_vars.max_radius) / 2) + bg_vars.max_radius
                ) / 2

                if self.radius >= (halfway_max_halfway):
                    self.texture = BLOB_TEXTURES_LARGE[
                        random.randint(1, len(BLOB_TEXTURES_LARGE) - 1)
                    ]
                else:
                    self.texture = BLOB_TEXTURES_SMALL[
                        random.randint(1, len(BLOB_TEXTURES_SMALL) - 1)
                    ]

        if rotation_speed is not None:
            self.rotation_speed = rotation_speed
        if rotation_pos is not None:
            self.rotation_pos = rotation_pos

        self.ursina_center_blob: BlobPointLight = None
        self.ursina_blob: Rotator = None

        if color == CENTER_BLOB_COLOR:

            urs_color = urs.color.rgb32(150, 150, 150)

            enabled: bool = not bg_vars.black_hole_mode
            self.texture = "textures/sun03.png"

            if not enabled:
                urs_color = urs.color.rgba(0, 0, 0, 0)

            if not bg_vars.textures_3d:
                urs_color = urs.color.rgb32(
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
                shadows=True,
                scale=(self.radius, self.radius, self.radius),
                position=(0, 0, 0),
                shadow_map_resolution=(2048, 2048),
                max_distance=bg_vars.universe_size * 1000,
                attenuation=(1, 0, 0),
                color=urs.color.rgba(5, 5, 5, 5),
            )
        else:

            if not bg_vars.textures_3d:
                self.texture = None
            else:
                urs_color = urs.color.rgb32(255, 255, 255)

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

        BlobSurfaceUrsina.center_blob.x = x
        BlobSurfaceUrsina.center_blob.y = y
        BlobSurfaceUrsina.center_blob.z = z

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects
        """

        self.position = pos
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

        self.position = pos
        self.ursina_center_blob.position = urs.Vec3(pos)
        self.ursina_blob.position = urs.Vec3(pos)

    def on_destroy(self: Self) -> None:
        """Called when getting rid of this instance, so it can clean up"""
        self.destroy()

    def destroy(self: Self) -> None:
        """Called when getting rid of this instance, so it can clean up"""

        if self.ursina_center_blob is not None:
            # self.ursina_center_blob.color = (0, 0, 0, 0)
            self.ursina_center_blob.destroy()
            urs.destroy(self.ursina_center_blob)
            self.ursina_center_blob = None

        urs.destroy(self.ursina_blob)
        self.ursina_blob = None
