"""
Newton's Laws, a simulator of physics at the scale of space

File for resource related vars or functions

by Jason Mott, copyright 2024
"""

import sys
from os import path
import pygame
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(resource_path(DISPLAY_FONT), STAT_FONT_SIZE)
        self.text = self.font.render(
            str(round(self.clock.get_fps(), 2)), True, (255, 255, 255), (19, 21, 21)
        )

    def render(self, display, x, y):
        self.text = self.font.render(
            str(round(self.clock.get_fps(), 2)), True, (255, 255, 255), (19, 21, 21)
        )
        display.blit(self.text, (x, y))
