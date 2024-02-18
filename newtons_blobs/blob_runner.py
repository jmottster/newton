"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

from typing import Callable, Dict
import pygame

from .blob_save_load import BlobSaveLoad
from .resources import resource_path
from .globals import *
from .blob_plotter import BlobPlotter

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

    def __init__(self):
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

    def render(self, display: pygame.Surface, x: float, y: float) -> None:
        """Renders the fps to the display object at x,y coordinates"""
        self.text = self.font.render(
            f"FPS {round(self.clock.get_fps(), 2)}",
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        display.blit(self.text, (x, y))


class BlobRunner:
    """
    A class used for managing the top level running of the app, especially the while loop
    checking for events

    Attributes
    ----------

    Methods
    -------
    get_prefs(data: dict) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    set_prefs(data: dict, universe: pygame.Surface = None) -> None
        Sets this instances variables according to the key/value pairs in the provided dict, restoring the state
        saved in it. universe param is ignored, put there to conform with SavableLoadablePrefs protocol

    load_keyboard_events() -> Dict[int, Callable[[None], None]]
        Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict

    init_display() -> pygame.Surface
        Initiates and returns a pygame display instance configured for the current monitor.

    run() -> None
        Starts the application and maintains the while loop. This is the only method that ever gets called
        from an external source.

    render_frame() -> None
        Calls all the draw methods to display a frame on the screen/monitor

    draw_universe() -> None
        Draws the universe surface onto the display surface, for a frame of actual display to monitor.

    draw_stats(stat_font: pygame.font.Font, message: str =None) -> None
        Draws statistical information to the display instance, and if message is sent, will also draw that
        text in the middle of the display instance.

    get_elapsed_time_in(divisor: float) -> float
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns float number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.

    display_elapsed_time() -> None
        Draws the elapsed time to the display instance


    """

    MINUTES = 60
    HOURS = MINUTES * 60
    DAYS = HOURS * 24
    YEARS = DAYS * 365.25

    def __init__(self):

        pygame.init()

        # Set up the window, frame rate clock, and fonts
        self.universe: pygame.Surface = pygame.Surface(
            [UNIVERSE_SIZE_W, UNIVERSE_SIZE_H]
        )
        self.display: pygame.Surface = self.init_display()
        self.img: pygame.Surface = pygame.image.load(resource_path(WINDOW_ICON))
        self.fps: FPS = FPS()
        self.stat_font: pygame.font.Font = pygame.font.Font(
            resource_path(DISPLAY_FONT), STAT_FONT_SIZE
        )

        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_icon(self.img)

        # Get all the blobs ready to roll
        self.blob_plotter: BlobPlotter = BlobPlotter(
            self.universe.get_width(),
            self.universe.get_height(),
            self.display.get_width(),
            self.display.get_height(),
        )
        self.blob_save_load: BlobSaveLoad = BlobSaveLoad([self, self.blob_plotter])

        # Store keyboard events
        self.keyboard_events: Dict[int, Callable[[None], None]] = (
            self.load_keyboard_events()
        )

        # Runtime preferences/states
        self.auto_save_load: bool = AUTO_SAVE_LOAD
        self.running: bool = True
        self.paused: bool = False
        self.elapsed_time: int = 0
        self.show_stats: bool = True
        self.message: str = None
        self.message_counter: int = 0
        self.fullscreen: bool = False
        self.fullscreen_save_w: float = self.display.get_width()
        self.fullscreen_save_h: float = self.display.get_height()

        # Display text for option changes
        self.toggle_start_square_t: str = f"Toggled starting formation to square"
        self.toggle_start_circular_t: str = f"Toggled starting formation to circular"
        self.toggle_start_perfect_orbit_t: str = (
            f"Toggled starting orbit to perfect velocities"
        )
        self.toggle_start_random_orbit_t: str = (
            f"Toggled starting orbit to random velocities"
        )
        self.toggle_save_load_on: str = f"Toggled auto save/load to on"
        self.toggle_save_load_off: str = f"Toggled auto save/load to off"

    def get_prefs(self, data: dict) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["auto_save_load"] = self.auto_save_load
        data["running"] = self.running
        data["paused"] = self.paused
        data["elapsed_time"] = self.elapsed_time
        data["show_stats"] = self.show_stats
        data["fullscreen"] = self.fullscreen
        data["fullscreen_save_w"] = self.fullscreen_save_w
        data["fullscreen_save_h"] = self.fullscreen_save_h

    def set_prefs(self, data: dict, universe: pygame.Surface = None) -> None:
        """
        Sets this instances variables according to the key/value pairs in the provided dict, restoring the state
        saved in it. universe param is ignored, put there to conform with SavableLoadablePrefs protocol
        """
        self.auto_save_load = data["auto_save_load"]
        self.running = data["running"]
        self.paused = data["paused"]
        self.elapsed_time = data["elapsed_time"]
        self.show_stats = data["show_stats"]
        self.fullscreen = data["fullscreen"]
        self.fullscreen_save_w = data["fullscreen_save_w"]
        self.fullscreen_save_h = data["fullscreen_save_h"]

        if self.fullscreen:
            self.fullscreen = False
            self.keyboard_events[pygame.K_f]()

    def load_keyboard_events(self) -> Dict[int, Callable[[None], None]]:
        """Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict"""
        keyboard_events: Dict[int, Callable[[None], None]] = {}

        def quit_game() -> None:
            self.running = False

        def pause_game() -> None:
            self.paused = not self.paused
            if self.paused:
                self.blob_plotter.blobs[0].pause = True
            else:
                self.blob_plotter.blobs[0].pause = False

        def toggle_stats() -> None:
            self.show_stats = not self.show_stats

        def start_over() -> None:
            self.elapsed_time = 0
            self.blob_plotter.start_over(self.universe)

        def toggle_square_grid() -> None:
            self.blob_plotter.square_grid = not self.blob_plotter.square_grid
            if self.blob_plotter.square_grid:
                self.message = self.toggle_start_square_t
            else:
                self.message = self.toggle_start_circular_t
            self.message_counter = 60 * 3

        def toggle_perfect_orbit() -> None:
            self.blob_plotter.start_perfect_orbit = (
                not self.blob_plotter.start_perfect_orbit
            )
            if self.blob_plotter.start_perfect_orbit:
                self.message = self.toggle_start_perfect_orbit_t
            else:
                self.message = self.toggle_start_random_orbit_t
            self.message_counter = 60 * 3

        def toggle_fullscreen() -> None:
            if self.fullscreen:
                pygame.display.set_mode(
                    (self.fullscreen_save_w, self.fullscreen_save_h),
                    pygame.RESIZABLE,
                )
                self.fullscreen = False
            else:
                self.fullscreen_save_w = self.display.get_width()
                self.fullscreen_save_h = self.display.get_height()
                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.fullscreen = True

        def toggle_auto_save_load() -> None:
            self.auto_save_load = not self.auto_save_load

            if self.auto_save_load:
                self.message = self.toggle_save_load_on
            else:
                self.message = self.toggle_save_load_off
            self.message_counter = 60 * 3

        keyboard_events[pygame.K_e] = toggle_auto_save_load
        keyboard_events[pygame.K_q] = quit_game
        keyboard_events[pygame.K_SPACE] = pause_game
        keyboard_events[pygame.K_d] = toggle_stats
        keyboard_events[pygame.K_s] = start_over
        keyboard_events[pygame.K_a] = toggle_square_grid
        keyboard_events[pygame.K_w] = toggle_perfect_orbit
        keyboard_events[pygame.K_f] = toggle_fullscreen

        return keyboard_events

    def init_display(self) -> pygame.Surface:
        """Initiates and returns a pygame display instance configured for the current monitor."""
        current_height = pygame.display.get_desktop_sizes()[0][1]

        if current_height < DISPLAY_SIZE_H:
            return pygame.display.set_mode(
                [current_height, current_height - 70], pygame.RESIZABLE
            )

        return pygame.display.set_mode(
            [DISPLAY_SIZE_W, DISPLAY_SIZE_H], pygame.RESIZABLE
        )

    def run(self) -> None:
        """
        Starts the application and maintains the while loop. This is the only method that ever gets called
        from an external source.
        """

        self.auto_save_load = self.blob_save_load.load_value("auto_save_load")

        if self.auto_save_load:
            if not self.blob_save_load.load(self.universe):
                self.blob_plotter.plot_blobs(self.universe)
        else:
            self.blob_plotter.plot_blobs(self.universe)

        while self.running:
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if self.keyboard_events.get(event.key) is not None:
                        self.keyboard_events[event.key]()

            self.render_frame()

        # While loop broke! Time to quit.
        if self.auto_save_load:
            self.running = True
            self.blob_save_load.save()
        else:
            self.blob_save_load.save_value("auto_save_load", False)
        pygame.quit()

    def render_frame(self) -> None:
        """Calls all the draw methods to display a frame on the screen/monitor"""

        # Fill the background, then draw stuff
        self.display.fill(BACKGROUND_COLOR)
        self.universe.fill(BACKGROUND_COLOR)

        self.blob_plotter.draw_blobs()

        self.draw_universe()

        if self.show_stats:
            self.draw_stats(self.stat_font, self.message)
            if self.message_counter > 0:
                self.message_counter -= 1
            else:
                self.message = None
                self.message_counter = 0

            self.display_elapsed_time()

            if CLOCK_FPS:
                self.fps.render(
                    self.display,
                    20,
                    self.display.get_height() - (self.fps.text.get_height() * 2) - 20,
                )

        # Flip the display
        pygame.display.flip()

        if not self.paused:
            # Apply changes
            self.blob_plotter.update_blobs()

            self.elapsed_time += 1

        # ensure frame rate
        self.fps.clock.tick(FRAME_RATE)

    def draw_universe(self) -> None:
        """Draws the universe surface onto the display surface, for a frame of actual display to monitor."""
        self.display.blit(
            self.universe,
            (
                (self.display.get_width() - self.universe.get_width()) / 2,
                (self.display.get_height() - self.universe.get_height()) / 2,
            ),
        )

    def draw_stats(self, stat_font: pygame.font.Font, message: str = None) -> None:
        """
        Draws statistical information to the display instance, and if message is sent, will also draw that
        text in the middle of the display instance.
        """
        if message is not None:
            # Center, showing message, if any
            message_center = stat_font.render(
                message,
                1,
                (255, 255, 255),
                BACKGROUND_COLOR,
            )
            self.display.blit(
                message_center,
                (
                    (self.display.get_width() / 2) - (message_center.get_width() / 2),
                    (self.display.get_height() / 2) - (message_center.get_height() / 2),
                ),
            )

        # Top left, showing sun mass
        stat_text_top_left = stat_font.render(
            f"Sun mass: {self.blob_plotter.blobs[0].mass}",
            1,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(
            stat_text_top_left,
            (
                20,
                20,
            ),
        )

        # Top right, showing number of orbiting blobs
        stat_text_top_right = stat_font.render(
            f"Orbiting blobs: {self.blob_plotter.blobs.size - 1}",
            1,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(
            stat_text_top_right,
            (
                self.display.get_width() - stat_text_top_right.get_width() - 20,
                20,
            ),
        )

        # Bottom left, showing number of blobs swallowed by the sun
        stat_text_bottom_left = stat_font.render(
            f"Blobs swallowed by Sun: {self.blob_plotter.blobs_swallowed}",
            1,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(
            stat_text_bottom_left,
            (
                20,
                self.display.get_height() - stat_text_bottom_left.get_height() - 20,
            ),
        )

        # Bottom right, showing number of blobs escaped the sun
        stat_text_bottom_right = stat_font.render(
            f"Blobs escaped Sun: {self.blob_plotter.blobs_escaped}",
            1,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(
            stat_text_bottom_right,
            (
                self.display.get_width() - stat_text_bottom_right.get_width() - 20,
                self.display.get_height() - stat_text_bottom_left.get_height() - 20,
            ),
        )

    def get_elapsed_time_in(self, divisor: float) -> float:
        """
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns float number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.
        """
        return round((self.elapsed_time * TIMESCALE) / divisor, 2)

    def display_elapsed_time(self) -> None:
        """Draws the elapsed time to the display instance"""

        self.time_text = self.stat_font.render(
            f"Years elapsed: {self.get_elapsed_time_in(self.YEARS)}",
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(self.time_text, (20, self.time_text.get_height() + 20))
