"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area screen display

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, ClassVar, Dict, Tuple, Self, Protocol

from .blob_universe import BlobUniverse

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobDisplay(Protocol):

    FULLSCREEN: ClassVar[int] = 1
    RESIZABLE: ClassVar[int] = 2
    TEXT_LEFT: ClassVar[int] = 1
    TEXT_RIGHT: ClassVar[int] = 2
    TEXT_TOP: ClassVar[int] = 3
    TEXT_TOP_PLUS: ClassVar[int] = 4
    TEXT_BOTTOM: ClassVar[int] = 5
    TEXT_CENTER_x: ClassVar[int] = 6
    TEXT_CENTER_y: ClassVar[int] = 7

    size_w: float
    size_h: float

    def get_framework(self: Self) -> Any:
        pass

    def get_width(self: Self) -> float:
        pass

    def get_height(self: Self) -> float:
        pass

    def get_key_code(self: Self, key: str) -> int:
        pass

    def check_events(
        self: Self, keyboard_events: Dict[int, Callable[[], None]]
    ) -> None:
        pass

    def fps_clock_tick(self: Self, fps: int) -> None:
        pass

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        pass

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        pass

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        pass

    def blit_text(
        self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        pass

    def draw_universe(self: Self, universe: BlobUniverse) -> None:
        pass

    def update(self: Self) -> None:
        pass

    def quit(self: Self) -> None:
        pass
