"""
Newton's Laws, a simulator of physics at the scale of space

Class to create NodePath instances when needed to use instead
of urs.Entity

by Jason Mott, copyright 2024
"""

from pathlib import Path
from typing import Self

from panda3d.core import Vec3 as PanVec3  # type: ignore
from panda3d.core import Vec4 as PanVec4  # type: ignore

from panda3d.core import (  # type: ignore
    NodePath,
    Vec3 as PanVec3,
    Vec4 as PanVec4,
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
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobNodePathFactory:

    _instance: "BlobNodePathFactory" = None
    _initialized: bool = False

    def __new__(cls) -> "BlobNodePathFactory":
        if cls._instance is None:
            cls._instance = super(BlobNodePathFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self: Self):

        if not BlobNodePathFactory._initialized:
            self.base_dir: Path = urs.application.asset_folder
            BlobNodePathFactory._initialized = True

    def create_node_path(
        self: Self,
        model: str,
        parent: NodePath,
        scale: PanVec3 = None,
        texture: str = None,
        glow_map: str = None,
        color: PanVec4 = None,
    ) -> NodePath:

        node_path: NodePath = urs.application.base.loader.loadModel(
            self.base_dir.joinpath("models").joinpath(model)
        )
        node_path.reparentTo(parent)
        node_path.setTransparency(TransparencyAttrib.M_alpha)
        if scale is not None:
            node_path.setScale(parent, scale)
        if color is not None:
            node_path.setColorScaleOff()
            node_path.setColorScale((0.9, 0.9, 0.9, 0.9))
            node_path.setColor(color)

        if glow_map is not None:
            node_path.setTexture(
                PlanetMaterial.texture_stage_glow,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(glow_map)
                ),
            )
        if texture is not None:
            node_path.setTexture(
                PlanetMaterial.texture_stage,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(texture)
                ),
            )

        return node_path

    def set_texture(
        self: Self, node_path: NodePath, texture: str, glow_map: str = None
    ) -> None:

        node_path.setTextureOff()
        node_path.clearTexture()

        if glow_map is not None:
            node_path.setTexture(
                PlanetMaterial.texture_stage_glow,
                urs.application.base.loader.loadTexture(
                    self.base_dir.joinpath("textures").joinpath(glow_map)
                ),
            )

        node_path.setTexture(
            PlanetMaterial.texture_stage,
            urs.application.base.loader.loadTexture(
                self.base_dir.joinpath("textures").joinpath(texture)
            ),
        )
