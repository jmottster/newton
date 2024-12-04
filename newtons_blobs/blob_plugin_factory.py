"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class that defines an interface for a plugin object for providing
a graphics/drawing library to this simulator

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, Tuple, Self, Protocol

import numpy.typing as npt

from .blob_surface import BlobSurface
from .blob_display import BlobDisplay
from .blob_universe import BlobUniverse
from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPluginFactory(Protocol):
    """
    A Protocol class that defines an interface for a plugin object for providing
    a graphics/drawing library to this simulator

    Methods
    -------
    get_prefs(data: dict) -> None
        A dict will be sent to this method. so the implementor can load the dict up with attributes that are desired to be saved (if saving is turned on)

    set_prefs(data: dict) -> None
        A dict instance will be sent to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs()) (if saving is turned on)

    reset(self: Self) -> None
        Resets to default state

    new_blob_surface(name: str, radius: float, mass: float, color: Tuple[int, int, int], texture: str = None, ring_texture: str = None, rotation_speed : float = None, rotation_pos: Tuple[int, int, int] = None) -> BlobSurface
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
        if you want to the laoding screen to go away, or before starting a new
        one.

    get_blob_universe() -> BlobUniverse
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor

    get_blob_display() -> BlobDisplay
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor

    grid_check(proximity_grid: npt.NDArray):
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.

    """

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
        pass

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
        ring_texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ) -> BlobSurface:
        """
        Factory method for instantiating instances of an implementor of the BlobSurface interface,
        as implementation is not known at runtime
        """
        pass

    def loading_screen_start(
        self: Self, max_count: int, bar_message: str = "loading blobs . . . "
    ) -> None:
        """
        Method for staring a loading screen with max_count (reaching means done)
        and message (describe what is being done)
        """
        pass

    def loading_screen_add_count(self: Self, increment: int = 1) -> None:
        """
        Must call loading_screen_start() first. This will add increment amount
        to display bar (which displays % toward max_count)
        """
        pass

    def loading_screen_is_at_max(self: Self) -> bool:
        """
        Returns True if count has reached max_count via calls to
        loading_screen_add_count()
        """
        pass

    def loading_screen_end(self: Self, screen_update: bool = True) -> None:
        """
        Call this to close out the current loading screen. You must call this
        if you want to the laoding screen to go away, or before starting a new
        one.
        """
        pass

    def get_blob_universe(self: Self) -> BlobUniverse:
        """
        Returns a the single instance of a Universe object, intended to be the area that is drawn on.
        Can be larger than the display area, which represents the area shown on one's monitor
        """
        pass

    def get_blob_display(self: Self) -> BlobDisplay:
        """
        Returns the single instance of a Display object, intended to be the area of the Universe object
        that is shown on one's monitor
        """
        pass

    def grid_check(self: Self, proximity_grid: npt.NDArray):
        """
        Gives the graphics layer a chance to traverse the proximity grid for collision detection, etc.
        """
        pass
