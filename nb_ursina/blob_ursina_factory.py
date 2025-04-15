"""
Newton's Laws, a simulator of physics at the scale of space

A class that implements an interface for a plugin object for providing
a graphics/drawing library to this simulator using Ursina

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, Tuple, Self, cast

import numpy.typing as npt
import math

from panda3d.core import AntialiasAttrib  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from newtons_blobs import MassiveBlob
from newtons_blobs import BlobVector as BVec3
from newtons_blobs import BlobSurface
from newtons_blobs import BlobDisplay
from newtons_blobs import BlobUniverse
from newtons_blobs import blob_random

from .blob_universe_ursina import BlobUniverseUrsina
from .blob_display_ursina import BlobDisplayUrsina
from .blob_first_person_surface import FirstPersonSurface
from .blob_watcher_registry_ursina import (
    BlobWatcherRegistryUrsina as blob_registry,
)
from .blob_surface_ursina import BlobCore, BlobSurfaceUrsina
from .blob_loading_screen_ursina import BlobLoadingScreenUrsina
from .fps import FPS
from .ursina_fix import BlobText
from .blob_utils_ursina import MathFunctions as mf

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

    reset(num_blobs: int = NUM_BLOBS) -> None
        Resets to default state

    new_blob_surface(index: int,
                     name: str,
                     radius: float,
                     mass: float,
                     color: Tuple[int, int, int],
                     texture: str = None,
                     ring_texture: str = None,
                     ring_scale: float = None,
                     rotation_speed : float = None,
                     rotation_pos: Tuple[int, int, int] = None) -> BlobSurface
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime

    loading_screen_start(max_count: int, bar_message: str = "loading blobs . . . ") -> None
        Method for staring a loading screen with max_count (reaching means done)
        and message (describe what is being done)

    loading_screen_add_count(increment: int = 1) -> None
        Must call loading_screen_start() first. This will add increment amount
        to display bar (which displays % toward max_count)

    loading_screen_is_at_max() -> bool
        Returns True if count has reached max_count via calls to
        loading_screen_add_count()

    loading_screen_end(screen_update: bool = True) -> None
        Call this to close out the current loading screen. You must call this
        if you want to the loading screen to go away, or before starting a new
        one.
     set_plot_radius(plot_radius: float) -> None
        Set the radius of where the farthest blob from the center is
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

        bg_vars.set_au_scale_factor(1.495978707 * 10**6)
        bg_vars.set_universe_scale(50)
        bg_vars.set_center_blob_scale(15)
        bg_vars.set_scale_center_blob_mass_with_size(True)
        bg_vars.set_black_hole_mode(False)
        if LOW_VRAM:
            bg_vars.set_center_blob_shadow_resolution(2048)
            bg_vars.set_blob_shadow_resolution(4096)
        bg_vars.set_blob_scale(15)
        bg_vars.set_scale_blob_mass_with_size(True)
        bg_vars.set_grid_cells_per_au(0.5)
        # bg_vars.set_start_pos_rotate_y(True)
        # bg_vars.set_start_pos_rotate_z(True)
        bg_vars.set_first_person_scale(bg_vars.max_radius * 0.75)
        bg_vars.set_background_scale(bg_vars.universe_size)
        if LOW_VRAM:
            bg_vars.set_background_scale(bg_vars.universe_size * 0.5)
        bg_vars.set_timescale(DAYS * 1)
        bg_vars.set_orig_timescale(DAYS * 1)
        bg_vars.set_timescale_inc(HOURS * 6)
        bg_vars.set_num_planets(5)
        bg_vars.set_textures_3d(True)
        bg_vars.set_start_perfect_orbit(True)
        bg_vars.set_start_angular_chaos(False)
        bg_vars.set_square_blob_plotter(False)
        bg_vars.set_center_blob_escape(True)
        bg_vars.set_wrap_if_no_escape(False)

        bg_vars.print_info()

        self.start_distance: float = bg_vars.au_scale_factor * 4 * bg_vars.num_planets

        self.num_moons: int = (NUM_BLOBS - bg_vars.num_planets) - 1

        BlobText.default_font = DISPLAY_FONT
        # BlobText.size = 0.5

        self.urs_display: BlobDisplayUrsina = BlobDisplayUrsina(
            DISPLAY_SIZE_W, DISPLAY_SIZE_H
        )

        self.urs_universe: BlobUniverseUrsina = BlobUniverseUrsina(
            bg_vars.universe_size_w, bg_vars.universe_size_h
        )

        self.urs_display.first_person_surface = FirstPersonSurface(
            bg_vars.first_person_scale,
            (0, 0, 0),
            self.urs_universe,
        )

        blob_registry.set_first_person_viewer(
            self.urs_display.first_person_surface.first_person_viewer
        )

        self.first_person_blob: MassiveBlob = MassiveBlob(
            bg_vars.universe_size_h,
            -1,
            "first_person",
            cast(BlobSurface, self.urs_display.first_person_surface),
            bg_vars.min_mass,
            BVec3(0, 0, 0),
            BVec3(0, 0, 0),
        )

        self.default_start_pos: urs.Vec3 = urs.Vec3(
            urs.Vec3(self.urs_universe.get_center_blob_start_pos()) * bg_vars.scale_down
        )

        self.loading_screen: BlobLoadingScreenUrsina = None

        self.loading_screen_start(NUM_BLOBS)

        self.urs_display.update()

    def setup_start_pos(self: Self, center_pos: urs.Vec3) -> None:
        """Configures the starting position of the first person viewer"""

        temp_ent = urs.Entity(position=center_pos, shader=shd.unlit_shader, unlit=True)

        start_pos = center_pos + (
            urs.Vec3(
                blob_random.randint(-10, 10),
                blob_random.randint(-10, 10),
                blob_random.randint(-10, 10),
            ).normalized()
            * self.start_distance
        )

        # start_pos = center_pos + urs.Vec3((0, -self.start_distance, 0))

        self.urs_display.first_person_surface.draw(start_pos)

        self.urs_display.first_person_surface.first_person_viewer.lookAt(
            temp_ent, self.urs_display.first_person_surface.first_person_viewer.my_up
        )
        self.urs_display.first_person_surface.first_person_viewer.setup_lock()

        urs.destroy(temp_ent)

        self.first_person_blob.update_pos_vel(
            BVec3(*start_pos),
            BVec3(0, 0, 0),
        )

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        A dict will be sent to this method. so the implementor can load the dict up with
        attributes that are desired to be saved (if saving is turned on)
        """
        data["center_blob_scale"] = bg_vars.center_blob_scale
        data["scale_center_blob_mass_with_size"] = (
            bg_vars.scale_center_blob_mass_with_size
        )
        data["blob_scale"] = bg_vars.blob_scale
        data["scale_blob_mass_with_size"] = bg_vars.scale_blob_mass_with_size
        data["background_texture"] = self.urs_universe.texture

    def set_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        A dict instance will be sent to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs()) (if saving is turned on)

        """
        self.urs_universe.width = data["universe_size_w"] * bg_vars.au_scale_factor
        self.urs_universe.height = data["universe_size_h"] * bg_vars.au_scale_factor

        if data.get("center_blob_scale") is not None:
            bg_vars.set_center_blob_scale(data["center_blob_scale"])

        if data.get("scale_center_blob_mass_with_size") is not None:
            bg_vars.set_scale_center_blob_mass_with_size(
                data["scale_center_blob_mass_with_size"]
            )

        if data.get("blob_scale") is not None:
            bg_vars.set_blob_scale(data["blob_scale"])

        if data.get("scale_blob_mass_with_size") is not None:
            bg_vars.set_scale_blob_mass_with_size(data["scale_blob_mass_with_size"])

        self.urs_universe.set_universe_entity(
            bg_vars.background_scale, data.get("background_texture")
        )

        self.setup_start_pos(
            urs.Vec3(
                data["blobs"][0]["x"], data["blobs"][0]["y"], data["blobs"][0]["z"]
            )
            * bg_vars.scale_down
        )

        if data["paused"]:
            self.urs_display.paused = True

        if not data["show_stats"]:
            self.urs_display.urs_keyboard_events[self.urs_display.get_key_code("2")]()

        if not data["fullscreen"]:
            self.urs_display.set_mode(
                (data["fullscreen_save_w"], data["fullscreen_save_h"]),
                BlobDisplay.RESIZABLE,
            )

    def reset(self: Self, num_blobs: int = NUM_BLOBS) -> None:
        """Resets to default state"""

        blob_registry.reset()

        self.urs_display.first_person_surface.first_person_viewer.stop_following()

        blob_registry.set_first_person_viewer(
            self.urs_display.first_person_surface.first_person_viewer
        )

        self.urs_display.clear_stats()

        BlobSurfaceUrsina.num_rings = 1

        mf.camera_mask_counter = 0

        if num_blobs > 0:

            self.loading_screen_start(num_blobs)

            self.urs_display.update()

    def new_blob_surface(
        self: Self,
        index: int,
        name: str,
        radius: float,
        mass: float,
        color: Tuple[int, int, int],
        texture: str = None,
        ring_texture: str = None,
        ring_scale: float = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ) -> BlobSurface:
        """
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime
        """
        new_blob: BlobSurfaceUrsina = BlobSurfaceUrsina(
            index,
            name,
            radius,
            mass,
            color,
            self.get_blob_universe(),
            texture,
            ring_texture,
            ring_scale,
            rotation_speed,
            rotation_pos,
        )

        if name != CENTER_BLOB_NAME:
            if index <= self.num_moons:
                blob_registry.add_moon(new_blob.ursina_blob)
            else:
                blob_registry.add_planet(new_blob.ursina_blob)

        self.loading_screen_add_count()

        if self.loading_screen_is_at_max():
            blob_registry.purge_none_elements()
            self.setup_start_pos(self.default_start_pos)
            self.loading_screen_end(False)

        return cast(
            BlobSurface,
            new_blob,
        )

    def loading_screen_start(
        self: Self, max_count: int, bar_message: str = "loading blobs . . . "
    ) -> None:
        """
        Method for staring a loading screen with max_count (reaching means done)
        and message (describe what is being done)
        """
        if self.loading_screen is not None:
            self.loading_screen.enabled = False
            urs.destroy(self.loading_screen)
            self.loading_screen = None

        self.loading_screen = BlobLoadingScreenUrsina(
            max_value=max_count, bar_message=bar_message
        )

        self.loading_screen.enabled = True

        self.urs_display.update()

    def loading_screen_add_count(self: Self, increment: int = 1) -> None:
        """
        Must call loading_screen_start() first. This will add increment amount
        to display bar (which displays % toward max_count)
        """
        if self.loading_screen is not None:
            self.loading_screen.add_to_bar(increment)
            self.urs_display.update()

    def loading_screen_is_at_max(self: Self) -> bool:
        """
        Returns True if count has reached max_count via calls to
        loading_screen_add_count()
        """
        return self.loading_screen.bar_at_max()

    def loading_screen_end(self: Self, screen_update: bool = True) -> None:
        """
        Call this to close out the current loading screen. You must call this
        if you want to the laoding screen to go away, or before starting a new
        one.
        """
        if self.loading_screen is not None and self.loading_screen.enabled:
            self.loading_screen.enabled = False
            urs.destroy(self.loading_screen)
            self.loading_screen = None
            if screen_update:
                self.urs_display.update()

    def set_plot_radius(self: Self, plot_radius: float) -> None:
        """Set the radius of where the farthest blob from the center is"""
        self.start_distance = (plot_radius + AU) * bg_vars.scale_down
        self.setup_start_pos(self.default_start_pos)

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
        gk: Tuple[int, int, int] = self.first_person_blob.grid_key(
            self.first_person_blob.blob_surface.position
        )
        pg: npt.NDArray = proximity_grid
        blobs: npt.NDArray = None

        pos1: urs.Vec3 = urs.Vec3(self.first_person_blob.blob_surface.position)
        pos2: urs.Vec3 = None
        diff: urs.Vec3 = None
        touching: float = 0.0
        d: float = 0.0
        colliding: bool = False

        for z_i_offset in range(-1, 2):
            z = gk[2] + z_i_offset
            for x_i_offset in range(-1, 2):
                x = gk[0] + x_i_offset
                for y_i_offset in range(-1, 2):
                    y = gk[1] + y_i_offset
                    # Skip the corners of the cube, worth risking the occasional miss for the performance boost
                    if x_i_offset != 0 and y_i_offset != 0 and z_i_offset != 0:
                        continue
                    # do the thing here
                    try:
                        blobs = pg[x][y][z]
                    except:
                        continue
                    if blobs is not None:

                        for blob in blobs:
                            pos2 = urs.Vec3(blob.blob_surface.position)
                            touching = (
                                blob.blob_surface.ursina_blob.scale_x
                                + self.first_person_blob.blob_surface.radius
                            )
                            diff = urs.Vec3(pos1 - pos2)
                            d = math.sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)
                            if d <= touching:
                                touching += 20
                                diff = urs.Vec3(diff.normalized() * (touching - d))
                                self.urs_display.first_person_surface.first_person_viewer.position += (
                                    diff
                                )
                                colliding = True
                                pos1 = urs.Vec3(
                                    self.first_person_blob.blob_surface.position
                                )
        self.urs_display.first_person_surface.first_person_viewer.colliding = colliding
