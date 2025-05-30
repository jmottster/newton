"""
Newton's Laws, a simulator of physics at the scale of space

Class to create dust cloud upon blob collisions

by Jason Mott, copyright 2025
"""

from pathlib import Path
from typing import Self


from panda3d.physics import (  # type: ignore
    BaseParticleRenderer,
    BaseParticleEmitter,
)  # type: ignore
from panda3d.core import (  # type: ignore
    Vec4 as PanVec4,
    Vec3 as PanVec3,
    Point3 as PanPoint3,
)  # type: ignore

from direct.particles.ParticleEffect import ParticleEffect, Particles, ForceGroup  # type: ignore

import ursina as urs  # type: ignore

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobCollisionCloud(ParticleEffect):
    """
    Class to create dust cloud upon blob collisions

    See Panda3D's documentation for ParticleEffect (this class' super class)

    Of concern here is:

    To instantiate:
    instance = BlobCollisionCloud(node_path_instance)

    instance.start(node_path_where_cloud_originates)

    instance.cleanup() when you're done

    This is also a NodePath itself, so all that functionality is available


    """

    life_span: float = 4.00

    def __init__(self: Self, name):

        super().__init__()
        if name is not None:
            self.name = name

        self.base_dir: Path = urs.application.asset_folder

        urs.application.base.enableParticles()

        particles: Particles = Particles.Particles(f"particles-{name}")
        # Particles parameters
        particles.setFactory("PointParticleFactory")
        particles.setRenderer("SpriteParticleRenderer")
        particles.setEmitter("SphereVolumeEmitter")
        particles.setPoolSize(10000)
        particles.setBirthRate(0.0500)
        particles.setLitterSize(10)
        particles.setLitterSpread(2000)
        particles.setSystemLifespan(BlobCollisionCloud.life_span)
        particles.setLocalVelocityFlag(1)
        particles.setSystemGrowsOlderFlag(1)
        # Factory parameters
        particles.factory.setLifespanBase(4.0000)
        particles.factory.setLifespanSpread(0.2500)
        particles.factory.setMassBase(20.0000)
        particles.factory.setMassSpread(0.0100)
        particles.factory.setTerminalVelocityBase(400.0000)
        particles.factory.setTerminalVelocitySpread(0.0000)
        # Renderer parameters
        particles.renderer.setAlphaMode(BaseParticleRenderer.PR_ALPHA_OUT)
        particles.renderer.setUserAlpha(0.07)
        # Sprite parameters
        particles.renderer.setTexture(
            urs.application.base.loader.loadTexture(
                self.base_dir.joinpath("textures").joinpath("collision/dust.png")
            )
        )
        particles.renderer.setColor(PanVec4(1.00, 1.00, 1.00, 1.00))
        particles.renderer.setXScaleFlag(1)
        particles.renderer.setYScaleFlag(1)
        particles.renderer.setAnimAngleFlag(1)
        particles.renderer.setInitialXScale(0.00500)
        particles.renderer.setFinalXScale(0.00200)
        particles.renderer.setInitialYScale(0.00500)
        particles.renderer.setFinalYScale(0.00200)
        particles.renderer.setNonanimatedTheta(90.0000)
        particles.renderer.setAlphaBlendMethod(BaseParticleRenderer.PP_BLEND_CUBIC)
        particles.renderer.setAlphaDisable(0)
        # Emitter parameters
        particles.emitter.setEmissionType(BaseParticleEmitter.ET_RADIATE)
        particles.emitter.setAmplitude(2.000)
        particles.emitter.setAmplitudeSpread(2.0000)
        particles.emitter.setOffsetForce(PanVec3(0.0000, 0.0000, 0.0000))
        particles.emitter.setExplicitLaunchVector(PanVec3(1.0000, 0.0000, 0.0000))
        particles.emitter.setRadiateOrigin(PanPoint3(0.0000, 0.0000, 0.0000))
        # Sphere Volume parameters
        particles.emitter.setRadius(0.01000)
        self.addParticles(particles)
        force: ForceGroup = ForceGroup.ForceGroup("gravity")
        # Force parameters
        self.addForceGroup(force)
