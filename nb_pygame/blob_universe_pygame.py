"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class implementation to represent an object that holds and controls a drawing area for universe of blobs

by Jason Mott, copyright 2024
"""

from typing import Any, Tuple, Self

import pygame

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobUniversePygame:

    def __init__(self: Self, size_w: float, size_h: float):
        self.universe: pygame.Surface = pygame.Surface([size_w, size_h])

    def get_framework(self: Self) -> Any:
        return self.universe

    def get_width(self: Self) -> float:
        return self.universe.get_width()

    def get_height(self: Self) -> float:
        return self.universe.get_height()

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        self.universe.fill(color)
