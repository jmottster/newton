"""
Newton's Laws, a simulator of physics at the scale of space

A class that implements an interface for a plugin object for providing
a graphics/drawing library to this simulator

by Jason Mott, copyright 2024
"""

import random
from typing import Any, Dict, Tuple, Self, cast

import numpy.typing as npt
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars
from newtons_blobs import MassiveBlob
from newtons_blobs import BlobSurface
from newtons_blobs import BlobDisplay
from newtons_blobs import BlobUniverse

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_display_ursina import BlobDisplayUrsina
from .blob_first_person_surface import FirstPersonSurface
from .blob_surface_ursina import BlobSurfaceUrsina

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUrsinaFactory:
    """
    A class that implements an interface for a plugin object for providing
    a graphics/drawing library to this simulator

    Methods
    -------
    def setup_start_pos() -> None
        Configures the starting position of the first person viewer

    get_prefs(data: dict) -> None
        A dict will be sent to this method. so the implementor can load the dict up with attributes that are desired to be saved (if saving is turned on)

    set_prefs(data: dict) -> None
        A dict instance will be sent to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs()) (if saving is turned on)

    reset(self: Self) -> None
        Resets to default state

    new_blob_surface(name: str, radius: float, color: Tuple[int, int, int], texture: str = None, rotation_speed: float = None, rotation_pos: Tuple[int, int, int] = None) -> BlobSurface
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime

    get_blob_universe() -> BlobUniverse
        Returns a single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor

    get_blob_display() -> BlobDisplay
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor

    grid_check(proximity_grid: npt.NDArray):
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
    """

    def __init__(self: Self):

        BlobGlobalVars.set_blob_scale(S / 6)
        # BlobGlobalVars.set_au_scale_factor(200)
        BlobGlobalVars.set_universe_scale(10)
        BlobGlobalVars.set_center_blob_scale(20)
        BlobGlobalVars.set_grid_cells_per_au(5)
        # BlobGlobalVars.set_start_pos_rotate_y(True)
        # BlobGlobalVars.set_start_pos_rotate_z(True)
        BlobGlobalVars.set_timescale(HOURS * 15)
        BlobGlobalVars.set_true_3d(True)
        # BlobGlobalVars.set_start_perfect_orbit(False)
        # BlobGlobalVars.set_start_angular_chaos(True)
        # BlobGlobalVars.set_square_blob_plotter(True)

        self.start_distance = (BlobGlobalVars.universe_size) / 2

        self.urs_display: BlobDisplayUrsina = BlobDisplayUrsina(
            DISPLAY_SIZE_W, DISPLAY_SIZE_H
        )

        self.urs_universe: BlobUniverseUrsina = BlobUniverseUrsina(
            BlobGlobalVars.universe_size_w, BlobGlobalVars.universe_size_h
        )

        self.urs_display.first_person_surface = FirstPersonSurface(
            self.start_distance,
            (0, 0, 0),
            self.urs_universe,
        )

        self.first_person_blob: MassiveBlob = MassiveBlob(
            BlobGlobalVars.universe_size_h,
            "first_person",
            cast(BlobSurface, self.urs_display.first_person_surface),
            MIN_MASS,
            0,
            0,
            0,
            0,
            0,
            0,
        )

        self.default_start_pos: urs.Vec3 = (
            urs.Vec3(self.urs_universe.get_center_blob_start_pos())
            * BlobGlobalVars.scale_down
        )

        self.setup_start_pos(self.default_start_pos)

    def setup_start_pos(self: Self, start_pos: urs.Vec3) -> None:
        """Configures the starting position of the first person viewer"""

        temp_ent = urs.Entity(position=start_pos)

        start_pos = start_pos + urs.Vec3(
            random.randint(-10, 10),
            random.randint(-10, 10),
            random.randint(-10, 10),
        ).normalized() * (self.start_distance)

        self.urs_display.first_person_surface.draw(start_pos)

        self.urs_display.first_person_surface.first_person_viewer.look_at(temp_ent)
        self.urs_display.first_person_surface.first_person_viewer.setup_lock()

        urs.destroy(temp_ent)

        self.first_person_blob.update_pos_vel(
            start_pos[0],
            start_pos[1],
            start_pos[2],
            0,
            0,
            0,
        )

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        A dict will be sent to this method. so the implementor can load the dict up with
        attributes that are desired to be saved (if saving is turned on)
        """
        pass

    def set_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        A dict instance will be sent to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs()) (if saving is turned on)

        """
        self.urs_universe.width = (
            data["universe_size_w"] * BlobGlobalVars.au_scale_factor
        )
        self.urs_universe.height = (
            data["universe_size_h"] * BlobGlobalVars.au_scale_factor
        )

        self.urs_universe.set_universe_entity(
            (data["blobs"][0]["radius"] * BlobGlobalVars.au_scale_factor) * 1000
        )

        self.setup_start_pos(
            urs.Vec3(
                data["blobs"][0]["x"], data["blobs"][0]["y"], data["blobs"][0]["z"]
            )
            * BlobGlobalVars.scale_down
        )

        if data["paused"]:
            urs.camera.ui.collider = None

        if not data["show_stats"]:
            self.urs_display.urs_keyboard_events[self.urs_display.get_key_code("2")]()

    def reset(self: Self) -> None:
        """Resets to default state"""
        self.setup_start_pos(self.default_start_pos)

    def new_blob_surface(
        self: Self,
        name: str,
        radius: float,
        color: Tuple[int, int, int],
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ) -> BlobSurface:
        """
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime
        """
        return cast(
            BlobSurface,
            BlobSurfaceUrsina(
                name,
                radius,
                color,
                self.get_blob_universe(),
                texture,
                rotation_speed,
                rotation_pos,
            ),
        )

    def get_blob_universe(self: Self) -> BlobUniverse:
        """
        Returns a single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor
        """
        return cast(BlobUniverse, self.urs_universe)

    def get_blob_display(self: Self) -> BlobDisplay:
        """
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
        """
        return cast(BlobDisplay, self.urs_display)

    def grid_check(self: Self, proximity_grid: npt.NDArray):
        """
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
        """
        pass
