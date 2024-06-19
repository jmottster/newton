"""
Newton's Laws, a simulator of physics at the scale of space

An implementation class of the interface for a plugin object for providing
a graphics/drawing library to this simulator, based on Pygame

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, Tuple, Self, cast

import numpy.typing as npt


from newtons_blobs.globals import *
from newtons_blobs import BlobGlobalVars
from newtons_blobs import BlobSurface
from newtons_blobs import BlobDisplay
from newtons_blobs import BlobUniverse
from .blob_universe_pygame import BlobUniversePygame
from .blob_display_pygame import BlobDisplayPygame
from .blob_surface_pygame import BlobSurfacePygame


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPygameFactory:
    """
    An implementation class of the interface for a plugin object for providing
    a graphics/drawing library to this simulator, based on Pygame

    Attributes
    ----------

    Methods
    -------
    get_prefs(data: dict) -> None
        A dict will be sent to this method. so the implementor can load the dict up with attributes that are desired to be saved (if saving is turned on)

    set_prefs(data: dict) -> None
        A dict instance will be sent to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs()) (if saving is turned on)

    reset(self: Self) -> None
        Resets to default state

    new_blob_surface(name: str, radius: float, mass: float, color: Tuple[int, int, int], texture: str = None, rotation_speed : float = None, rotation_pos: Tuple[int, int, int] = None) -> BlobSurface
        Factory method for instantiating instances of an implementor of the BlobSurface interface

    get_blob_universe() -> BlobUniverse
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor

    get_blob_display() -> BlobDisplay
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor

    grid_check(proximity_grid: npt.NDArray):
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
    """

    def __init__(self: Self):

        BlobGlobalVars.set_au_scale_factor(100)
        BlobGlobalVars.set_universe_scale(40)
        BlobGlobalVars.set_center_blob_scale(30)
        BlobGlobalVars.set_scale_center_blob_mass_with_size(True)
        BlobGlobalVars.set_black_hole_mode(False)
        BlobGlobalVars.set_blob_scale(100)
        BlobGlobalVars.set_scale_blob_mass_with_size(True)
        BlobGlobalVars.set_grid_cells_per_au(1)
        # BlobGlobalVars.set_start_pos_rotate_y(True)
        # BlobGlobalVars.set_start_pos_rotate_z(True)
        BlobGlobalVars.set_timescale(DAYS * 2)
        BlobGlobalVars.set_timescale_inc(HOURS * 15)
        BlobGlobalVars.set_true_3d(False)
        # BlobGlobalVars.set_start_perfect_orbit(False)
        BlobGlobalVars.set_start_angular_chaos(False)
        # BlobGlobalVars.set_square_blob_plotter(True)
        BlobGlobalVars.set_center_blob_escape(False)
        BlobGlobalVars.set_wrap_if_no_escape(True)

        BlobGlobalVars.print_info()

        self.py_display: BlobDisplayPygame = BlobDisplayPygame(
            DISPLAY_SIZE_W, DISPLAY_SIZE_H
        )
        self.py_universe: BlobUniversePygame = BlobUniversePygame(
            BlobGlobalVars.universe_size_w, BlobGlobalVars.universe_size_h
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
        self.py_universe = BlobUniversePygame(
            data["universe_size_w"] * BlobGlobalVars.au_scale_factor,
            data["universe_size_h"] * BlobGlobalVars.au_scale_factor,
        )

        x_offset = 0
        y_offset = 0
        z_offset = 0
        center_blob_pos = self.py_universe.get_center_blob_start_pos()

        for blob_pref in data["blobs"]:
            if blob_pref["name"] == CENTER_BLOB_NAME:
                x_offset = center_blob_pos[0] - blob_pref["x"]
                y_offset = center_blob_pos[1] - blob_pref["y"]
                z_offset = center_blob_pos[2] - blob_pref["z"]
                blob_pref["x"] = center_blob_pos[0]
                blob_pref["y"] = center_blob_pos[1]
                blob_pref["z"] = center_blob_pos[2]
            else:
                blob_pref["x"] += x_offset
                blob_pref["y"] += y_offset
                blob_pref["z"] += z_offset

    def reset(self: Self, num_blobs: int = NUM_BLOBS) -> None:
        """Resets to default state"""
        pass

    def new_blob_surface(
        self: Self,
        name: str,
        radius: float,
        mass: float,
        color: Tuple[int, int, int],
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ) -> BlobSurface:
        """Factory method for instantiating instances of an implementor of the BlobSurface interface"""
        return cast(
            BlobSurface,
            BlobSurfacePygame(
                name,
                radius,
                mass,
                color,
                self.get_blob_universe(),
                texture,
                rotation_speed,
                rotation_pos,
            ),
        )

    def get_blob_universe(self: Self) -> BlobUniverse:
        """
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor
        """
        return cast(BlobUniverse, self.py_universe)

    def get_blob_display(self: Self) -> BlobDisplay:
        """
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
        """
        return cast(BlobDisplay, self.py_display)

    def grid_check(self: Self, proximity_grid: npt.NDArray):
        """
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
        """
        pass
