"""
Newton's Laws, a simulator of physics at the scale of space

An Entity (Ursina) class that holds the first person view, 
position and rotation control via keyboard and mouse

by Jason Mott, copyright 2024
"""

from pathlib import Path
from typing import Callable, Self

from panda3d.core import Vec3 as PanVec3  # type: ignore
from panda3d.core import AmbientLight as PandaAmbientLight  # type: ignore
from panda3d.core import NodePath  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars

from .blob_surface_ursina import BlobSurfaceUrsina
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_utils_ursina import TempMessage

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
        Recommended for this class: scale and eternal, Specific to this class: start_y and universe

    Methods
    -------
    setup_lock() -> None
        Locks the mouse position while setup completes, because it
        tends to wonder otherwise and corrupts the starting position

    start_following(follow_entity: urs.Entity) -> None
        Point gimbal arrow to follow_entity rather than center blob

    stop_following() -> None
        Point gimbal arrow to the center blob, rather than the assigned entity
        from start_following()

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

    my_forward() -> PanVec3
        get the first person forward direction

    def my_back() -> PanVec3
        get the first person backwards direction

    my_right() -> PanVec3
        get the first person right direction

    my_left() -> PanVec3
        get the first person left direction

    my_up() -> PanVec3
        get the first person up direction

    my_down() -> PanVec3
        get the first person down direction

    on_enable() -> None
        Called by Ursina when this Entity is enabled

    on_disable() -> None
        Called by Ursina when this Entity is disabled

    """

    def __init__(self: Self, **kwargs):

        self.temp_scale: float = kwargs["scale"]
        self.start_y: float = kwargs["start_y"]
        self.flashlight_color: urs.Vec3 = urs.color.rgba(0.3, 0.3, 0.3, 0.3)
        if not bg_vars.textures_3d:
            self.flashlight_color = urs.color.rgba(0.7, 0.7, 0.7, 0.3)
        self.mass: float = None
        self.universe: BlobUniverseUrsina = kwargs["universe"]
        self.base_dir: Path = urs.application.asset_folder

        super().__init__()

        urs.camera.parent = self
        urs.camera.position = PanVec3.forward() * -0.25
        urs.camera.rotation = (0, 0, 0)
        urs.camera.ui.collider = "sphere"
        urs.camera.ui.position = (0, 0, 0)

        color: urs.Color = urs.color.rgba(1, 1, 1, 0.59)
        self.gimbal_texture: str = "textures/suns/sun03.png"
        if not bg_vars.textures_3d:
            color = urs.color.rgba32(
                CENTER_BLOB_COLOR[0], CENTER_BLOB_COLOR[1], CENTER_BLOB_COLOR[2], 150
            )
            self.gimbal_texture = None
        self.gimbal: urs.Entity = urs.Entity(
            parent=self,
            color=color,
            position=(PanVec3.up() * -0.05),
            scale=(
                0.008,
                0.008,
                0.008,
            ),
            texture=self.gimbal_texture,
            # texture_scale=(1, 1),
            unlit=True,
            shader=shd.unlit_shader,
            eternal=kwargs["eternal"],
        )

        self.gimbal.model = urs.application.base.loader.loadModel(
            self.base_dir.joinpath("models").joinpath("blend_uvsphere.obj")
        )

        self.gimbal_arrow: urs.Entity = urs.Entity(
            parent=self.gimbal,
            model="arrow",
            color=urs.color.rgb32(179, 0, 27),
            scale=(1.9, 4, 2),
            position=(PanVec3.forward() * 0.95),
            unlit=True,
            shader=shd.unlit_shader,
            eternal=kwargs["eternal"],
        )

        self.gimbal_arrow.setHpr(self.gimbal_arrow, (90, 0, 0))

        self.gimbal_ring: urs.Entity = None

        self.gimbal_look_at: urs.Entity = urs.Entity(
            scale=urs.Vec3(self.temp_scale * 0.005),
            world_position=self.gimbal.world_position,
            eternal=kwargs["eternal"],
            unlit=True,
            shader=shd.unlit_shader,
        )

        self.ambient_light: PandaAmbientLight = PandaAmbientLight(
            f"ambient_light_universe"
        )
        self.ambient_light.setColor(self.flashlight_color)
        self.flashlight: urs.Entity = urs.Entity(
            parent=self.gimbal,
            position=(0, 0, 0),
            color=self.flashlight_color,
            eternal=kwargs["eternal"],
        )
        self.ambient_light_node: NodePath = self.flashlight.attachNewNode(
            self.ambient_light
        )
        urs.scene.setLight(self.ambient_light_node)

        self.orig_speed: float = bg_vars.au_scale_factor / 4
        self.min_speed: float = self.orig_speed * 0.05
        self.max_speed: float = self.orig_speed * 5

        self.orig_speed = (self.min_speed + self.max_speed) / 2
        self.speed: float = self.orig_speed
        self.speed_inc: float = self.max_speed / 50

        # self.orig_roll_speed: float = self.roll_speed
        self.min_roll_speed: float = 20
        self.max_roll_speed: float = 90

        self.orig_roll_speed: float = (self.min_roll_speed + self.max_roll_speed) / 2
        self.roll_speed: float = self.orig_roll_speed
        self.roll_speed_inc: float = self.max_roll_speed / 50

        self.direction: urs.Vec3 = None
        self.position: urs.Vec3 = urs.Vec3(PanVec3.forward() * self.start_y)
        self.velocity: urs.Vec3 = urs.Vec3(0, 0, 0)
        self.world_position: urs.Vec3 = urs.Vec3(PanVec3.forward() * self.start_y)
        self.local_disabled: bool = False
        self.flashlight_on: bool = True
        self.temp_message: TempMessage = None

        urs.mouse.locked = True
        self.mouse_sensitivity: urs.Vec3 = urs.Vec2(35, 35)
        self.scroll_speed: float = 0
        self.mouse_scroll_up: int = 0
        self.mouse_scroll_down: int = 0

        self.follow_entity: urs.Entity = None
        self.follow_entity_last_pos: urs.Vec3 = None

        self.hud = True

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

        self.setup_stage: bool = True

        self.center_cursor: urs.Entity = urs.Entity(
            parent=self,
            model="pan_quad",
            color=urs.color.rgb32(179, 0, 27),
            scale=urs.Vec3(0.003, 0.003, 0.003),
            eternal=kwargs["eternal"],
            shader=shd.unlit_shader,
        )
        self.center_cursor.setHpr(urs.scene, (0, 0, 45))

        lens = urs.camera.lens
        universe = bg_vars.universe_size / 2
        lens.setFar(universe / bg_vars.first_person_scale)
        lens.setFilmSize(urs.window.size[0], urs.window.size[1])

    def setup_lock(self: Self) -> None:
        """
        Locks the mouse position while setup completes, because it
        tends to wonder otherwise and corrupts the starting position
        """
        self.setup_stage = True
        self.pos_lock()

    def start_following(self: Self, follow_entity: urs.Entity) -> None:
        """Point gimbal arrow to follow_entity rather than center blob"""
        self.follow_entity = follow_entity
        self.follow_entity_last_pos = self.follow_entity.position
        if (
            hasattr(self.follow_entity, "texture_name")
            and self.follow_entity.texture_name is not None
        ):
            self.gimbal.texture = self.follow_entity.texture_name
        else:
            self.gimbal.texture = self.gimbal_texture

        if (
            hasattr(self.follow_entity, "planet_ring")
            and self.follow_entity.planet_ring is not None
        ):
            self.gimbal_ring = urs.Entity(
                parent=self.gimbal,
                scale=self.follow_entity.planet_ring.getScale(),
                color=self.gimbal.color,
                texture=self.follow_entity.ring_texture,
                unlit=True,
                shader=shd.unlit_shader,
            )
            self.gimbal_ring.model = urs.application.base.loader.loadModel(
                self.base_dir.joinpath("models").joinpath("rings.obj")
            )

    def stop_following(self: Self) -> None:
        """
        Point gimbal arrow to the center blob, rather than the assigned entity
        from start_following()
        """
        self.follow_entity = None
        self.follow_entity_last_pos = None
        self.gimbal.texture = self.gimbal_texture
        if self.gimbal_ring is not None:
            self.gimbal_ring.disable()
            urs.destroy(self.gimbal_ring)
            self.gimbal_ring = None

    def update(self: Self) -> None:
        """Called by Ursina engine once per frame"""

        if self.setup_stage and self.local_disabled:
            self.pos_unlock()
            self.setup_stage = False

        if urs.mouse.locked:
            self.rotate((0, urs.mouse.velocity[0] * self.mouse_sensitivity[1], 0))

            self.rotate((-(urs.mouse.velocity[1] * self.mouse_sensitivity[0]), 0, 0))

            thrust: int = self.mouse_scroll_up - self.mouse_scroll_down

            if thrust != 0:

                self.speed += self.speed_inc * thrust
                self.roll_speed += self.roll_speed_inc * thrust

                self.speed = urs.clamp(
                    self.speed,
                    self.min_speed,
                    self.max_speed,
                )

                self.roll_speed = urs.clamp(
                    self.roll_speed,
                    self.min_roll_speed,
                    self.max_roll_speed,
                )

                self.report_throttle_speed()

            self.rotate(
                urs.Vec3(0, 0, (urs.held_keys["z"] - urs.held_keys["c"]))
                * urs.time.dt
                * self.roll_speed
            )

            self.mouse_scroll_up = 0
            self.mouse_scroll_down = 0

            if self.follow_entity is not None:
                self.position += (
                    self.follow_entity.position - self.follow_entity_last_pos
                )
                self.follow_entity_last_pos = self.follow_entity.position

            self.direction = urs.Vec3(
                self.my_forward * (urs.held_keys["w"] - urs.held_keys["s"])
                + self.my_right * (urs.held_keys["d"] - urs.held_keys["a"])
                + self.my_up * (urs.held_keys["e"] - urs.held_keys["x"])
            ).normalized()

            self.velocity = self.direction * urs.time.dt * self.speed

            self.position += self.velocity

        if self.follow_entity is not None:
            self.gimbal_look_at.world_position = self.gimbal.world_position
            self.gimbal_look_at.world_rotation = self.world_rotation

            self.gimbal_look_at.look_at(self.follow_entity, up=self.my_up)
        elif BlobSurfaceUrsina.center_blob is not None:
            self.gimbal_look_at.world_position = self.gimbal.world_position
            self.gimbal_look_at.world_rotation = self.world_rotation

            self.gimbal_look_at.look_at(BlobSurfaceUrsina.center_blob, up=self.my_up)

        self.gimbal.world_rotation = self.gimbal_look_at.world_rotation

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
                self.ambient_light.setColor((0, 0, 0, 0.3))
                self.flashlight_on = False
            else:
                self.ambient_light.setColor(self.flashlight_color)
                self.flashlight_on = True

        if key == "r":
            self.speed = self.orig_speed
            self.roll_speed = self.orig_roll_speed
            self.report_throttle_speed()

        if key == "g":
            self.hud = not self.hud

            if self.hud:
                self.gimbal_arrow.enabled = True
                self.gimbal.enabled = True
                self.center_cursor.enabled = True
            else:
                self.gimbal_arrow.enabled = False
                self.gimbal.enabled = False
                self.center_cursor.enabled = False

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
                    urs.window.size[0] / 2,
                    0,
                    urs.window.size[1] * 0.25,
                ),
            )
        else:
            self.temp_message.set_text(
                f"Throttle speed: {round(self.speed)}",
                (
                    urs.window.size[0] / 2,
                    0,
                    urs.window.size[1] * 0.25,
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

    @property
    def my_forward(self: Self) -> PanVec3:
        """get the first person forward direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.forward()))

    @property
    def my_back(self: Self) -> PanVec3:
        """get the first person backwards direction"""
        return -self.my_forward

    @property
    def my_right(self: Self) -> PanVec3:
        """get the first person right direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.right()))

    @property
    def my_left(self: Self) -> PanVec3:
        """get the first person left direction"""
        return -self.my_right

    @property
    def my_up(self: Self) -> PanVec3:
        """get the first person up direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.up()))

    @property
    def my_down(self: Self) -> PanVec3:
        """get the first person down direction"""
        return -self.my_up

    def on_enable(self: Self) -> None:
        """Called by Ursina when this Entity is enabled"""
        urs.mouse.locked = True
        if hasattr(self, "_mouse_position"):
            urs.mouse.position = self._mouse_position
        urs.mouse.enabled = True

        if hasattr(self, "_original_camera_transform"):
            # urs.camera.parent = self
            urs.camera.transform = self._original_camera_transform

    def on_disable(self: Self) -> None:
        """Called by Ursina when this Entity is disabled"""

        urs.mouse.locked = False
        self._mouse_position = urs.mouse.position
        urs.mouse.enabled = False
        # store original position and rotation
        self._original_camera_transform = urs.camera.transform
        # urs.camera.world_parent = urs.scene

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""

        self.on_disable()

        urs.scene.clearLight(self.ambient_light_node)
