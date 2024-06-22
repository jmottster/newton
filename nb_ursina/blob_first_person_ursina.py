"""
Newton's Laws, a simulator of physics at the scale of space

An Entity (Ursina) class that holds the first person view, 
position and rotation control via keyboard and mouse

by Jason Mott, copyright 2024
"""

from typing import Callable, Self

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs import resource_path

from .blob_surface_ursina import BlobSurfaceUrsina
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import BLOB_TEXTURES_SMALL
from .blob_utils_ursina import TempMessage
from .blob_lights import BlobAmbientLight

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobFirstPersonUrsina(urs.Entity):
    """
    An Entity (Ursina) class that holds the first person view,
    position and rotation control via keyboard and mouse

    Attributes
    ----------
    **kwargs
        Recommended for this class: scale and eternal, Specific to this class: start_z and universe

    Methods
    -------
    setup_lock() -> None
        Locks the mouse position while setup completes, because it
        tends to wonder otherwise and corrupts the starting position

    update() -> None
        Called by Ursina engine once per frame

    input(key: str) -> None
        Called by Ursina when a keyboard event happens

    report_throttle_speed() -> None
        Called from update when throttle speed changes, will print a temporary message
        on screen reporting the current throttle speed

    on_mouse1_click() -> None
        Called when the mouse1 button is clicked

    pos_lock() -> None
        Calls on_disable(), which will unlock the mouse from the camera, lock the position
        by saving it

    pos_unlock() -> None
        Calls on_enable(), which will lock the mouse to the camera, unlock the position hold,
        and restore any saved positions

    on_enable() -> None
        Called by Ursina when this Entity is enabled

    on_disable() -> None
        Called by Ursina when this Entity is disabled

    """

    def __init__(self: Self, **kwargs):

        self.temp_scale: float = kwargs["scale"]
        self.start_z: float = kwargs["start_z"]
        self.flashlight_color: urs.Vec3 = urs.color.rgba(0.3, 0.3, 0.3, 0.3)
        if not bg_vars.textures_3d:
            self.flashlight_color = urs.color.rgba(0.7, 0.7, 0.7, 0.3)
        self.mass: float = None
        self.universe: BlobUniverseUrsina = kwargs["universe"]

        self.center_cursor: urs.Entity = urs.Entity(
            parent=urs.camera.ui,
            model="quad",
            color=urs.color.rgb(179, 0, 27),
            scale=(0.008, 0.008, 0.008),
            position=(0, 0, 2),
            rotation_z=45,
            eternal=kwargs["eternal"],
        )

        color: urs.Color = urs.color.rgba(200, 200, 200, 150)
        self.gimbal_texture: str = "nb_ursina/textures/sun03.png"
        if not bg_vars.textures_3d:
            color = urs.rgba(
                CENTER_BLOB_COLOR[0], CENTER_BLOB_COLOR[1], CENTER_BLOB_COLOR[2], 150
            )
            self.gimbal_texture = None
        self.gimbal: urs.Entity = urs.Entity(
            model="sphere",
            color=color,
            position=(0, 0, self.start_z),
            scale=(
                self.temp_scale * 0.005,
                self.temp_scale * 0.005,
                self.temp_scale * 0.005,
            ),
            texture=self.gimbal_texture,
            texture_scale=(1, 1, 1),
            shader=shd.unlit_shader,
            eternal=kwargs["eternal"],
        )

        self.gimbal_arrow: urs.Entity = urs.Entity(
            parent=self.gimbal,
            model="arrow",
            color=urs.rgb(179, 0, 27),
            scale=(1, 3, 1.75),
            position=(0, 0, 0.5),
            rotation_x=90,
            rotation_y=0,
            rotation_z=-90,
            shader=shd.unlit_shader,
            eternal=kwargs["eternal"],
        )

        self.flashlight: BlobAmbientLight = BlobAmbientLight(
            parent=self.gimbal,
            position=(0, 0, 0),
            shadows=False,
            shadow_map_resolution=(4096, 4096),
            max_distance=bg_vars.universe_size,
            attenuation=(1, 0, 0),
            color=self.flashlight_color,
            eternal=kwargs["eternal"],
        )

        super().__init__()

        self.center_blob: urs.Vec3 = urs.Vec3(
            BlobSurfaceUrsina.center_blob_x,
            BlobSurfaceUrsina.center_blob_y,
            BlobSurfaceUrsina.center_blob_z,
        )

        urs.camera.parent = self
        urs.camera.position = (0, 0, 0)
        urs.camera.rotation = (0, 0, 0)
        urs.camera.ui.collider = "sphere"
        urs.camera.ui.position = (0, 0, 0)

        self.speed: float = bg_vars.au_scale_factor / 4
        self.orig_speed: float = self.speed
        self.roll_speed: float = 20
        self.orig_roll_speed: float = self.roll_speed
        self.direction: urs.Vec3 = None
        # self.m_direction: urs.Vec3 = None
        self.position: urs.Vec3 = urs.Vec3(0, 0, self.start_z)
        self.velocity: urs.Vec3 = urs.Vec3(0, 0, 0)
        self.world_position: urs.Vec3 = urs.Vec3(0, 0, self.start_z)
        self.local_disabled: bool = False
        self.flashlight_on: bool = True
        self.temp_message: TempMessage = None

        urs.mouse.locked = True
        self.mouse_sensitivity: urs.Vec3 = urs.Vec2(35, 35)
        self.scroll_speed: float = 0
        self.mouse_scroll_up: int = 0
        self.mouse_scroll_down: int = 0

        self.on_destroy: Callable[[], None] = self.on_disable

        self.follow_entity: urs.Entity = None
        self.follow_entity_last_pos: urs.Vec3 = None

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

        self.gimbal_relative_forward_pos = self.scale_x * 0.103
        self.gimbal_relative_down_pos = self.scale_x * 0.02

        self.speed_inc = self.orig_speed * 0.04

        self.setup_stage = True

    def setup_lock(self: Self) -> None:
        """
        Locks the mouse position while setup completes, because it
        tends to wonder otherwise and corrupts the starting position
        """
        self.setup_stage = True
        self.pos_lock()

    def start_following(self: Self, follow_entity: urs.Entity) -> None:
        self.follow_entity = follow_entity
        self.follow_entity_last_pos = self.follow_entity.position
        self.gimbal.texture = self.follow_entity.texture

    def stop_following(self: Self) -> None:
        self.follow_entity = None
        self.follow_entity_last_pos = None
        self.gimbal.texture = self.gimbal_texture

    def update(self: Self) -> None:
        """Called by Ursina engine once per frame"""

        if self.setup_stage and self.local_disabled:
            self.pos_unlock()
            self.setup_stage = False

        if urs.mouse.locked:
            self.rotate((0, urs.mouse.velocity[0] * self.mouse_sensitivity[1], 0))

            self.rotate((-(urs.mouse.velocity[1] * self.mouse_sensitivity[0]), 0, 0))

            self.rotate(
                urs.Vec3(0, 0, (urs.held_keys["z"] - urs.held_keys["c"]))
                * urs.time.dt
                * self.roll_speed
            )

            thrust: int = self.mouse_scroll_up - self.mouse_scroll_down

            if thrust != 0:

                self.speed += self.speed_inc * thrust
                self.roll_speed += 5 * thrust

                self.speed = urs.clamp(
                    self.speed,
                    self.orig_speed * 0.10,
                    self.orig_speed * 2.5,
                )

                self.roll_speed = urs.clamp(
                    self.roll_speed,
                    5,
                    self.orig_roll_speed * 2.5,
                )

                self.report_throttle_speed()

            self.mouse_scroll_up = 0
            self.mouse_scroll_down = 0

            if self.follow_entity is not None:
                diff: urs.Vec3 = (
                    self.follow_entity.position - self.follow_entity_last_pos
                )
                self.position += diff
                self.follow_entity_last_pos = self.follow_entity.position

            self.direction = urs.Vec3(
                self.forward * (urs.held_keys["w"] - urs.held_keys["s"])
                + self.right * (urs.held_keys["d"] - urs.held_keys["a"])
                + self.up * (urs.held_keys["e"] - urs.held_keys["x"])
            ).normalized()

            self.velocity = self.direction * urs.time.dt * self.speed

            self.position += self.velocity

            self.center_blob = urs.Vec3(
                BlobSurfaceUrsina.center_blob_x,
                BlobSurfaceUrsina.center_blob_y,
                BlobSurfaceUrsina.center_blob_z,
            )

            self.gimbal.rotation = self.rotation
            self.gimbal.position = (
                self.position
                + self.forward.normalized() * self.gimbal_relative_forward_pos
            )
            self.gimbal.position += (
                self.gimbal.down.normalized() * self.gimbal_relative_down_pos
            )

            if self.follow_entity is not None:
                self.gimbal.look_at(self.follow_entity)
            else:
                self.gimbal.look_at(self.center_blob)

            self.universe.universe.position = self.world_position

    def input(self: Self, key: str) -> None:
        """Called by Ursina when a keyboard event happens"""

        if key == "q":
            if self.local_disabled:
                self.pos_unlock()
            else:
                self.pos_lock()

        if key == "v":

            if self.flashlight_on:
                self.flashlight.color = (0, 0, 0, 0.3)
                self.flashlight_on = False
            else:
                self.flashlight.color = self.flashlight_color
                self.flashlight_on = True

        if key == "r":
            self.speed = self.orig_speed
            self.roll_speed = self.orig_roll_speed
            self.report_throttle_speed()

        if key == "scroll up":
            self.mouse_scroll_up = 1
        if key == "scroll down":
            self.mouse_scroll_down = 1

        if key == "space":
            if urs.camera.ui.collider is None:
                urs.camera.ui.collider = "sphere"
            else:
                urs.camera.ui.collider = None

    def report_throttle_speed(self: Self) -> None:
        """
        Called from update when throttle speed changes, will print a temporary message
        on screen reporting the current throttle speed
        """
        if self.temp_message is None:

            self.temp_message = TempMessage(
                text=f"Throttle speed: {round(self.speed)}",
                pos=(
                    (urs.window.size[0] / 2),
                    (urs.window.size[1] * 0.75),
                ),
            )
        else:
            self.temp_message.set_text(
                f"Throttle speed: {round(self.speed)}",
                (
                    (urs.window.size[0] / 2),
                    (urs.window.size[1] * 0.75),
                ),
            )
            self.temp_message.reset_counter()

    def on_mouse1_click(self: Self) -> None:
        """on_mouse1_click(self: Self) -> None"""
        print(f"click")

    def pos_lock(self: Self) -> None:
        """
        Calls on_disable(), which will unlock the mouse from the camera, lock the position
        by saving it
        """
        self.on_disable()
        self.local_disabled = True

    def pos_unlock(self: Self) -> None:
        """
        Calls on_enable(), which will lock the mouse to the camera, unlock the position hold,
        and restore any saved positions
        """
        self.on_enable()
        self.local_disabled = False

    def on_enable(self: Self) -> None:
        """Called by Ursina when this Entity is enabled"""
        urs.mouse.locked = True
        self.gimbal_arrow.enabled = True
        self.gimbal.enabled = True
        self.center_cursor.enabled = True
        if hasattr(self, "_mouse_position"):
            urs.mouse.position = self._mouse_position
        urs.mouse.enabled = True

        if hasattr(self, "_original_camera_transform"):
            # urs.camera.parent = self
            urs.camera.transform = self._original_camera_transform

    def on_disable(self: Self) -> None:
        """Called by Ursina when this Entity is disabled"""

        urs.mouse.locked = False
        self.gimbal_arrow.enabled = False
        self.gimbal.enabled = False
        self.center_cursor.enabled = False
        self._mouse_position = urs.mouse.position
        urs.mouse.enabled = False
        # store original position and rotation
        self._original_camera_transform = urs.camera.transform
        # urs.camera.world_parent = urs.scene
