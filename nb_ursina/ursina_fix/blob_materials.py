"""
Newton's Laws, a simulator of physics at the scale of space

Classes that hold a Material instance

by Jason Mott, copyright 2024
"""

from typing import Self

from panda3d.core import (  # type: ignore
    Material,
    TextureStage,
)  # type: ignore

from newtons_blobs.globals import *

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
    _initialized: bool = False

    texture_stage: TextureStage = TextureStage("ts")
    texture_stage.setMode(TextureStage.MModulate)

    texture_stage_glow: TextureStage = TextureStage("ts_glow")
    texture_stage_glow.setMode(TextureStage.MGlow)

    def __new__(cls) -> "PlanetMaterial":
        if cls._instance is None:
            cls._instance = super(PlanetMaterial, cls).__new__(cls)
        return cls._instance

    def __init__(self: Self):

        if not PlanetMaterial._initialized:
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
            PlanetMaterial._initialized = True

    def getMaterial(self: Self) -> Material:
        """Returns the Material instance"""
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
    _initialized: bool = False

    texture_stage: TextureStage = TextureStage("ts")
    texture_stage.setMode(TextureStage.MModulate)

    texture_stage_glow: TextureStage = TextureStage("ts_glow")
    texture_stage_glow.setMode(TextureStage.MGlow)

    def __new__(cls) -> "SunMaterial":
        if cls._instance is None:
            cls._instance = super(SunMaterial, cls).__new__(cls)
        return cls._instance

    def __init__(self: Self):

        if not SunMaterial._initialized:
            self.material: Material = Material("sun_material")
            self.material.setShininess(120)
            # self.setRoughness(0.8)
            self.material.setMetallic(0)
            self.material.setBaseColor((1, 1, 1, 1))
            self.material.setAmbient((1, 1, 1, 1))
            self.material.setDiffuse((0.8, 0.8, 0.8, 1))
            self.material.setSpecular((1, 1, 1, 1))
            self.material.setEmission((2, 2, 2, 1))
            self.material.setRefractiveIndex(1)
            SunMaterial._initialized = True

    def getMaterial(self: Self) -> Material:
        """Returns the Material instance"""
        return self.material
