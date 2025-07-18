"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area intended for screen display

by Jason Mott, copyright 2025
"""

from typing import Any, Callable, ClassVar, Dict, Tuple, Self, Protocol

from .blob_universe import BlobUniverse

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobDisplay(Protocol):
    """
    Protocol class to represent an object that holds and controls a drawing
    area intended for screen display (the viewable area of the Universe object)

    Attributes
    ----------
    size_w: float
        The desired width of the display in pixels
    size_h: float
        The desired height of the display in pixels

    Methods
    -------
    get_framework() -> Any
        Returns the underlying framework implementation of the drawing area for display, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_windowed_width() -> float
        Returns the default width of the non-fullscreen display object

    get_windowed_height() -> float
        Returns the default height of the non-fullscreen display object

    get_width() -> float
        Returns the current width of the display object

    get_height() -> float
        Returns the current height of the display object

    get_key_code(key: str) -> int
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict

    check_events(keyboard_events: Dict[int, Callable[[], None]]) -> None
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.

    fps_clock_tick(fps: int) -> None
        Control the FPS rate by sending the desired rate here every frame of while loop

    fps_get_dt() -> float
        Returns the elapsed time for the previous frame in seconds

    fps_render(pos: Tuple[float, float]) -> None
        Will print the current achieved rate on the screen

    set_mode(size: Tuple[float, float], mode: int) -> None
        Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)

    is_fullscreen() -> bool:
        Whether of not the display is in fullscreen mode (False if in windowed mode)

    blit_text(text: str, pos: Tuple[float, float], orientation: Tuple[int, int]) -> None
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)

    update() -> None
        Draw the prepared frame to the screen/window

    quit() -> None
        Exit the application

    """

    FULLSCREEN: ClassVar[int] = 1
    RESIZABLE: ClassVar[int] = 2
    TEXT_LEFT: ClassVar[int] = 1
    TEXT_RIGHT: ClassVar[int] = 2
    TEXT_TOP: ClassVar[int] = 3
    TEXT_TOP_PLUS: ClassVar[int] = 4
    TEXT_BOTTOM: ClassVar[int] = 5
    TEXT_CENTER_x: ClassVar[int] = 6
    TEXT_CENTER_z: ClassVar[int] = 7

    size_w: float
    size_h: float
    paused: bool

    def get_framework(self: Self) -> Any:
        """
        Returns the underlying framework implementation of the drawing area for display, mostly for use
        in an implementation of BlobSurface within the same framework for direct access
        """
        pass

    def get_windowed_width(self: Self) -> float:
        """
        Returns the default width of the non-fullscreen display object
        """
        pass

    def get_windowed_height(self: Self) -> float:
        """
        Returns the default height of the non-fullscreen display object
        """
        pass

    def get_width(self: Self) -> float:
        """
        Returns the current width of the display object
        """
        pass

    def get_height(self: Self) -> float:
        """
        Returns the current height of the display object
        """
        pass

    def get_key_code(self: Self, key: str) -> int:
        """
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict
        """
        pass

    def check_events(
        self: Self, keyboard_events: Dict[int, Callable[[], None]]
    ) -> None:
        """
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.
        """
        pass

    def fps_clock_tick(self: Self, fps: int) -> None:
        """Control the FPS rate by sending the desired rate here every frame of while loop"""
        pass

    def fps_get_dt(self: Self) -> float:
        """Returns the elapsed time for the previous frame in seconds"""
        pass

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        """Will print the current achieved rate on the screen"""
        pass

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        """Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)"""
        pass

    def is_fullscreen(self: Self) -> bool:
        """Whether of not the display is in fullscreen mode (False if in windowed mode)"""
        pass

    def blit_text(
        self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        """
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)
        """
        pass

    def update(self: Self) -> None:
        """Draw the prepared frame to the screen/window"""
        pass

    def quit(self: Self) -> None:
        """Exit the application"""
        pass
