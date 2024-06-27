"""
Newton's Laws, a simulator of physics at the scale of space

A singleton class (accessed via a class instance) that tracks viewer position and displays trails on moons
around the closest planet blob.

by Jason Mott, copyright 2024
"""

from typing import ClassVar, Self

import numpy as np
import numpy.typing as npt

import ursina as urs  # type: ignore


from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars

from .blob_surface_ursina import Rotator

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class MoonWatcher(urs.Entity):
    """
    A class used to periodically check which moons are nearby, and thus turn on
    their trails (and turn off trails that are far away)

    Attributes
    ----------
    **kwargs

    self.num_moons : int
        The number of moons, used to create the array that will hold them.
        Set to int((NUM_BLOBS - 1) * bg_vars.blob_moon_percent)

    self.num_planets : int
        The number of planets, used to create the array that will hold them.
        Set to int((NUM_BLOBS - 1) - self.num_moons)

    self.planet_index_offset : int
        Used to turn planet number into a proper array index that begins at 0
        Set to self.num_moons + 1

    self.planets : npt.NDArray
        Array of planet blobs

    self.moons : npt.NDArray
        Array of moon blobs

    self.first_person_viewer : urs.Entity
        The Entity that represents the position of the player

    self._t : float
        Variable to track time intervals, when it reaches self.update_step, positions
        are checked to find which moons get trails

    self.update_step : float
        Time interval between position checks (in seconds)

    self.trail_on : bool
        Whether or not to check positions to turn on/off moon trails


    Methods
    -------

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

    input(key: str) -> None
        Called by Ursina when a key event happens (looks for T, to turn functionality on/off)

    update() -> None
        Called by Ursina once per frame. This is where all the checks happens and moon trails
        are turned on and off


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

        self.num_moons: int = int((NUM_BLOBS - 1) * bg_vars.blob_moon_percent)
        self.num_planets: int = int((NUM_BLOBS - 1) - self.num_moons)
        self.planet_index_offset: int = self.num_moons + 1

        self.planets: npt.NDArray = np.empty([self.num_planets], dtype=Rotator)
        self.moons: npt.NDArray = np.empty([self.num_moons], dtype=Rotator)

        self.first_person_viewer: urs.Entity = None

        self._t: float = 0
        self.update_step: float = 1

        self.trail_on: bool = False

    def set_first_person_viewer(self: Self, first_person_viewer: urs.Entity) -> None:
        """Sets the Entity that represents the position of the player"""
        self.first_person_viewer = first_person_viewer

    def add_planet(self: Self, planet: Rotator) -> None:
        """Adds a blob to the internal planet blob array"""
        self.planets[int(planet.blob_name) - self.planet_index_offset] = planet

    def add_moon(self: Self, moon: Rotator) -> None:
        """Adds a blob to the internal moon blob array"""
        self.moons[int(moon.blob_name) - 1] = moon

    def remove_planet(self: Self, planet: Rotator) -> None:
        """Removes a blob from the internal planet blob array"""
        self.planets = np.array(
            [k for k in self.planets if k.blob_name != planet.blob_name],
            dtype=Rotator,
        )

    def remove_moon(self: Self, moon: Rotator) -> None:
        """Removes a blob from the internal moon blob array"""
        self.moons = np.array(
            [k for k in self.moons if k.blob_name != moon.blob_name], dtype=Rotator
        )

    def input(self: Self, key: str) -> None:
        """Called by Ursina when a key event happens (looks for T, to turn functionality on/off)"""
        if key == "t":
            self.trail_on = not self.trail_on

    def update(self: Self) -> None:
        """
        Called by Ursina once per frame. This is where all the checks happens and moon trails
        are turned on and off
        """

        if self.trail_on:
            self._t += urs.time.dt
            if self._t >= self.update_step:

                distance: float = urs.distance(
                    self.first_person_viewer.world_position,
                    self.planets[0].world_position,
                )
                next_distance: float = 0
                closest: int = 0

                for i in range(1, len(self.planets)):
                    next_distance = urs.distance(
                        self.first_person_viewer.world_position,
                        self.planets[i].world_position,
                    )

                    if next_distance < distance:
                        distance = next_distance
                        closest = i

                for blob in self.moons:
                    if (
                        urs.distance(
                            blob.world_position, self.planets[closest].world_position
                        )
                        <= bg_vars.au_scale_factor
                    ):
                        if (
                            not blob.trail.enabled
                            or blob.barycenter_blob.blob_name
                            != self.planets[closest].blob_name
                        ):
                            blob.trail.enabled = True
                            if (
                                blob.barycenter_blob is None
                                or blob.barycenter_blob.blob_name
                                != self.planets[closest].blob_name
                            ):
                                blob.barycenter_blob = self.planets[closest]
                                blob.trail.barycenter_blob = self.planets[closest]

                            blob.trail.barycenter_last_pos = (
                                blob.trail.barycenter_blob.world_position
                            )

                    else:
                        blob.trail.enabled = False

                self._t = 0


class BlobMoonTrailRegistryUrsina:
    """
    A class used to act as a static wrapper to a singleton instance of MoonWatcher

    Attributes
    ----------
    moon_watcher : ClassVar[MoonWatcher]
        The singleton instance of MoonWatcher

    Methods
    -------

    BlobMoonTrailRegistryUrsina.get_moon_watch_instance() -> MoonWatcher
        Called by other methods, will create singleton instance if it doesn't already exist

    BlobMoonTrailRegistryUrsina.set_first_person_viewer(first_person_viewer: urs.Entity) -> None
        Sets the Entity that represents the position of the player

    BlobMoonTrailRegistryUrsina.add_planet(planet: Rotator) -> None
        Adds a blob to the internal planet blob array

    BlobMoonTrailRegistryUrsina.add_moon(moon: Rotator) -> None
        Adds a blob to the internal moon blob array

    BlobMoonTrailRegistryUrsina.remove_planet(planet: Rotator) -> None
        Removes a blob from the internal planet blob array

    BlobMoonTrailRegistryUrsina.remove_moon(moon: Rotator) -> None
        Removes a blob from the internal moon blob array

    """

    moon_watcher: ClassVar[MoonWatcher] = None

    @classmethod
    def get_moon_watch_instance(cls) -> MoonWatcher:
        """Called by other methods, will create singleton instance if it doesn't already exist"""
        if cls.moon_watcher is None:
            cls.moon_watcher = MoonWatcher()
        return cls.moon_watcher

    @classmethod
    def set_first_person_viewer(cls, first_person_viewer: urs.Entity) -> None:
        """Sets the Entity that represents the position of the player"""
        cls.get_moon_watch_instance().set_first_person_viewer(first_person_viewer)

    @classmethod
    def add_planet(cls, planet: Rotator) -> None:
        """Adds a blob to the internal planet blob array"""
        cls.get_moon_watch_instance().add_planet(planet)

    @classmethod
    def add_moon(cls, moon: Rotator) -> None:
        """Adds a blob to the internal moon blob array"""
        cls.get_moon_watch_instance().add_moon(moon)

    @classmethod
    def remove_planet(cls, planet: Rotator) -> None:
        """Removes a blob from the internal planet blob array"""
        cls.get_moon_watch_instance().remove_planet(planet)

    @classmethod
    def remove_moon(cls, moon: Rotator) -> None:
        """Removes a blob from the internal moon blob array"""
        cls.get_moon_watch_instance().remove_moon(moon)
