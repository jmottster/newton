"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, Dict, Self, Tuple, cast

import pygame

from newtons_blobs.resources import resource_path
from newtons_blobs.globals import *
from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.blob_display import BlobDisplay

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class FPS:
    """
    An encapsulation of the fps clock, with display output functionality added

    Attributes
    ----------

    Methods
    -------
    render(display: pygame.Surface, x: float, y: float) -> None
        Renders the fps to the display object at x,y coordinates


    """

    def __init__(self: Self):
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.Font(
            resource_path(DISPLAY_FONT), STAT_FONT_SIZE
        )
        self.text: pygame.Surface = self.font.render(
            f"FPS {round(self.clock.get_fps(), 2)}",
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )

    def render(self: Self, display: pygame.Surface, x: float, y: float) -> None:
        """Renders the fps to the display object at x,y coordinates"""
        self.text = self.font.render(
            f"FPS {round(self.clock.get_fps(), 2)}",
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        display.blit(self.text, (x, y))


class BlobDisplayPygame:

    def __init__(self: Self, size_w: float, size_h: float):

        pygame.init()

        self.width: float = size_w
        self.height: float = size_h
        self.display: pygame.Surface = self.init_display()
        self.img: pygame.Surface = pygame.image.load(resource_path(WINDOW_ICON))
        self.fps: FPS = FPS()
        self.stat_font: pygame.font.Font = pygame.font.Font(
            resource_path(DISPLAY_FONT), STAT_FONT_SIZE
        )

        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_icon(self.img)

        self.modes: Dict[int, int] = {
            BlobDisplay.FULLSCREEN: pygame.FULLSCREEN,
            BlobDisplay.RESIZABLE: pygame.RESIZABLE,
        }

    def init_display(self: Self) -> pygame.Surface:
        """Initiates and returns a pygame display instance configured for the current monitor."""
        current_height = pygame.display.get_desktop_sizes()[0][1]

        if current_height < self.height:
            return pygame.display.set_mode(
                [current_height, current_height - 70], pygame.RESIZABLE
            )

        return pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        pygame.display.set_mode(size, self.modes[mode])

    def get_framework(self: Self) -> Any:
        return self.display

    def get_width(self: Self) -> float:
        return self.display.get_width()

    def get_height(self: Self) -> float:
        return self.display.get_height()

    def get_key_code(self: Self, key: str) -> int:
        return pygame.key.key_code(key)

    def check_events(
        self: Self, keyboard_events: Dict[int, Callable[[], None]]
    ) -> None:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keyboard_events[pygame.K_q]()
            if event.type == pygame.KEYDOWN:
                if keyboard_events.get(event.key) is not None:
                    keyboard_events[event.key]()

    def fps_clock_tick(self: Self, fps: int) -> None:
        self.fps.clock.tick(fps)

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        self.fps.render(self.display, pos[0], pos[1] - (self.fps.text.get_height() * 2))

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        self.display.fill(color)

    def blit_text(
        self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        text_surface = self.stat_font.render(
            text,
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )

        offset_x: float = 0.0
        offset_y: float = 0.0

        if orientation[0] == BlobDisplay.TEXT_RIGHT:
            offset_x = -text_surface.get_width()
        elif orientation[0] == BlobDisplay.TEXT_CENTER_x:
            offset_x = -text_surface.get_width() / 2

        if orientation[1] == BlobDisplay.TEXT_BOTTOM:
            offset_y = -text_surface.get_height()
        elif orientation[1] == BlobDisplay.TEXT_CENTER_y:
            offset_y = -text_surface.get_height() / 2
        elif orientation[1] == BlobDisplay.TEXT_TOP_PLUS:
            offset_y = text_surface.get_height()

        self.display.blit(
            text_surface,
            (
                pos[0] + offset_x,
                pos[1] + offset_y,
            ),
        )

    def draw_universe(self: Self, universe: BlobUniverse) -> None:
        """Draws the universe surface onto the display surface, for a frame of actual display to monitor."""
        self.display.blit(
            cast(pygame.Surface, universe.get_framework()),
            (
                (self.display.get_width() - universe.get_width()) / 2,
                (self.display.get_height() - universe.get_height()) / 2,
            ),
        )

    def update(self: Self) -> None:
        pygame.display.flip()

    def quit(self: Self) -> None:
        pygame.quit()
