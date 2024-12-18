"""
Newton's Laws, a simulator of physics at the scale of space

Class to create the base Ursina Entity for a blob (and helper classes)

by Jason Mott, copyright 2024
"""

from pathlib import Path
from typing import Self, Tuple

from panda3d.core import Vec3 as PanVec3  # type: ignore

from panda3d.core import (  # type: ignore
    NodePath,
    TextureStage,
    TransparencyAttrib,
    Material,
)  # type: ignore

import ursina as urs  # type: ignore

from newtons_blobs.globals import *

from newtons_blobs.blob_random import blob_random
from nb_ursina.fps import FPS
from newtons_blobs import BlobGlobalVars as bg_vars

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class PlanetMaterial:
    """
    A class that holds a Material instance tweaked for planet textures

    Methods
    -------
    getMaterial(self: Self) -> Material
        Returns the Material instance

    """

    _instance: "PlanetMaterial" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlanetMaterial, cls).__new__(cls)
        return cls._instance

    def __init__(self: Self):
        self.material: Material = Material("planet_material")
        self.material.setShininess(99.999992)
        # self.material.setRoughness(0.8)
        self.material.setMetallic(0)
        self.material.setBaseColor((1, 1, 1, 1))
        self.material.setAmbient((1, 1, 1, 1))
        self.material.setDiffuse((0.8, 0.8, 0.8, 1))
        # self.material.setSpecular((0.5, 0.5, 0.5, 1))
        self.material.setEmission((0, 0, 0, 0))
        self.material.setRefractiveIndex(1)

    def getMaterial(self: Self) -> Material:
        return self.material


class SunMaterial:
    """
     A class that holds a Material instance tweaked for sun textures

    Methods
    -------
    getMaterial(self: Self) -> Material
        Returns the Material instance

    """

    _instance: "SunMaterial" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SunMaterial, cls).__new__(cls)
        return cls._instance

    def __init__(self: Self):
        self.material: Material = Material("sun_material")
        self.material.setShininess(120)
        # self.setRoughness(0.8)
        self.material.setMetallic(0)
        self.material.setBaseColor((1, 1, 1, 1))
        self.material.setAmbient((1, 1, 1, 1))
        self.material.setDiffuse((0.8, 0.8, 0.8, 1))
        self.material.setSpecular((1, 1, 1, 1))
        self.material.setEmission((1, 1, 1, 1))
        self.material.setRefractiveIndex(1)

    def getMaterial(self: Self) -> Material:
        return self.material


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

    follower_entity: urs.Entity
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

    rotator_texture_stage: TextureStage = TextureStage("ts")
    rotator_texture_stage.setMode(TextureStage.MModulate)

    def __init__(self: Self, **kwargs):

        self.rotator_model: NodePath = None
        self.planet_ring: NodePath = None
        self.blob_material: Material = kwargs.get("blob_material")
        self.base_dir: Path = urs.application.asset_folder
        self.default_color: urs.Color = urs.color.rgba32(1, 1, 1, 1)
        self._radius: float = None
        self.blob_name: str = kwargs.get("name")
        self._rotation_speed: float = None
        self._rotation_pos: Tuple[float, float, float] = None
        self._pos: urs.Vec3 = None
        self.texture_name: str = kwargs.get("texture_name")
        self.ring_texture: str = kwargs.get("ring_texture")
        self.center_light: NodePath = kwargs.get("center_light")

        self._follower_entity: urs.Entity = None
        self.follower_entity_last_pos: urs.Vec3 = None

        for key in (
            "model",
            "texture",
            "texture_scale",
            "texture_offset",
            "name",
            "texture_name",
            "ring_texture",
            "blob_material",
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
        return urs.Vec3(self.rotator_model.getScale())

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
    def follower_entity(self: Self) -> urs.Entity:
        """Get this follower_entity property"""
        return self._follower_entity

    @follower_entity.setter
    def follower_entity(self: Self, follower_entity: urs.Entity) -> None:
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
        return PanVec3(
            *self.rotator_model.getRelativeVector(self.center_light, PanVec3.up())
        )

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
            self.rotator_model.setTransparency(TransparencyAttrib.M_dual)
            if self.color is not None:
                self.rotator_model.setColor(self.color)
            self.rotator_model.setMaterial(self.blob_material, 1)
            self.rotator_model.setTexture(
                BlobRotator.rotator_texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.texture_name)
                ),
                2,
            )
            self.rotator_model.reparentTo(urs.scene)

            if self.ring_texture is not None:
                self.create_ring()

            if self.blob_name != CENTER_BLOB_NAME and self.center_light is not None:
                if self.ring_texture is None:
                    self.rotator_model.setLight(self.center_light)
                    self.rotator_model.setShaderAuto()

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
            # self.planet_ring.setTwoSided(True)
            scale: float = (blob_random.random() * 0.3) + 0.4
            self.planet_ring.setDepthOffset(-4)
            self.planet_ring.setScale((scale, scale, scale))
            self.planet_ring.setTransparency(TransparencyAttrib.M_dual)
            self.planet_ring.setMaterial(PlanetMaterial().getMaterial(), 1)
            self.planet_ring.setTexture(
                BlobRotator.rotator_texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(self.ring_texture)
                ),
                2,
            )
            # self.planet_ring.setAntialias(AntialiasAttrib.M_multisample)
            # self.planet_ring.setColor((1, 1, 1, 0.6))

    def update(self: Self) -> None:
        """Called by Ursina once per frame"""

        if not FPS.paused and self.rotator_model is not None:

            degrees: float = self.rotation_speed * (
                (FPS.dt * bg_vars.timescale) / HOURS
            )
            self.rotate = (0, 0, degrees)

    def on_destroy(self: Self) -> None:
        """Called by Ursina when this Entity is destroyed"""
        if self.rotator_model is not None:
            if self.planet_ring is not None:
                self.planet_ring.removeNode()
                del self.planet_ring
            self.rotator_model.removeNode()
            del self.rotator_model
