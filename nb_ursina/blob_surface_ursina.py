"""
Newton's Laws, a simulator of physics at the scale of space

A class used to represent an object that draws a blob, with a distinction of the center blob

by Jason Mott, copyright 2024
"""

import math
from typing import ClassVar, List, Tuple, Self, cast
from collections import deque

from panda3d.core import (  # type: ignore
    PointLight,
    Spotlight,
    TransparencyAttrib,
    NodePath,
    BitMask32,
    Shader,
    Vec3 as PanVec3,
)  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore


from newtons_blobs import BlobSurface
from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs import BlobUniverse
from newtons_blobs import blob_random

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_textures import *
from .blob_utils_ursina import MathFunctions as mf, LightUtils as lu

from .fps import FPS
from .ursina_fix import BlobText, BlobRotator, SunMaterial, PlanetMaterial, BlobLine
from .blob_collision_cloud import BlobCollisionCloud as coll_cloud

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

    build_trail_gradient() -> None
        Constructs the color gradient for the trail using colors in self.color_gradient

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
        "thickness",
        "_barycenter_blob",
        "check_barycenter_dist",
        "line_renderer",
        "pos_overlap",
        "orbit_arc",
    )

    def __init__(
        self: Self,
        segments: int = 2,
        min_spacing: float = 0.05,
        barycenter_blob: "BlobCore" = None,
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
        self.orig_segments: int = self.segments
        self.orbit_arc: float = math.pi * 1.25
        self.pos_overlap: int = segments
        self._t: float = 0

        self.min_spacing: float = min_spacing
        self.spacing_check: int = self.orig_segments
        self.space_check_multiplier: int = 1
        self.thickness: int = 4
        self._barycenter_blob: BlobCore = None
        self.barycenter_blob = barycenter_blob
        self.check_barycenter_dist: float = 2
        if self.is_moon:
            self.thickness = 3
            self.min_spacing = bg_vars.min_moon_radius / self.parent.scale_x
            self.space_check_multiplier = 8
            self.segments = 250
            self.pos_overlap = segments

        self.points: deque[urs.Vec3] = deque(
            [urs.Vec3(0, 0, 0) for _ in range(0, self.segments)]
        )
        self.color_gradient: List[urs.Color] = [urs.color.clear, self.color, self.color]
        self.color_test: List[urs.Color] = [urs.color.red, urs.color.yellow]
        self.colors: List = [urs.Color]
        self.build_trail_gradient()

        self.last_point_distances: deque[urs.Vec3] = deque([0])

        self.line_renderer = urs.Entity(
            name=self.parent.blob_name,
            parent=urs.scene,
            model=BlobLine(
                parent=self.line_renderer,
                name=self.parent.blob_name,
                vertices=self.points,  # type: ignore
                colors=self.colors,
                thickness=self.thickness,
            ),
            unlit=True,
        )
        self.line_renderer.setShaderOff()
        self.line_renderer.setScale(urs.scene, self.parent.getScale(urs.scene))

        self.line_renderer.setTransparency(TransparencyAttrib.M_alpha)
        self.line_renderer.setLightOff()
        for bit in range(0, len(lu.bit_masks)):
            self.line_renderer.hide(lu.bit_masks[bit])

        if self.is_moon:
            self.enabled = False
        else:
            self.line_renderer.setPos(urs.scene, self.barycenter_blob.getPos(urs.scene))
            self.calibrate_segments(True)

    @property
    def barycenter_blob(self: Self) -> urs.Entity:
        if self._barycenter_blob is None:
            if self.parent.index != 0:
                return BlobSurfaceUrsina.center_blob
            else:
                return urs.scene
        return self._barycenter_blob

    @barycenter_blob.setter
    def barycenter_blob(self: Self, barycenter_blob: urs.Entity) -> None:
        self._barycenter_blob = barycenter_blob

    def update(self: Self) -> None:
        """
        Called by Ursina once per frame. This will keep the trial
        current and only min_spacing * segments long
        """

        self.line_renderer.setPos(urs.scene, self.barycenter_blob.getPos(urs.scene))

        if not FPS.paused:

            if len(self.last_point_distances) >= self.spacing_check:
                self.calibrate_segments()

            self.last_point_distances[-1] = mf.distance(
                self.points[-2], self.points[-1]
            )

            if self.last_point_distances[-1] >= self.min_spacing:

                if len(self.points) == self.segments:
                    self.points.popleft()
                    self.points.append(self.getPos(self.line_renderer))
                    self.last_point_distances.append(0)
                else:
                    self.points.append(self.getPos(self.line_renderer))
                    self.last_point_distances.append(0)
                    self.build_trail_gradient()
            else:

                self.points[-1] = self.getPos(self.line_renderer)

            self.line_renderer.model.generate()

    def build_trail_gradient(self: Self) -> None:
        """Constructs the color gradient for the trail using colors in self.color_gradient"""

        self.colors.clear()

        length = len(self.points)
        for i in range(length):
            self.colors.append(mf.sample_gradient(self.color_gradient, i / length))

        # For testing purposes
        # color = 0
        # for i in range(length):
        #     if i % 2:
        #         color = 1
        #     else:
        #         color = 0
        #     self.colors.append(self.color_test[color])

    def calibrate_segments(self: Self, new: bool = False) -> None:
        """
        Called when the number of items in self.last_point_distances >= self.spacing_check
        this will adjust self.min_spacing and self.segments to control the length of the trail
        """

        if BlobSurfaceUrsina.center_blob is None:
            return

        r = mf.distance(
            self.getPos(self.line_renderer),
            self.line_renderer.getPos(self.line_renderer),
        )

        self.min_spacing = r * self.orbit_arc / self.orig_segments

        if new:

            for i in range(0, len(self.points)):
                self.points[i] = self.getPos(self.line_renderer)

            while len(self.points) > 3:
                self.points.popleft()

            self.spacing_check = self.segments
        else:

            avg_length = sum(self.last_point_distances) / len(self.last_point_distances)

            if avg_length <= self.min_spacing:
                avg_length = self.min_spacing
                self.segments = self.orig_segments
            else:
                arc = r * (math.asin(avg_length / (r * 2)) * 2)
                self.segments = round(r * self.orbit_arc / arc)

            self.spacing_check = self.segments * self.space_check_multiplier

        self.last_point_distances.clear()
        self.last_point_distances.append(0)

        while len(self.points) > self.segments:
            self.points.popleft()

        self.build_trail_gradient()

    def on_enable(self: Self) -> None:
        """
        Called by Ursina when self.enabled is set to True. This passes the True flag on to
        self.line_renderer
        """
        if self.line_renderer is not None:
            if not self.line_renderer.enabled:
                self.line_renderer.enabled = True
                self.line_renderer.setPos(
                    urs.scene, self.barycenter_blob.getPos(urs.scene)
                )

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
        self.line_renderer.model.removeNode()

        self.points.clear()
        self.points = None

        urs.destroy(self.line_renderer)

        self.barycenter_blob = None


class BlobCore(BlobRotator):
    """
    A class to create a blob Entity that rotates,
    can light up if center blob, gives special lights for rings, and has trails

    Attributes
    ----------
    **kwargs
        Specific to this class:
        rotation_speed: float, rotation_pos: Tuple[float, float, float]
    barycenter_blob: BlobCore
        The blob that this blob orbits, if it's not the center blob

    Methods
    -------
    swallowed_by(blob: "BlobSurface") -> None
        Tells this blob what other blob is swallowing it

    check_light_source() -> None
        Checks if the barycenter blob has its own light and uses that if so.
        Otherwise it will use the center blob light

    begin_disintegration() -> None
        Instantiates the dust cloud object

    set_orbital_pos_vel(orbital: BlobSurface) -> None
        Sets orbital to a position and velocity appropriate for an orbital of this blob

    create_light() -> None
        Creates a point light at the center of this blob. Used for
        center blob only.

    create_spotlight() -> None
        Creates a spotlight just for this blob, used to correct
        poor shadowing -- especially on rings -- by the point light from center blob.

    set_spotlight(light_node: NodePath) -> None
        Sets a spotlight just for this blob from another source, used to correct
        poor shadowing by the point light from center blob.

    unset_spotlight() -> None
        Removes the spotlight reference set on this blob by set_spotlight(), and returns to using
        the center blob. Notably, this does not destroy the spotlight, as that is the responsibility
        of the sender to set_spotlight()

    update_spotlight() -> None
        Updates the position of the spotlight created in create_spotlight(), and
        ensures the light is pointing at this blob.

    remove_spotlight() -> None
        Destroys the spotlight just for this blob, and returns to using
        the center blob

    create_trail() -> None
        Creates the orbital trail. Called by input() when the "t" key is pressed if it
        is not running

    destroy_trail() -> None
        Disables and destroys the trail entity. Called by input() when the "t" is pressed
        and there is a trail running.

    create_text_overlay() -> None
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()

    update_text_background() -> None
        This is for when text changes, it will ensure the background size updates accordingly

    destroy_text_overlay() -> None
        Cleans up all the objects related to the text overlay. Called by
        on_click()

    full_overlay_text() -> str
        creates info text with full details

    short_overlay_text() -> str
        creates info text with just name

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

    # __slots__ = (
    #     "mass",
    #     "rotation_speed",
    #     "rotation_pos",
    #     "trail_color",
    #     "trail",
    #     "barycenter_blob",
    #     "blob_name",
    # )

    def __init__(self: Self, **kwargs):

        self._mass: float = None
        self.percent_radius: int = None
        self.percent_mass: int = None
        self.trail_color: urs.Color = kwargs.get("trail_color")
        self.light_node: NodePath = None
        self.light_bit_mask: BitMask32 = None
        self.light_bit_mask_index: int = None
        self.light_scale: float = None

        super().__init__(
            blob_material=kwargs.get("blob_material"),
            index=kwargs.get("index"),
            blob_name=kwargs.get("blob_name"),
            rotation_speed=kwargs.get("rotation_speed"),
            rotation_pos=kwargs.get("rotation_pos"),
            position=kwargs.get("position"),
            texture_name=kwargs.get("texture_name"),
            glow_map_name=kwargs.get("glow_map_name"),
            ring_texture=kwargs.get("ring_texture"),
            ring_scale=kwargs.get("ring_scale"),
            scale=kwargs.get("scale"),
            center_light=kwargs.get("center_light"),
            color=kwargs.get("color"),
        )

        self.is_moon: bool = kwargs.get("radius") < bg_vars.min_radius
        self.mass = kwargs.get("mass")

        for key in (
            "model",
            "shader",
            "texture",
            "texture_scale",
            "texture_offset",
            "mass",
            "trail_color",
            "blob_material",
            "index",
            "blob_name",
            "rotation_speed",
            "rotation_pos",
            "position",
            "texture_name",
            "glow_map_name",
            "ring_texture",
            "scale",
            "center_light",
            "color",
        ):
            if key in kwargs:
                del kwargs[key]

        for key in (
            "origin",
            "origin_x",
            "origin_y",
            "origin_z",
            "collider",
        ):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._barycenter_blob: BlobCore = None
        self.trail: TrailRenderer = None
        self.trail_ready: bool = False
        self.text_entity: urs.Entity = None
        self.info_text: BlobText = None
        self.text: str = None
        self.text_scale: urs.Vec3 = urs.Vec3(0.1, 0.1, 0.1)
        self.text_position_pad: float = self.text_scale[0] - 0.02
        self.is_gas: bool = self.percent_radius > 50
        self.is_rocky: bool = self.percent_radius < 50

        if self.is_moon:
            self.text_scale = urs.Vec3(0.08, 0.08, 0.08)
            self.text_position_pad = self.text_scale[0] - 0.03

        self.text_position: float = self.scale_x / self.text_position_pad
        self.all_text_on: bool = False
        self.planet_text_only: bool = False
        self.text_on: bool = False
        self.text_full_details: bool = True
        self._swallowed: bool = False
        self.collision_cloud: coll_cloud = None
        self.collision_cleanup_timer: float = 1.5
        self.swallowed_by_blob: BlobCore = None
        self.collisions: deque[urs.Vec3] = deque([])

        for bit in range(1, len(lu.bit_masks)):
            self.hide(lu.bit_masks[bit])
            self.rotator_model.hide(lu.bit_masks[bit])

    @property
    def barycenter_blob(self: Self) -> "BlobCore":
        """The blob that this blob orbits, if it's not the center blob"""
        return getattr(self, "_barycenter_blob", None)

    @barycenter_blob.setter
    def barycenter_blob(self: Self, barycenter_blob: "BlobCore") -> None:
        """Sets the blob that this blob orbits, if it's not the center blob"""
        self._barycenter_blob = barycenter_blob
        if barycenter_blob is not None:
            self.check_light_source()

    @property
    def radius(self: Self) -> float:
        """The blob's radius (equivalent to scale)"""
        return super().radius

    @BlobRotator.radius.setter
    def radius(self: Self, radius: float) -> None:
        """Set the blob's radius (and scale)"""

        x_size: bool = False
        if self.radius is not None and round(self.scale_x) > round(self.radius) and (self.scale_x / self.radius) >= 1.5:  # type: ignore
            x_size = True

        super(BlobCore, type(self)).radius.fset(self, radius)  # type: ignore
        if not self.is_moon:
            self.percent_radius = round(
                (
                    (self.scale_x - bg_vars.min_radius)
                    / (bg_vars.max_radius - bg_vars.min_radius)
                )
                * 100
            )

            if x_size:
                self.input("y")
        else:
            self.percent_radius = round(
                (
                    (self.scale_x - bg_vars.min_moon_radius)
                    / (bg_vars.max_moon_radius - bg_vars.min_moon_radius)
                )
                * 100
            )

            if x_size:
                self.input("u")

    @property
    def mass(self: Self) -> float:
        """Returns the mass of the blob"""
        return self._mass

    @mass.setter
    def mass(self: Self, mass: float) -> None:
        """Sets the blob's mass, and updates the % mass attribute"""
        self._mass = mass

        if not self.is_moon:
            self.percent_mass = round(
                (self._mass - bg_vars.min_mass)
                / (bg_vars.max_mass - bg_vars.min_mass)
                * 100
            )

        else:
            self.percent_mass = round(
                (self.mass - bg_vars.min_moon_mass)
                / (bg_vars.max_moon_mass - bg_vars.min_moon_mass)
                * 100
            )

    @property
    def swallowed(self: Self) -> bool:
        """Returns bool indicating if this blob has been swallowed"""
        return self._swallowed

    @swallowed.setter
    def swallowed(self: Self, swallowed: bool) -> None:
        """Sets bool indicating if this blob has been swallowed"""
        self.begin_disintegration()

    def swallowed_by(self: Self, blob: "BlobCore") -> None:
        """Tells this blob what other blob is swallowing it"""
        self.swallowed_by_blob = blob

    def check_light_source(self: Self) -> None:
        """
        Checks if the barycenter blob has its own light and uses that if so.
        Otherwise it will use the center blob light
        """
        if (
            self._barycenter_blob is not None
            and self._barycenter_blob.blob_name != CENTER_BLOB_NAME
            and mf.distance(self._barycenter_blob.position, self.position)
            < (self._barycenter_blob.scale_x * 50)
            and self._barycenter_blob.light_node is not None
        ):

            if not self.rotator_model.hasLight(self.barycenter_blob.light_node):
                self.rotator_model.clearLight()
                self.rotator_model.hide(lu.get_center_light_bitmask())

                self.rotator_model.setLight(self.barycenter_blob.light_node)
                self.rotator_model.show(
                    self.barycenter_blob.light_node.node().getCameraMask()
                )
        else:
            if not self.rotator_model.hasLight(self.center_light):
                self.rotator_model.clearLight()
                self.rotator_model.setLight(self.center_light)
                self.rotator_model.show(lu.get_center_light_bitmask())
                for bit in range(1, len(lu.bit_masks)):
                    self.hide(lu.bit_masks[bit])
                    self.rotator_model.hide(lu.bit_masks[bit])

    def begin_disintegration(self: Self) -> None:
        """Instantiates the dust cloud object"""
        self.collision_cloud = coll_cloud(self.blob_name)

    def set_orbital_pos_vel(self: Self, orbital: "BlobSurfaceUrsina") -> urs.Vec3:
        """Sets orbital to a position and velocity appropriate for an orbital of this blob"""

        self.rotate = (0, 0, (blob_random.random() * 360.00))
        orbital.ursina_blob.rotation_pos = self.rotation_pos

        orbit_distance: float = (
            blob_random.random() * (self.scale_x * 15)
        ) + self.scale_x * 3
        move: urs.Vec3 = urs.Vec3(self.my_right.normalized() * orbit_distance)

        orbital.ursina_blob.position = urs.Vec3(self.position + move)
        orbital.position = orbital.ursina_blob.position

        dx: float = (self.world_x - orbital.ursina_blob.world_x) * bg_vars.scale_up
        dy: float = (self.world_y - orbital.ursina_blob.world_y) * bg_vars.scale_up
        dz: float = (self.world_z - orbital.ursina_blob.world_z) * bg_vars.scale_up

        distance: float = math.sqrt(dx**2 + dy**2 + dz**2)
        # print(f"{self.index} to {orbital.ursina_blob.index} dist: {distance}")

        vel: float = math.sqrt(G * self.mass / distance)

        orbital.ursina_blob.barycenter_blob = self

        return urs.Vec3(orbital.ursina_blob.my_forward.normalized() * vel)

    def create_light(self: Self) -> None:
        """
        Creates a point light at the center of this blob. Used for
        center blob only.
        """

        light: PointLight = PointLight(f"{self.blob_name}_plight")
        light.setShadowCaster(
            True,
            bg_vars.center_blob_shadow_resolution,
            bg_vars.center_blob_shadow_resolution,
        )
        light.setAttenuation((1, 0, 0))  # constant, linear, and quadratic.
        light.setColor((3, 3, 3, 1))

        self.light_node = self.rotator_model.attachNewNode(light)
        self.light_node.reparentTo(self.rotator_model)  # type: ignore

        self.light_node.setScale(urs.scene, bg_vars.center_blob_radius * 30)

        self.light_bit_mask = lu.bit_masks[lu.get_center_light_index()]
        self.light_node.node().setCameraMask(self.light_bit_mask)

        lens = self.light_node.node().getLens()
        far = bg_vars.au_scale_factor * 4 * bg_vars.num_planets
        lens.setNearFar(
            500 / self.light_node.getSx(),
            far,
        )

        self.rotator_model.setLight(self.light_node)
        self.show(lu.get_center_light_bitmask())
        self.rotator_model.show(lu.get_center_light_bitmask())

    def create_spotlight(self: Self) -> None:
        """
        Creates a spotlight just for this blob, used to correct
        poor shadowing -- especially on rings -- by the point light from center blob.
        """

        if self.light_node is not None:
            return

        self.clearLight(self.center_light)
        self.rotator_model.clearLight(self.center_light)

        light: Spotlight = Spotlight(f"{self.blob_name}_slight")
        light.setShadowCaster(
            True, bg_vars.blob_shadow_resolution, bg_vars.blob_shadow_resolution
        )
        light.setAttenuation((1, 0, 0))  # constant, linear, and quadratic.
        light.setColor((3, 3, 3, 1))

        self.light_node = self.rotator_model.attachNewNode(light)
        self.light_node.reparentTo(urs.scene)  # type: ignore

        self.light_scale = bg_vars.center_blob_radius * 30

        self.light_node.setScale(urs.scene, self.light_scale)

        self.light_bit_mask_index = lu.get_next_index()
        self.light_bit_mask = lu.bit_masks[self.light_bit_mask_index]
        self.light_node.node().setCameraMask(self.light_bit_mask)

        lens = self.light_node.node().getLens()
        far = self.scale_x * 50
        lens.setNearFar(
            500 / self.light_node.getSx(),
            far,
        )
        lens.setFov(90)

        # self.light_node.node().showFrustum()
        self.update_spotlight()

        self.rotator_model.setShaderAuto(
            BitMask32.allOff() | BitMask32.bit(Shader.bit_AutoShaderShadow)
        )
        self.hide(lu.get_center_light_bitmask())
        self.rotator_model.hide(lu.get_center_light_bitmask())
        self.rotator_model.setLight(self.light_node)
        self.rotator_model.show(self.light_bit_mask)

    def set_spotlight(self: Self, light_node: NodePath) -> None:
        """
        Sets a spotlight just for this blob from another source, used to correct
        poor shadowing by the point light from center blob.
        """

        if self.light_node is not None:
            return

        self.clearLight(self.center_light)
        self.rotator_model.clearLight(self.center_light)

        self.light_node = light_node

        self.update_spotlight()

        self.rotator_model.setShaderAuto(
            BitMask32.allOff() | BitMask32.bit(Shader.bit_AutoShaderShadow)
        )
        self.hide(lu.get_center_light_bitmask())
        self.rotator_model.hide(lu.get_center_light_bitmask())
        self.rotator_model.setLight(self.light_node)
        self.rotator_model.show(self.light_node.node().getCameraMask())

    def unset_spotlight(self: Self) -> None:
        """
        Removes the spotlight reference set on this blob by set_spotlight(), and returns to using
        the center blob. Notably, this does not destroy the spotlight, as that is the responsibility
        of the sender to set_spotlight()
        """

        if (
            self.ring_texture is None
            and self.light_node is not None
            and self.blob_name != CENTER_BLOB_NAME
        ):
            self.clearLight()
            self.rotator_model.clearLight()

            self.light_node = None

            self.rotator_model.setLight(self.center_light)
            self.rotator_model.show(lu.get_center_light_bitmask())

    def update_spotlight(self: Self) -> None:
        """
        Updates the position of the spotlight created in create_spotlight(), and
        ensures the light is pointing at this blob.
        """
        direction = urs.Vec3(
            self.center_light.getPos(urs.scene) - self.rotator_model.getPos(urs.scene)
        ).normalized()

        distance = self.scale_x * 40

        pos = self.rotator_model.getPos(urs.scene) + urs.Vec3(direction * distance)
        self.light_node.setPos(urs.scene, pos)
        self.light_node.lookAt(
            self.rotator_model, BlobSurfaceUrsina.center_blob.world_up
        )

    def remove_spotlight(self: Self) -> None:
        """
        Destroys the spotlight just for this blob, and returns to using
        the center blob
        """

        if (
            self.ring_texture is None
            and self.light_node is not None
            and self.blob_name != CENTER_BLOB_NAME
        ):
            self.clearLight()
            self.rotator_model.clearLight()
            self.light_node.removeNode()
            del self.light_node

            self.light_node = None
            lu.return_index(self.light_bit_mask_index)
            self.light_bit_mask = None
            self.light_bit_mask_index = None

            self.rotator_model.setLight(self.center_light)
            self.rotator_model.show(lu.get_center_light_bitmask())

    def create_trail(self: Self, barycenter_blob: "BlobCore" = None) -> None:
        """
        Creates the orbital trail. Called by input() when the "t" key is pressed if it
        is not running
        """

        if barycenter_blob is None:
            barycenter_blob = self.barycenter_blob

        self.trail = TrailRenderer(
            segments=250,
            min_spacing=bg_vars.max_radius / self.scale_x,
            parent=self,
            color=self.trail_color,
            barycenter_blob=barycenter_blob,
            is_moon=self.is_moon,
            unlit=True,
            shader=shd.unlit_shader,
        )

    def destroy_trail(self: Self) -> None:
        """
        Disables and destroys the trail entity. Called by input() when the "t" is pressed
        and there is a trail running.
        """
        if self.trail is not None:
            self.trail.enabled = False  # type: ignore
            urs.destroy(self.trail)
            self.trail = None

    def create_text_overlay(self: Self) -> None:
        """
        Instantiates all the objects necessary to display the text overlay.
        This is called by on_click()
        """

        if self.text_entity is None:
            self.text_entity = BlobRotator(
                scale=self.text_scale,
                color=urs.color.rgba(1, 1, 1, 0.9),
                unlit=True,
            )

            self.text_entity.setShaderOff()
            self.text_entity.setLightOff()

            for bit in range(0, len(lu.bit_masks)):
                self.text_entity.hide(lu.bit_masks[bit])

            self.text = self.short_overlay_text()

            if self.text_on and self.text_full_details:
                self.text = self.full_overlay_text()

            self.info_text = BlobText(
                text=self.text,
                parent=self.text_entity,
                font=DISPLAY_FONT,
                size=(STAT_FONT_SIZE),
                origin=(0, 0, -0.5),
                position=(0, 0, 0),
                color=urs.color.rgba(1, 1, 1, 0.9),
                enabled=False,
                unlit=True,
            )

            self.info_text.setLightOff(1)
            for bit in range(0, len(lu.bit_masks)):
                self.info_text.hide(lu.bit_masks[bit])

        self.text_entity.enabled = True
        self.info_text.enabled = True
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

    def destroy_text_overlay(self: Self) -> None:
        """
        Cleans up all the objects related to the text overlay. Called by
        on_click()
        """
        if self.text_entity is not None:
            self.info_text.enabled = False
            urs.destroy(self.info_text)
            self.info_text = None
            self.text_entity.enabled = False
            urs.destroy(self.text_entity)
            self.text_entity = None

    def full_overlay_text(self: Self) -> str:
        """creates info text with full details"""
        return f"{self.blob_name}: mass: {float(self.mass)} ({self.percent_mass}%) radius: {round(self.scale_x,2)} ({self.percent_radius}%) x: {round(self.position[0])} y: {round(self.position[1])} z: {round(self.position[2])}"

    def short_overlay_text(self: Self) -> str:
        """creates info text with just name"""
        return f"{self.blob_name}"

    def update(self: Self) -> None:
        """Called by Ursina engine once per frame"""

        super().update()

        if not FPS.paused:

            if self.collision_cloud is not None and self.swallowed_by_blob is not None:

                self.collision_cloud.start(self.swallowed_by_blob)
                self.collision_cloud.setScale(urs.scene, self.radius)

                angle_pos = PanVec3(
                    self.getPos(self.swallowed_by_blob)
                    - self.swallowed_by_blob.getPos(self.swallowed_by_blob)
                ).normalized()

                self.collision_cloud.setPos(
                    self.swallowed_by_blob,
                    angle_pos,
                )

                self.swallowed_by_blob.collisions.append(self.collision_cloud)
                self._swallowed = True

            if len(self.collisions) > 0:
                if self.collision_cleanup_timer <= 0:
                    cloud = self.collisions.popleft()

                    cloud.cleanup()
                    del cloud
                    self.collision_cleanup_timer = 1.5
                else:
                    self.collision_cleanup_timer -= FPS.dt

        if self.text_entity is not None and self.info_text.enabled:

            self.text_entity.position = self.position
            self.text_entity.rotation = urs.camera.parent.rotation

            d = mf.distance(self.text_entity.world_position, urs.camera.world_position)

            self.text_entity.scale = self.text_scale * d
            self.text_entity.position += (self.text_entity.my_up) * (
                self.text_position / d
            )

            if self.text_on and self.text_full_details:
                self.text = self.full_overlay_text()

                self.info_text.text = self.text

        if not self.trail_ready:
            from .blob_watcher_registry_ursina import (
                BlobWatcherRegistryUrsina as blob_registry,
            )

            self.trail_ready = blob_registry.is_ready()

        if self.blob_name != CENTER_BLOB_NAME and self.light_node is not None:
            self.update_spotlight()

    def on_click(self: Self) -> None:
        """
        Calls the text overlay methods to toggle it on and off. Called when the mouse
        clicks on this blob while the simulation is paused
        """
        self.text_on = not self.text_on

        if self.text_on:
            self.create_text_overlay()
        else:
            if self.all_text_on:

                if self.is_moon and self.planet_text_only:
                    self.destroy_text_overlay()
                else:
                    self.update_text_background()
            else:
                self.destroy_text_overlay()

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
                self.destroy_trail()
            elif self.trail is None:
                self.create_trail()

        if not self.blob_name == CENTER_BLOB_NAME and not self.is_moon and key == "y":

            if round(self.scale_x) == round(self.radius):  # type: ignore
                self.scale = urs.Vec3(self.radius * 35)

            else:
                self.scale = urs.Vec3(self.radius)

            self.text_position = self.scale_x / self.text_position_pad

        if not self.blob_name == CENTER_BLOB_NAME and self.is_moon and key == "u":

            if round(self.scale_x) == round(self.radius):  # type: ignore
                size_factor: float = 10
                if hasattr(self.barycenter_blob, "is_rocky") or hasattr(
                    self.barycenter_blob, "is_gas"
                ):
                    if self.barycenter_blob.is_rocky:
                        size_factor = (
                            3 * (self.barycenter_blob.percent_radius / 25)
                        ) + 1.5
                    else:
                        size_factor = (
                            2 * ((self.barycenter_blob.percent_radius - 75) / 25)
                        ) + 7
                self.scale = urs.Vec3(self.radius * size_factor)
            else:
                self.scale = urs.Vec3(self.radius)

            self.text_position = self.scale_x / self.text_position_pad

    def on_disable(self: Self) -> None:
        """
        Called when this Entity is set to enabled=False. This calls clean up method for
        text overlay
        """
        self.destroy_text_overlay()

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""

        from .blob_watcher_registry_ursina import (
            BlobWatcherRegistryUrsina as blob_registry,
        )

        if self.trail is not None:
            urs.destroy(self.trail)

        if self.is_moon:
            self.barycenter_blob = None
            blob_registry.remove_moon(self)
        else:
            blob_registry.remove_planet(self)

        self.destroy_text_overlay()

        if self.light_node is not None and self.blob_name != CENTER_BLOB_NAME:
            self.rotator_model.clearLight()
            self.clearLight()

            if self.ring_texture is not None:
                self.light_node.removeNode()
                del self.light_node
        else:
            if self.light_node is not None:
                self.light_node.removeNode()
                del self.light_node

        super().on_destroy()

        self.enabled = False


class BlobSurfaceUrsina:
    """
    A class used to represent an object that draws a blob, with a distinction of the center blob

    Attributes
    ----------
    index: int
        An order number in a group of blobs
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
    ring_texture : str = None
        For 3d rendering, this is optional (implement as ring_texture = None in __init__)
    ring_scale : float = None
        Scale of ring relative to blob scale for gas blobs with rings, optional
    rotation_speed : float = None
        For 3d rendering, the speed (degrees per frame) at which the blob will spin
    rotation_pos : Tuple[float, float, float] = None
        For 3d rendering, the z,y,z angles of orientation of the blob (in degrees)
    position : Tuple[float,float,float] = (0,0,0)
        The x,y,z position for this blob
    barycenter_index : int
        The index of the blob that this blob orbits (used for moon blobs)

    Methods
    -------
    swallowed_by(blob: "BlobSurface") -> None
        Tells this blob what other blob is swallowing it

    set_barycenter(blob: "BlobSurface") -> None:
        Sets the blob that this blob orbits (used for moon blobs)

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
        "index",
        "_name",
        "_radius",
        "_mass",
        "_position",
        "color",
        "trail_color",
        "universe",
        "_texture",
        "ring_texture",
        "ring_scale",
        "_rotation_speed",
        "_rotation_pos",
        "ursina_center_blob_light",
        "ursina_blob",
        "_barycenter_index",
        "_swallowed",
    )

    center_blob_x: ClassVar[float] = 0
    center_blob_y: ClassVar[float] = 0
    center_blob_z: ClassVar[float] = 0
    center_blob: BlobCore = None
    universe_node: NodePath = None
    num_rings: int = 1

    def __init__(
        self: Self,
        index: int,
        name: str,
        radius: float,
        mass: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        ring_texture: str = None,
        ring_scale: float = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[float, float, float] = None,
    ):

        self._name: str = None
        self._texture: str = None
        self.ursina_blob: BlobCore = None
        self.index: int = index
        self.name: str = name
        self._radius: float = None
        self.radius = radius
        self._mass: float = None
        self.mass = mass
        self.color: Tuple[int, int, int] = color
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.texture: str = texture
        glow_map_name: str = None
        self.ring_texture: str = ring_texture
        self.ring_scale: float = ring_scale
        self._rotation_speed: float = None
        self._rotation_pos: Tuple[float, float, float] = None
        self._position: Tuple[float, float, float] = (0, 0, 0)
        self._barycenter_index: int = 0
        self.trail_color: urs.Color = urs.color.rgba(
            25 / 255, 100 / 255, 150 / 255, 0.9
        )
        self._swallowed: bool = False

        BlobSurfaceUrsina.universe_node = self.universe.universe

        urs_color: urs.Color = urs.color.rgba32(
            self.color[0], self.color[1], self.color[2], 255
        )

        if bg_vars.textures_3d:

            if index != 0 and self.texture is None:

                halfway_max_halfway: float = (
                    ((bg_vars.min_radius + bg_vars.max_radius) / 2) + bg_vars.max_radius
                ) / 2

                if self.radius >= (halfway_max_halfway):
                    i: int = blob_random.randint(0, len(BLOB_TEXTURES_GAS) - 1)
                    self.texture = BLOB_TEXTURES_GAS[i]
                    if (
                        BlobSurfaceUrsina.num_rings > 0
                        and (blob_random.random() * 100) > 50
                    ):
                        self.ring_texture = BLOB_TEXTURES_RINGS[i]

                        if self.ring_scale is None:
                            self.ring_scale = (blob_random.random() * 0.3) + 0.4
                        BlobSurfaceUrsina.num_rings -= 1

                elif self.radius >= bg_vars.min_radius:
                    self.texture = BLOB_TEXTURES_ROCKY[
                        blob_random.randint(0, len(BLOB_TEXTURES_ROCKY) - 1)
                    ]
                else:
                    self.texture = BLOB_TEXTURES_MOON[
                        blob_random.randint(0, len(BLOB_TEXTURES_MOON) - 1)
                    ]

        if rotation_speed is not None:
            self.rotation_speed = rotation_speed
        if rotation_pos is not None:
            self.rotation_pos = rotation_pos

        if color == CENTER_BLOB_COLOR:

            enabled: bool = not bg_vars.black_hole_mode
            glow_map_name = "glow_maps/8k_sun-glow_map.jpg"

            urs_color = urs.color.rgba(1.1, 1.1, 1.1, 1)
            self.texture = "suns/8k_sun.jpg"
            self.ring_texture = ""

            if not enabled:
                urs_color = urs.color.rgba(0, 0, 0, 0)

            if not bg_vars.textures_3d:
                urs_color = urs.color.rgb32(
                    CENTER_BLOB_COLOR[0], CENTER_BLOB_COLOR[1], CENTER_BLOB_COLOR[2]
                )
                texture = None
            self.ursina_blob = BlobCore(
                index=self.index,
                blob_name=self.name,
                position=(0, 0, 0),
                scale=urs.Vec3(self.radius, self.radius, self.radius),
                radius=self.radius,
                mass=self.mass,
                blob_material=SunMaterial().getMaterial(),
                texture_name=self.texture,
                glow_map_name=glow_map_name,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                color=urs_color,
                trail_color=self.trail_color,
                collider="sphere",
                enabled=enabled,
                # unlit=True,
                # shader=shd.unlit_shader,
            )
            self.ursina_blob.create_light()
            BlobSurfaceUrsina.center_blob = self.ursina_blob

        else:

            glow_map_name = None  # "glow_maps/no_glow_map.png"

            if not bg_vars.textures_3d:
                self.texture = None
            else:
                urs_color = urs.color.rgba(1, 1, 1, 1)

            self.ursina_blob = BlobCore(
                index=self.index,
                blob_name=self.name,
                position=(0, 0, 0),
                scale=urs.Vec3(self.radius, self.radius, self.radius),
                radius=self.radius,
                mass=self.mass,
                blob_material=PlanetMaterial().getMaterial(),
                texture_name=self.texture,
                glow_map_name=glow_map_name,
                ring_texture=self.ring_texture,
                ring_scale=self.ring_scale,
                center_light=BlobSurfaceUrsina.center_blob.light_node,
                color=urs_color,
                trail_color=self.trail_color,
                rotation_speed=self.rotation_speed,
                rotation_pos=self.rotation_pos,
                collider="sphere",
                unlit=True,
                shader=shd.unlit_shader,
            )

            if self.ring_texture is not None:
                self.ursina_blob.create_spotlight()

    @property
    def name(self: Self) -> str:

        if self.ursina_blob is not None:
            self._name = self.ursina_blob.blob_name
        return self._name

    @name.setter
    def name(self: Self, name: str) -> None:
        self._name = name

    @property
    def texture(self: Self) -> str:
        if self.ursina_blob is not None:
            self._texture = self.ursina_blob.texture_name

        return self._texture

    @texture.setter
    def texture(self: Self, texture: str) -> None:
        self._texture = texture

    @property
    def radius(self: Self) -> float:
        if self.ursina_blob is not None:
            return self.ursina_blob.radius
        else:
            return self._radius

    @radius.setter
    def radius(self: Self, radius: float) -> None:
        self._radius = radius

        if self.ursina_blob is not None and self.ursina_blob.radius != self._radius:
            self.ursina_blob.radius = self._radius

    @property
    def mass(self: Self) -> float:
        """Returns the mass of the blob"""
        if self.ursina_blob is not None:
            return self.ursina_blob.mass
        else:
            return self._mass

    @mass.setter
    def mass(self: Self, mass: float) -> None:
        """Sets the mass of the blob"""
        self._mass = mass

        if self.ursina_blob is not None and self.ursina_blob.mass != self._mass:
            self.ursina_blob.mass = self._mass

    @property
    def position(self: Self) -> Tuple[float, float, float]:
        if self.ursina_blob is not None:
            return tuple(self.ursina_blob.position)
        else:
            return self._position

    @position.setter
    def position(self: Self, position: Tuple[float, float, float]) -> None:
        self._position = position
        if self.ursina_blob is not None:
            self.ursina_blob.position = urs.Vec3(self._position)

    @property
    def rotation_pos(self: Self) -> Tuple[float, float, float]:
        """
        For 3d rendering, the z,y,z angles of orientation of the blob (in degrees)
        """
        if self.ursina_blob is not None:
            self._rotation_pos = self.ursina_blob.rotation_pos
        return self._rotation_pos

    @rotation_pos.setter
    def rotation_pos(self: Self, rotation: Tuple[float, float, float]) -> None:
        """
        Sets the rotation_pos attribute
        """
        self._rotation_pos = rotation

    @property
    def rotation_speed(self: Self) -> float:
        """For 3d rendering, the speed (degrees per frame) at which the blob will spin"""
        if self.ursina_blob is not None:
            self._rotation_speed = self.ursina_blob.rotation_speed
        return self._rotation_speed

    @rotation_speed.setter
    def rotation_speed(self: Self, rotation_speed: float) -> None:
        """Sets the rotation_speed attribute"""
        self._rotation_speed = rotation_speed

    @property
    def barycenter_index(self: Self) -> int:
        """The index of the blob that this blob orbits (used for moon blobs)"""
        if self.ursina_blob.barycenter_blob is not None:
            self._barycenter_index = self.ursina_blob.barycenter_blob.index
            return self.ursina_blob.barycenter_blob.index
        else:
            return self._barycenter_index

    @barycenter_index.setter
    def barycenter_index(self: Self, barycenter_index: int) -> None:
        self._barycenter_index = barycenter_index

    @property
    def swallowed(self: Self) -> bool:
        """Returns bool indicating if this blob has been swallowed"""
        return self.ursina_blob.swallowed

    @swallowed.setter
    def swallowed(self: Self, swallowed: bool) -> None:
        """Sets bool indicating if this blob has been swallowed"""
        self.ursina_blob.swallowed = swallowed

    def swallowed_by(self: Self, blob: "BlobSurface") -> None:
        """Tells this blob what other blob is swallowing it"""
        blob_u: BlobSurfaceUrsina = cast(BlobSurfaceUrsina, blob)
        self.ursina_blob.swallowed_by(blob_u.ursina_blob)

    def set_barycenter(self: Self, blob: BlobSurface) -> None:
        """Sets the blob that this blob orbits (used for moon blobs)"""
        u_blob: BlobSurfaceUrsina = cast(BlobSurfaceUrsina, blob)
        self.ursina_blob.barycenter_blob = u_blob.ursina_blob

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

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect
        """
        self.position = pos
        self.ursina_blob.light_node.setPos(urs.scene, urs.Vec3(pos))

    def on_destroy(self: Self) -> None:
        """Called when getting rid of this instance, so it can clean up"""
        self.destroy()

    def destroy(self: Self) -> None:
        """Called when getting rid of this instance, so it can clean up"""

        if self.index == 0:
            BlobSurfaceUrsina.center_blob = None

        urs.destroy(self.ursina_blob)
        self.ursina_blob = None
