"""
Newton's Laws, a simulator of physics at the scale of space

A class that holds and controls a drawing area intended for screen display
implements newtons_blobs.BlobDisplay

As well as an encapsulation class of the fps clock, 
with display output functionality added


by Jason Mott, copyright 2024
"""

from typing import Any, Callable, Dict, Self, Tuple, cast

import pygame

from newtons_blobs.resources import resource_path
from newtons_blobs.globals import *
from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.blob_display import BlobDisplay

from .blob_surface_pygame import BlobSurfacePygame

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
            resource_path(Path(DISPLAY_FONT)), STAT_FONT_SIZE
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
    """
    A class that holds and controls a drawing area intended for screen display
    implements newtons_blobs.BlobDisplay

    Attributes
    ----------
    size_w: float
        The desired width of the display in pixels
    size_h: float
        The desired height of the display in pixels

    Methods
    -------
    init_display() -> pygame.Surface
        Initiates and returns a pygame display instance configured for the current monitor.

    get_framework(self: Self) -> Any
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

    fps_render(pos: Tuple[float, float]) -> None
        Will print the current achieved rate on the screen

    set_mode(size: Tuple[float, float], mode: int) -> None
        Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)

    is_fullscreen() -> bool:
        Whether of not the display is in fullscreen mode (False if in windowed mode)

    fill(color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    blit_text(text: str, pos: Tuple[float, float], orientation: Tuple[int, int]) -> None
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)

    draw_universe(universe: BlobUniverse) -> None
        Draw the universe area inside the display area (note that universe may be larger than display)

    update() -> None
        Draw the prepared frame to the screen/window

    quit() -> None
        Exit the application
    """

    def __init__(self: Self, size_w: float, size_h: float):

        pygame.init()

        self.width: float = size_w
        self.height: float = size_h
        self.windowed_width = size_w
        self.windowed_height = size_h
        self.display: pygame.Surface = self.init_display()
        self.img: pygame.Surface = pygame.image.load(resource_path(Path(WINDOW_ICON)))
        self.fps: FPS = FPS()
        self.stat_font: pygame.font.Font = pygame.font.Font(
            resource_path(Path(DISPLAY_FONT)), STAT_FONT_SIZE
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

    def get_framework(self: Self) -> Any:
        """
        Returns the pygame.Surface instance that represents the display area. Must cast it since the interface requires
        a return type of Any
        """
        return self.display

    def get_windowed_width(self: Self) -> float:
        """
        Returns the default width of the non-fullscreen display object
        """
        return self.windowed_width

    def get_windowed_height(self: Self) -> float:
        """
        Returns the default height of the non-fullscreen display object
        """
        return self.windowed_height

    def get_width(self: Self) -> float:
        """Returns the current width of the display object"""
        return self.display.get_width()

    def get_height(self: Self) -> float:
        """Returns the current height of the display object"""
        return self.display.get_height()

    def get_key_code(self: Self, key: str) -> int:
        """
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict
        """
        return pygame.key.key_code(key)

    def check_events(
        self: Self, keyboard_events: Dict[int, Callable[[], None]]
    ) -> None:
        """
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.
        """
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keyboard_events[pygame.K_ESCAPE]()
            if event.type == pygame.KEYDOWN:
                if keyboard_events.get(event.key) is not None:
                    keyboard_events[event.key]()

    def fps_clock_tick(self: Self, fps: int) -> None:
        """Control the FPS rate by sending the desired rate here every frame of while loop"""
        self.fps.clock.tick(fps)

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        """Will print the current achieved rate on the screen"""
        self.fps.render(self.display, pos[0], pos[1] - (self.fps.text.get_height() * 2))

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        """Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)"""
        pygame.display.set_mode(size, self.modes[mode])

    def is_fullscreen(self: Self) -> bool:
        """Whether of not the display is in fullscreen mode (False if in windowed mode)"""
        return pygame.display.is_fullscreen()

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        self.display.fill(color)

    def blit_text(
        self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        """
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)
        """
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
        """
        Draw the universe area inside the display area (note that universe may be larger than display),
        for a frame of actual display to monitor.
        """
        self.display.blit(
            cast(pygame.Surface, universe.get_framework()),
            (
                (self.display.get_width() - universe.get_width()) / 2,
                (self.display.get_height() - universe.get_height()) / 2,
            ),
        )

    def update(self: Self) -> None:
        """Draw the prepared frame to the screen/window"""
        pygame.display.flip()

    def quit(self: Self) -> None:
        """Exit the application"""
        pygame.quit()
