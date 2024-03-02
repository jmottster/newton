from typing import Self

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from .blob_surface_ursina import BlobSurfaceUrsina
from newtons_blobs.globals import *
from newtons_blobs import relative_resource_path_str
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import BLOB_TEXTURES_SMALL


class BlobFirstPersonUrsina(urs.Entity):

    def __init__(self: Self, **kwargs):

        self.temp_scale = kwargs["scale"]
        self.start_z = kwargs["start_z"]
        self.flashlight_color = urs.color.rgb(0.175, 0.175, 0.175, 0.3)
        self.mass = None
        self.universe: BlobUniverseUrsina = kwargs["universe"]

        self.center_cursor = urs.Entity(
            parent=urs.camera.ui,
            model="quad",
            color=urs.color.rgb(179, 0, 27),
            scale=(0.008, 0.008, 0.008),
            position=(0, 0, 2),
            rotation_z=45,
            eternal=kwargs["eternal"],
        )

        self.gimbal = urs.Entity(
            model="sphere",
            color=urs.color.rgb(200, 200, 200, 150),
            position=(0, 0, self.start_z),
            scale=(
                self.temp_scale * 0.025,
                self.temp_scale * 0.025,
                self.temp_scale * 0.025,
            ),
            texture=relative_resource_path_str("nb_ursina/textures/sun03.png", ""),
            texture_scale=(1, 1),
            shader=shd.unlit_shader,
            eternal=kwargs["eternal"],
        )

        self.gimbal_arrow = urs.Entity(
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

        self.flashlight = urs.AmbientLight(
            parent=self.gimbal,
            position=(0, 0, 0),
            shadows=False,
            shadow_map_resolution=(4096, 4096),
            max_distance=500,
            attenuation=(1, 0, 0),
            color=self.flashlight_color,
            eternal=kwargs["eternal"],
        )

        super().__init__()

        self.center_blob = urs.Vec3(
            BlobSurfaceUrsina.center_blob_x,
            BlobSurfaceUrsina.center_blob_y,
            BlobSurfaceUrsina.center_blob_z,
        )

        urs.camera.parent = self
        urs.camera.position = (0, 0, 0)
        urs.camera.rotation = (0, 0, 0)
        # urs.camera.fov = 90
        urs.camera.ui.collider = "sphere"
        urs.camera.ui.on_click = self.on_mouse1_click

        self.speed = 5
        self.roll_speed = 1.5
        self.position = urs.Vec3(0, 0, self.start_z)
        self.velocity = urs.Vec3(0, 0, 0)
        self.world_position = urs.Vec3(0, 0, self.start_z)
        self.local_disabled = False
        self.flashlight_on = True

        urs.mouse.traverse_target = None
        urs.mouse.locked = True
        self.mouse_sensitivity = urs.Vec2(35, 35)
        self.scroll_smoothness = 6
        self.scroll_speed = 0
        self.mouse_scroll_up = 0
        self.mouse_scroll_down = 0

        self.on_destroy = self.on_disable

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

        self.speed *= self.temp_scale * 3
        self.roll_speed *= self.temp_scale * 3
        self.scroll_smoothness *= self.temp_scale * 3

        # self.cam_pos = urs.Text(
        #     f"({self.x},{self.y},{self.z})",
        #     position=(0, 0.03, 0),
        #     parent=urs.camera.ui,
        #     origin=(0, 0),
        #     scale=0.75,
        # )

    def update(self):

        if urs.mouse.locked:
            self.rotate((0, urs.mouse.velocity[0] * self.mouse_sensitivity[1], 0))

            self.rotate((-(urs.mouse.velocity[1] * self.mouse_sensitivity[0]), 0, 0))

            self.rotate(
                urs.Vec3(0, 0, (urs.held_keys["z"] - urs.held_keys["c"]))
                * urs.time.dt
                * self.roll_speed
            )

            thrust = self.mouse_scroll_up - self.mouse_scroll_down

            self.scroll_speed += thrust * self.scroll_smoothness

            self.m_direction = urs.Vec3(self.up * self.scroll_speed).normalized()

            if self.scroll_speed > -(
                self.scroll_smoothness / 4
            ) and self.scroll_speed < (self.scroll_smoothness / 4):
                self.scroll_speed = 0

            elif self.scroll_speed < 0:
                self.scroll_speed = urs.clamp(
                    self.scroll_speed,
                    -(self.scroll_smoothness),
                    -(self.scroll_smoothness / 4),
                )

            elif self.scroll_speed > 0:
                self.scroll_speed = urs.clamp(
                    self.scroll_speed,
                    self.scroll_smoothness / 4,
                    self.scroll_smoothness,
                )

            self.velocity = self.m_direction * urs.time.dt * abs(self.scroll_speed)

            self.scroll_speed *= 0.95

            self.mouse_scroll_up = 0
            self.mouse_scroll_down = 0

            self.direction = urs.Vec3(
                self.forward * (urs.held_keys["w"] - urs.held_keys["s"])
                + self.right * (urs.held_keys["d"] - urs.held_keys["a"])
                + self.up * (urs.held_keys["e"] - urs.held_keys["x"])
            ).normalized()

            self.velocity += self.direction * urs.time.dt * self.speed

            self.position += self.velocity

            self.center_blob = urs.Vec3(
                BlobSurfaceUrsina.center_blob_x,
                BlobSurfaceUrsina.center_blob_y,
                BlobSurfaceUrsina.center_blob_z,
            )

            self.gimbal.rotation = self.rotation
            self.gimbal.position = self.position + (self.forward / 2)
            self.gimbal.position += self.gimbal.down * 4
            self.gimbal.look_at(self.center_blob)

            self.universe.universe.position = self.world_position

            # self.cam_pos.text = f"({round(self.world_position[0],2)}, {round(self.world_position[1],2)}, {round(self.world_position[2],2)})"

    def input(self, key):

        if key == "q":
            if self.local_disabled:
                self.on_enable()
                self.local_disabled = False
            else:
                self.on_disable()
                self.local_disabled = True

        if key == "v":

            if self.flashlight_on:
                self.flashlight.color = (0, 0, 0, 0.3)
                self.flashlight_on = False
            else:
                self.flashlight.color = self.flashlight_color
                self.flashlight_on = True

        # print(key)
        if key == "scroll up":
            self.mouse_scroll_up = 1
        if key == "scroll down":
            self.mouse_scroll_down = 1

    def on_mouse1_click(self):
        print(f"click")

    def on_enable(self):
        urs.mouse.locked = True
        self.gimbal_arrow.enabled = True
        self.gimbal.enabled = True
        self.center_cursor.enabled = True
        if hasattr(self, "_mouse_position"):
            urs.mouse.position = self._mouse_position
        urs.mouse.enabled = True

        if hasattr(self, "_original_camera_transform"):
            urs.camera.parent = self
            urs.camera.transform = self._original_camera_transform

    def on_disable(self):
        urs.mouse.locked = False
        self.gimbal_arrow.enabled = False
        self.gimbal.enabled = False
        self.center_cursor.enabled = False
        self._mouse_position = urs.mouse.position
        urs.mouse.enabled = False
        self._original_camera_transform = (
            urs.camera.transform
        )  # store original position and rotation
        urs.camera.world_parent = urs.scene
