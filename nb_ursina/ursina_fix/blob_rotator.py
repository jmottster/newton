"""
Newton's Laws, a simulator of physics at the scale of space

Class to create the base Ursina Entity for a blob (and helper classes)

by Jason Mott, copyright 2025
"""

from pathlib import Path
from typing import Self, Tuple, Protocol

from panda3d.core import Vec3 as PanVec3  # type: ignore
from panda3d.core import Vec4 as PanVec4  # type: ignore

from panda3d.core import (  # type: ignore
    NodePath,
    TransparencyAttrib,
    Material,
    Shader,
    BitMask32,
)  # type: ignore

import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs.blob_random import blob_random
from newtons_blobs import BlobGlobalVars as bg_vars

from nb_ursina.fps import FPS
from .blob_materials import PlanetMaterial

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class FollowerEntity(Protocol):

    @property
    def position(self: Self) -> urs.Vec3:
        pass

    @position.setter
    def position(self: Self, position: urs.Vec3) -> None:
        pass

    def stop_following(self: Self) -> None:
        pass


class BlobRotator(urs.Entity):
    """
    A class to create a blob Entity that rotates and can have rings

    Attributes
    ----------
    position: urs.Vec3
        Position of this blob relative to urs.scene

    scale: urs.Vec3
        The scale of this blob relative to urs.scene

    scale_x: float
        The scale of the x axis relative to urs.scene

    radius: float
        The blob's radius (equivalent to scale)

    world_rotation_x: float
        The x axis rotation in degrees relative to urs.scene

    world_rotation_y: float
        The y axis rotation in degrees relative to urs.scene

    world_rotation_z: float
        The z axis rotation in degrees relative to urs.scene

    rotation_speed: float
        The blob's speed of rotation in degrees per hour

    rotation_pos: Tuple[float,float,float]
        The x,y,z axis rotation positions in degrees relative to urs.scene
        Setting this is relative to urs.scene

    rotation: Tuple[float,float,float]
        The x,y,z axis rotation positions in degrees relative to urs.scene
        Setting this is relative to current self position

    follower_entity: BlobFirstPersonUrsina
        Setting ths makes the Entity use this BlobRotator as its inertial frame of
        reference. I.e., its position will be updated in such a way that this BlobRotator
        will maintain the same relative distance/position, still allowing it to move
        independently relative to this BlobRotator

    world_up: PanVec3
        The up direction relative to urs.scene

    my_forward: PanVec3
        the first person forward direction

    my_back: PanVec3
        the first person backwards direction

    my_right: PanVec3
        the first person right direction

    my_left: PanVec3
        the first person left direction

    my_up: PanVec3
        the first person up direction

    my_down: PanVec3
        the first person down direction



    Methods
    -------
    create_blob(texture_name: str = None) -> None
        Creates the blob model

    create_ring(ring_texture: str = None) -> None
        Creates the ring model

    update() -> None
        Called by Ursina once per frame

    on_destroy(self: Self) -> None
        Called by Ursina when this Entity is destroyed



    """

    # __slots__ = (
    #     "rotation_speed",
    #     "rotation_pos",
    # )

    def __init__(self: Self, **kwargs):

        self.rotator_model: NodePath = None
        self.planet_ring: NodePath = None
        self.blob_material: Material = kwargs.get("blob_material")
        self.base_dir: Path = urs.application.asset_folder
        self.default_color: urs.Color = urs.color.rgba32(1, 1, 1, 1)
        self._radius: float = None
        self.index: int = kwargs.get("index")
        self.blob_name: str = kwargs.get("blob_name")
        self._rotation_speed: float = None
        self._rotation_pos: Tuple[float, float, float] = None
        self._pos: urs.Vec3 = None
        self.texture_name: str = kwargs.get("texture_name")
        self.glow_map_name: str = kwargs.get("glow_map_name")
        self.ring_texture: str = kwargs.get("ring_texture")
        self.ring_scale: float = kwargs.get("ring_scale")
        self.center_light: NodePath = kwargs.get("center_light")
        self.color = kwargs.get("color")

        self._follower_entity: FollowerEntity = None
        self.follower_entity_last_pos: urs.Vec3 = None

        for key in (
            "model",
            "texture",
            "texture_scale",
            "texture_offset",
            "index",
            "blob_name",
            "texture_name",
            "glow_map_name",
            "ring_texture",
            "blob_material",
            "center_light",
            "color",
        ):
            if key in kwargs:
                del kwargs[key]

        super().__init__()

        for key in ("origin", "origin_x", "origin_y", "origin_z", "collider", "scale"):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]
        for key, value in kwargs.items():
            if kwargs[key] is not None:
                setattr(self, key, value)

        if self.texture_name is not None:
            self.create_blob()

    @property
    def position(self: Self) -> urs.Vec3:
        """Position of this blob relative to urs.scene"""
        return self._pos

    @position.setter
    def position(self: Self, pos: urs.Vec3) -> None:
        """Sets the position of this blob relative to urs.scene"""
        self._pos = urs.Vec3(pos)
        self.world_position = self._pos

        if self.rotator_model is not None:
            self.rotator_model.setPos(urs.scene, self._pos)
            if self.follower_entity is not None:
                follow_pos: urs.Vec3 = urs.Vec3(
                    self._pos - self.follower_entity_last_pos
                )
                self.follower_entity_last_pos = self._pos

                self.follower_entity.position += follow_pos

    @property
    def scale(self: Self) -> urs.Vec3:
        """The scale of this blob relative to urs.scene"""
        if self.rotator_model is not None:
            return urs.Vec3(self.rotator_model.getScale())
        else:
            return urs.Vec3(self.getScale())

    @scale.setter
    def scale(self: Self, scale: urs.Vec3) -> None:
        """Sets the scale of this blob relative to urs.scene"""
        # print(f"{self.blob_name} setting scale")
        if self.rotator_model is not None:
            self.rotator_model.setScale(urs.scene, scale)
        self.setScale(urs.scene, scale)

    @property
    def scale_x(self: Self) -> float:
        """The scale of the x axis relative to urs.scene"""
        scale_x = self.scale
        return scale_x[0]

    @property
    def radius(self: Self) -> float:
        """The blob's radius (equivalent to scale)"""
        return self._radius

    @radius.setter
    def radius(self: Self, radius: float) -> None:
        """Set the blob's radius (and scale)"""
        self._radius = radius
        self.scale = urs.Vec3(self._radius)

    @property
    def world_rotation_x(self: Self) -> float:
        """The x axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        return x

    @world_rotation_x.setter
    def world_rotation_x(self: Self, degrees: float) -> None:
        """Sets the x axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        self.rotation_pos = (degrees, y, z)

    @property
    def world_rotation_y(self: Self) -> float:
        """The y axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        return y

    @world_rotation_y.setter
    def world_rotation_y(self: Self, degrees: float) -> None:
        """Sets the y axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        self.rotation_pos = (x, degrees, z)

    @property
    def world_rotation_z(self: Self) -> float:
        """The z axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        return z

    @world_rotation_z.setter
    def world_rotation_z(self: Self, degrees: float) -> None:
        """Sets the z axis rotation in degrees relative to urs.scene"""
        x, y, z = self.rotation_pos
        self.rotation_pos = (x, y, degrees)

    @property
    def rotation_speed(self: Self) -> float:
        """The blob's speed of rotation in degrees per hour"""
        return self._rotation_speed

    @rotation_speed.setter
    def rotation_speed(self: Self, rotation_speed: float) -> None:
        """Sets the blob's speed of rotation in degrees per hour"""
        self._rotation_speed = rotation_speed

    @property
    def rotation_pos(self: Self) -> Tuple[float, float, float]:
        """The x,y,z axis rotation positions in degrees relative to urs.scene"""
        z, x, y = self.getHpr(urs.scene)
        return (x, y, z)

    @rotation_pos.setter
    def rotation_pos(self: Self, rotation: Tuple[float, float, float]) -> None:
        """Sets the x,y,z axis rotation positions in degrees relative to urs.scene"""
        x, y, z = rotation
        self.setHpr(urs.scene, (z, x, y))
        if self.rotator_model is not None:
            self.rotator_model.setHpr(urs.scene, self.getHpr(urs.scene))

    @property
    def rotate(self: Self) -> Tuple[float, float, float]:
        """The x,y,z axis rotation positions in degrees relative to urs.scene"""
        return self.rotation_pos

    @rotate.setter
    def rotate(self: Self, rotation: Tuple[float, float, float]) -> None:
        """The x,y,z axis rotation positions set relative to current self position"""
        x, y, z = rotation
        if self.rotator_model is not None:
            self.rotator_model.setHpr(self.rotator_model, (z, x, y))
            z, x, y = self.rotator_model.getHpr(urs.scene)
        else:
            self.setHpr(self, (z, x, y))
            z, x, y = self.getHpr(urs.scene)

        self.rotation_pos = (x, y, z)

    @property
    def follower_entity(self: Self) -> FollowerEntity:
        """Get this follower_entity property"""
        return self._follower_entity

    @follower_entity.setter
    def follower_entity(self: Self, follower_entity: FollowerEntity) -> None:
        """
        Setting ths makes the Entity use this BlobRotator as its inertial frame of
        reference. I.e., its position will be updated in such a way that this BlobRotator
        will maintain the same relative distance/position, still allowing it to move
        independently relative to this BlobRotator
        """
        self._follower_entity = follower_entity

        if follower_entity is None:
            self.follower_entity_last_pos = None
        else:
            self.follower_entity_last_pos = self.position

    @property
    def world_up(self) -> PanVec3:
        return PanVec3(*self.rotator_model.getRelativeVector(urs.scene, PanVec3.up()))

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

    def create_blob(self: Self, texture_name: str = None) -> None:
        """Creates the blob model"""

        if not LOW_VRAM and self.index == 10:
            self.create_special_blob()
            return

        if texture_name is not None:
            self.texture_name = texture_name

        if self.texture_name is not None:

            self.rotator_model = urs.application.base.loader.loadModel(
                self.base_dir.joinpath("models").joinpath("blend_uvsphere.obj")
            )
            if self.radius is not None:
                self.scale = urs.Vec3(self.radius)
            if self.position is not None:
                self.position = self.position
            self.rotator_model.setTransparency(TransparencyAttrib.M_none)
            if self.color is not None:
                self.rotator_model.setColorScaleOff()
                if self.blob_name == CENTER_BLOB_NAME:
                    self.rotator_model.setColorScale((2, 2, 2, 1))
                else:
                    self.rotator_model.setColorScale((1, 1, 1, 1))
                self.rotator_model.setColor(self.color)
            self.rotator_model.setMaterial(self.blob_material, 1)

            if self.glow_map_name is not None:
                self.rotator_model.setTexture(
                    PlanetMaterial.texture_stage_glow,
                    urs.application.base.loader.loadTexture(
                        self.base_dir.joinpath("textures").joinpath(self.glow_map_name)
                    ),
                )
            self.rotator_model.setTexture(
                PlanetMaterial.texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.texture_name)
                ),
            )

            self.rotator_model.reparentTo(urs.scene)

            if self.ring_texture is not None:
                self.create_ring()

            if self.blob_name != CENTER_BLOB_NAME and self.center_light is not None:
                if self.ring_texture is None:
                    self.rotator_model.setLight(self.center_light)
                    self.rotator_model.setShaderAuto(
                        BitMask32.allOff() | BitMask32.bit(Shader.bit_AutoShaderShadow)
                    )

            if self.rotation_speed is None:
                self.rotation_speed = (blob_random.random() * 29.00) + 1
                if self.blob_name != CENTER_BLOB_NAME:
                    self.rotation_pos = (0, 0, blob_random.random() * 360)
                    self.rotate = (-45 + (blob_random.random() * 90), 0, 0)
            else:
                self.rotation_pos = self.rotation_pos

    def create_ring(self: Self, ring_texture: str = None) -> None:
        """Creates the ring model"""

        if ring_texture is not None:
            self.ring_texture = ring_texture

        if self.ring_texture is not None and self.rotator_model is not None:
            self.planet_ring = urs.application.base.loader.loadModel(
                self.base_dir.joinpath("models").joinpath("rings.obj")
            )

            self.planet_ring.reparentTo(self.rotator_model)
            self.planet_ring.setDepthOffset(-4)
            if self.ring_scale is not None:
                self.planet_ring.setScale(
                    (self.ring_scale, self.ring_scale, self.ring_scale)
                )
            self.planet_ring.setTransparency(TransparencyAttrib.M_dual)
            if self.color is not None:
                self.planet_ring.setColor(self.color)
            self.planet_ring.setMaterial(PlanetMaterial().getMaterial(), 1)
            self.planet_ring.setTexture(
                PlanetMaterial.texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.ring_texture)
                ),
            )

    def create_special_blob(self: Self) -> None:
        self.rotator_model = urs.application.base.loader.loadModel(
            self.base_dir.joinpath("models").joinpath("death_star.glb")
        )

        self.texture_name = "moons/death_star.jpg"
        self.blob_name = "That's no moon!"

        if self.position is not None:
            self.position = self.position
        self.rotator_model.setTransparency(TransparencyAttrib.M_none)
        self.rotator_model.setColorScaleOff()
        self.rotator_model.setColorScale(PanVec4(1, 1, 1, 1))

        self.rotator_model.reparentTo(urs.scene)
        self.rotator_model.setLight(self.center_light)
        self.rotator_model.setShaderAuto(
            BitMask32.allOff() | BitMask32.bit(Shader.bit_AutoShaderShadow)
        )

        for mat in self.rotator_model.findAllMaterials():
            if mat.getName() == "Death Star":
                mat.setEmission(PanVec4(75, 75, 75, 2))

        if self.rotation_speed is None:
            self.rotation_speed = 2
        else:
            self.rotation_pos = self.rotation_pos

    def update(self: Self) -> None:
        """Called by Ursina once per frame"""

        if not FPS.paused and self.rotator_model is not None:

            degrees: float = self.rotation_speed * (
                (FPS.dt * bg_vars.timescale) / HOURS
            )
            self.rotate = (0, 0, degrees)

    def on_destroy(self: Self) -> None:
        """Called by Ursina when this Entity is destroyed"""

        if self.follower_entity is not None:
            self.follower_entity.stop_following()

        if self.rotator_model is not None:
            if self.planet_ring is not None:
                self.planet_ring.removeNode()
                del self.planet_ring
            self.rotator_model.removeNode()
            del self.rotator_model
