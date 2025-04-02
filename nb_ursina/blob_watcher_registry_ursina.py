"""
Newton's Laws, a simulator of physics at the scale of space

A singleton class (accessed via a class instance) that tracks viewer position in relations to blobs and
coordinates interactions. Currently handles moon trails (only on around closest planet, and only if within 2 AU),
and shadow spotlight (only on for nearest planet, unless a ring planet)

by Jason Mott, copyright 2024
"""

from typing import ClassVar, Self

import numpy as np
import numpy.typing as npt

from panda3d.core import (  # type: ignore
    NodePath,
    Spotlight,
)  # type: ignore

import ursina as urs  # type: ignore
from ursina.ursinastuff import _destroy  # type: ignore
import ursina.shaders as shd  # type: ignore


from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars

from .blob_surface_ursina import BlobCore
from .blob_utils_ursina import MathFunctions as mf
from .fps import FPS

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobWatcher(urs.Entity):
    """
    A singleton class (accessed via a class instance) that tracks viewer position in relations to blobs and
    coordinates interactions. Currently handles moon trails (only on around closest planet, and only if within 2 AU),
    and shadow spotlight (only on for nearest planet, unless a ring planet)

    Attributes
    ----------
    **kwargs

    num_moons : int
        The number of moons, used to create the array that will hold them.
        Set to int(NUM_BLOBS - 1) - bg_vars.num_planets

    num_planets : int
        The number of planets, used to create the array that will hold them.
        Set to bg_vars.num_planets

    planet_index_offset : int
        Used to turn planet number into a proper array index that begins at 0
        Set to self.num_moons + 1

    planets : npt.NDArray
        Array of planet blobs

    moons : npt.NDArray
        Array of moon blobs

    self.first_person_viewer : urs.Entity
        The Entity that represents the position of the player

    _t : float
        Variable to track time intervals, when it reaches self.update_step, positions
        are checked to find which moons get trails

    update_step : float
        Time interval between position checks (in seconds)

    trail_on : bool
        Whether or not to check positions to turn on/off moon trails


    Methods
    -------

    create_nearby_light() -> None
        Creates a spotlight to be set to the nearest blob to the viewer at any given time, used to correct
        poor shadowing by the point light from center blob. Which blob has the reference at any given time
        is maintained in the update() method

    set_first_person_viewer(first_person_viewer: urs.Entity) -> None
        Sets the Entity that represents the position of the player

    add_planet(planet: Rotator) -> None
        Adds a blob to the internal planet blob array

    add_moon(moon: Rotator) -> None
        Adds a blob to the internal moon blob array

    remove_planet(planet: Rotator) -> None
        Removes a blob from the internal planet blob array

    remove_moon(moon: Rotator) -> None
        Removes a blob from the internal moon blob array

    purge_none_elements(self: Self) -> None
        Removes any None elements from the planets and moons arrays

    is_ready() -> bool
        Returns True if all blob arrays are full and the moon blobs all have a barycenter

    input(key: str) -> None
        Called by Ursina when a key event happens (looks for T, to turn functionality on/off)

    update() -> None
        Called by Ursina once per self.update_step seconds. This is where all the checks happens and moon trails
        are turned on and off

    find_nearest_planet() -> int
        Returns the index of the planet in self.planets that is
        closest to the first person view

    on_destroy() -> None
        Called by Ursina when this Entity is being destroyed. This cleans up references to first person viewer
        and blobs so they can be properly destroyed too


    """

    def __init__(
        self: Self,
        **kwargs,
    ):

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

        self.nearby_light: NodePath = None

        self.eternal = True

        self.num_moons: int = int(NUM_BLOBS - 1) - bg_vars.num_planets
        self.num_planets: int = bg_vars.num_planets
        self.planet_index_offset: int = self.num_moons + 1
        self.proximity: float = bg_vars.au_scale_factor * 2

        self.planets: npt.NDArray = np.empty([self.num_planets], dtype=BlobCore)
        self.moons: npt.NDArray = np.empty([self.num_moons], dtype=BlobCore)

        self.nearest_planet: int = -1

        self.first_person_viewer: urs.Entity = None

        self._t: float = 0
        self.update_step: float = 6

        self.trail_on: bool = False

        self._is_ready: bool = False

        self.create_nearby_light()

    def create_nearby_light(self: Self) -> None:
        """
        Creates a spotlight to be set to the nearest blob to the viewer at any given time, used to correct
        poor shadowing by the point light from center blob. Which blob has the reference at any given time
        is maintained in the update() method
        """

        if self.nearby_light is not None:
            return

        light: Spotlight = Spotlight(f"nearby_slight")
        light.setShadowCaster(
            True, bg_vars.blob_shadow_resolution, bg_vars.blob_shadow_resolution
        )
        light.setAttenuation((1, 0, 0))  # constant, linear, and quadratic.
        light.setColor((3, 3, 3, 1))

        self.nearby_light = self.attachNewNode(light)
        self.nearby_light.reparentTo(urs.scene)  # type: ignore

        light_scale: float = bg_vars.center_blob_radius

        self.nearby_light.setScale(urs.scene, light_scale)
        mf.camera_mask_counter += 1
        light_bit_mask = mf.bit_masks[mf.camera_mask_counter]
        self.nearby_light.node().setCameraMask(light_bit_mask)

        lens = self.nearby_light.node().getLens()
        far = bg_vars.max_radius * 30
        lens.setNearFar(
            500 / self.nearby_light.getSx(),
            far / self.nearby_light.getSx(),
        )
        lens.setFov(90)
        # self.nearby_light.node().showFrustum()

    def set_first_person_viewer(self: Self, first_person_viewer: urs.Entity) -> None:
        """Sets the Entity that represents the position of the player"""
        self.first_person_viewer = first_person_viewer

    def add_planet(self: Self, planet: BlobCore) -> None:
        """Adds a blob to the internal planet blob array"""
        self.planets[int(planet.index) - self.planet_index_offset] = planet

    def add_moon(self: Self, moon: BlobCore) -> None:
        """Adds a blob to the internal moon blob array"""
        self.moons[int(moon.index) - 1] = moon

    def remove_planet(self: Self, planet: BlobCore) -> None:
        """Removes a blob from the internal planet blob array"""
        self.planets = np.delete(self.planets, np.where(self.planets == planet)[0])

    def remove_moon(self: Self, moon: BlobCore) -> None:
        """Removes a blob from the internal moon blob array"""
        self.moons = np.delete(self.moons, np.where(self.moons == moon)[0])

    def purge_none_elements(self: Self) -> None:
        """Removes any None elements from the planets and moons arrays"""
        self.moons = np.delete(self.moons, np.where(self.moons == None)[0])
        self.planets = np.delete(self.planets, np.where(self.planets == None)[0])

    def is_ready(self: Self) -> bool:
        """Returns True if all blob arrays are full and the moon blobs all have a barycenter"""
        if not self._is_ready:
            self._is_ready = self.planets[-1] is not None and self.moons[-1] is not None

        return self._is_ready

    def input(self: Self, key: str) -> None:
        """Called by Ursina when a key event happens (looks for T, to turn functionality on/off)"""
        if key == "t":
            if self.is_ready():
                self.trail_on = not self.trail_on
                self._t = 0

    def update(self: Self) -> None:
        """
        Called by Ursina once per self.update_step seconds. This is where all the checks happens and moon trails
        are turned on and off
        """

        self._t += FPS.dt
        if self._t >= self.update_step:
            this_nearest_planet: int = -1

            if self.is_ready() and not self.trail_on:

                this_nearest_planet = self.find_nearest_planet()
                if (
                    this_nearest_planet >= 0
                    and this_nearest_planet != self.nearest_planet
                ):
                    self.planets[self.nearest_planet].unset_spotlight()
                    self.nearest_planet = this_nearest_planet
                    self.planets[self.nearest_planet].set_spotlight(self.nearby_light)

                    for blob in self.moons:
                        blob.check_light_source()
            elif self.trail_on:

                this_nearest_planet = self.find_nearest_planet()
                if (
                    this_nearest_planet >= 0
                    and this_nearest_planet != self.nearest_planet
                ):
                    self.planets[self.nearest_planet].unset_spotlight()
                    self.nearest_planet = this_nearest_planet
                    self.planets[self.nearest_planet].set_spotlight(self.nearby_light)

                barycenter: BlobCore = self.first_person_viewer.follow_entity

                if barycenter is not None:
                    if (
                        mf.distance(
                            self.first_person_viewer.position,
                            barycenter.position,
                        )
                        > self.proximity
                    ):
                        barycenter = None

                if barycenter is None:
                    barycenter = self.planets[self.nearest_planet]

                for blob in self.moons:

                    if (
                        barycenter is not None
                        and mf.distance(blob.position, barycenter.position)
                        <= bg_vars.au_scale_factor
                        and blob.blob_name != barycenter.blob_name
                    ):

                        if (
                            blob.trail.barycenter_blob is None
                            or blob.trail.barycenter_blob.blob_name
                            != barycenter.blob_name
                        ):

                            blob.destroy_trail()
                            blob.create_trail(barycenter)
                            # blob.trail.barycenter_blob = barycenter

                        if not blob.trail.enabled:
                            blob.trail.enabled = True
                            blob.check_light_source()

                    else:
                        if blob.trail.enabled:
                            blob.trail.enabled = False
                            blob.check_light_source()

            self._t = 0

    def find_nearest_planet(self: Self) -> int:
        """
        Returns the index of the planet in self.planets that is
        closest to the first person view
        """
        nearest_planet: int = -1
        next_distance: float = 0
        distance: float = mf.distance(
            self.first_person_viewer.position,
            self.planets[0].position,
        )
        if distance <= self.proximity:
            nearest_planet = 0
        for i in range(1, len(self.planets)):
            next_distance = mf.distance(
                self.first_person_viewer.position,
                self.planets[i].position,
            )

            if next_distance < distance:
                distance = next_distance
                if distance <= self.proximity:
                    nearest_planet = i

        return nearest_planet

    def on_destroy(self: Self) -> None:
        """
        Called by Ursina when this Entity is being destroyed. This cleans up references to first person viewer
        and blobs so they can be properly destroyed too
        """

        self.first_person_viewer = None
        for i in range(0, len(self.planets)):
            if self.planets[i] is not None:
                self.planets[i].unset_spotlight()
                self.planets[i] = None
        self.planets = None

        for i in range(0, len(self.moons)):
            if self.moons[i] is not None:
                self.moons[i].check_light_source()
                self.moons[i] = None
        self.moons = None

        if self.nearby_light is not None:
            self.clearLight()
            self.nearby_light.removeNode()
            del self.nearby_light


class BlobWatcherRegistryUrsina:
    """
    A class used to act as a static wrapper to a singleton instance of BlobWatcher

    Attributes
    ----------
    moon_watcher : ClassVar[BlobWatcher]
        The singleton instance of BlobWatcher

    Methods
    -------

    BlobWatcherRegistryUrsina.reset() -> None
        Will delete the singleton instance of BlobWatcher, which will create a new one
        when any other method is subsequently called

    BlobWatcherRegistryUrsina.get_moon_watch_instance() -> BlobWatcher
        Called by other methods, will create singleton instance if it doesn't already exist

    BlobWatcherRegistryUrsina.set_first_person_viewer(first_person_viewer: urs.Entity) -> None
        Sets the Entity that represents the position of the player

    BlobWatcherRegistryUrsina.add_planet(planet: Rotator) -> None
        Adds a blob to the internal planet blob array

    BlobWatcherRegistryUrsina.add_moon(moon: Rotator) -> None
        Adds a blob to the internal moon blob array

    BlobWatcherRegistryUrsina.remove_planet(planet: Rotator) -> None
        Removes a blob from the internal planet blob array

    BlobWatcherRegistryUrsina.remove_moon(moon: Rotator) -> None
        Removes a blob from the internal moon blob array

    BlobWatcherRegistryUrsina.purge_none_elements(self: Self) -> None
        Removes any None elements from the planets and moons arrays

    BlobWatcherRegistryUrsina.is_ready() -> bool
        Returns True if all blob arrays are full and the moon blobs all have a barycenter

    """

    blob_watcher: ClassVar[BlobWatcher] = None

    @classmethod
    def reset(cls) -> None:
        """
        Will delete the singleton instance of BlobWatcher, which will create a new one
        when any other method is subsequently called
        """

        for e in urs.scene.entities:
            if hasattr(e, "trail") and e.trail is not None:
                if hasattr(e, "input") and callable(e.input):
                    e.input("t")
        _destroy(cls.blob_watcher, True)
        cls.blob_watcher = None

    @classmethod
    def get_moon_watch_instance(cls) -> BlobWatcher:
        """Called by other methods, will create singleton instance if it doesn't already exist"""
        if cls.blob_watcher is None:
            cls.blob_watcher = BlobWatcher(shader=shd.unlit_shader, unlit=True)
        return cls.blob_watcher

    @classmethod
    def set_first_person_viewer(cls, first_person_viewer: urs.Entity) -> None:
        """Sets the Entity that represents the position of the player"""
        cls.get_moon_watch_instance().set_first_person_viewer(first_person_viewer)

    @classmethod
    def add_planet(cls, planet: BlobCore) -> None:
        """Adds a blob to the internal planet blob array"""
        cls.get_moon_watch_instance().add_planet(planet)

    @classmethod
    def add_moon(cls, moon: BlobCore) -> None:
        """Adds a blob to the internal moon blob array"""
        cls.get_moon_watch_instance().add_moon(moon)

    @classmethod
    def remove_planet(cls, planet: BlobCore) -> None:
        """Removes a blob from the internal planet blob array"""
        cls.get_moon_watch_instance().remove_planet(planet)

    @classmethod
    def remove_moon(cls, moon: BlobCore) -> None:
        """Removes a blob from the internal moon blob array"""
        cls.get_moon_watch_instance().remove_moon(moon)

    @classmethod
    def purge_none_elements(cls) -> None:
        """Removes any None elements from the planets and moons arrays"""
        cls.get_moon_watch_instance().purge_none_elements()

    @classmethod
    def is_ready(cls) -> bool:
        """Returns True if all blob arrays are full and the moon blobs all have a barycenter"""
        return cls.get_moon_watch_instance().is_ready()
