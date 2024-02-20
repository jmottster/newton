"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, Dict, Self

from .blob_plugin_factory import BlobPluginFactory
from .blob_save_load import BlobSaveLoad
from .globals import *
from .blob_plotter import BlobPlotter
from .blob_universe import BlobUniverse
from .blob_display import BlobDisplay

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobRunner:
    """
    A class used for managing the top level running of the app, especially the while loop
    checking for events

    Attributes
    ----------
    blob_factory: BlobPluginFactory
        An instance of BlobFactory loaded up with the required drawing libraries

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

    run() -> None
        Starts the application and maintains the while loop. This is the only method that ever gets called
        from an external source.

    render_frame() -> None
        Calls all the draw methods to display a frame on the screen/monitor

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

    def __init__(self: Self, blob_factory: BlobPluginFactory):

        # Set up the rendering objects
        self.universe: BlobUniverse = blob_factory.get_blob_universe()
        self.display: BlobDisplay = blob_factory.get_blob_display()

        # Get all the blobs ready to roll
        self.blob_plotter: BlobPlotter = BlobPlotter(
            self.universe.get_width(),
            self.universe.get_height(),
            self.display.get_width(),
            self.display.get_height(),
            blob_factory,
        )
        self.blob_save_load: BlobSaveLoad = BlobSaveLoad([self, self.blob_plotter])

        # Store keyboard events
        self.keyboard_events: Dict[int, Callable[[], None]] = (
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

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["auto_save_load"] = self.auto_save_load
        data["running"] = self.running
        data["paused"] = self.paused
        data["elapsed_time"] = self.elapsed_time
        data["show_stats"] = self.show_stats
        data["fullscreen"] = self.fullscreen
        data["fullscreen_save_w"] = self.fullscreen_save_w
        data["fullscreen_save_h"] = self.fullscreen_save_h

    def set_prefs(self: Self, data: Dict[str, Any]) -> None:
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
            self.keyboard_events[self.display.get_key_code("f")]()

    def load_keyboard_events(self: Self) -> Dict[int, Callable[[], None]]:
        """
        Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict
        """
        keyboard_events: Dict[int, Callable[[], None]] = {}

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
            self.blob_plotter.start_over()

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
                self.display.set_mode(
                    (self.fullscreen_save_w, self.fullscreen_save_h),
                    BlobDisplay.RESIZABLE,
                )
                self.fullscreen = False
            else:
                self.fullscreen_save_w = self.display.get_width()
                self.fullscreen_save_h = self.display.get_height()
                self.display.set_mode((0, 0), BlobDisplay.FULLSCREEN)
                self.fullscreen = True

        def toggle_auto_save_load() -> None:
            self.auto_save_load = not self.auto_save_load

            if self.auto_save_load:
                self.message = self.toggle_save_load_on
            else:
                self.message = self.toggle_save_load_off
            self.message_counter = 60 * 3

        keyboard_events[self.display.get_key_code("e")] = toggle_auto_save_load
        keyboard_events[self.display.get_key_code("q")] = quit_game
        keyboard_events[self.display.get_key_code("space")] = pause_game
        keyboard_events[self.display.get_key_code("d")] = toggle_stats
        keyboard_events[self.display.get_key_code("s")] = start_over
        keyboard_events[self.display.get_key_code("a")] = toggle_square_grid
        keyboard_events[self.display.get_key_code("w")] = toggle_perfect_orbit
        keyboard_events[self.display.get_key_code("f")] = toggle_fullscreen

        return keyboard_events

    def run(self: Self) -> None:
        """
        Starts the application and maintains the while loop. This is the only method that ever gets called
        from an external source.
        """

        self.auto_save_load = self.blob_save_load.load_value("auto_save_load")

        if self.auto_save_load:
            if not self.blob_save_load.load():
                self.blob_plotter.plot_blobs()
        else:
            self.blob_plotter.plot_blobs()

        while self.running:
            self.display.check_events(self.keyboard_events)

            self.render_frame()

        if self.auto_save_load:
            self.running = True
            self.blob_save_load.save()
        else:
            self.blob_save_load.save_value("auto_save_load", False)
        self.display.quit()

    def render_frame(self: Self) -> None:
        """Calls all the draw methods to display a frame on the screen/monitor"""

        self.display.fill(BACKGROUND_COLOR)
        self.universe.fill(BACKGROUND_COLOR)

        self.blob_plotter.draw_blobs()

        self.display.draw_universe(self.universe)

        if self.show_stats:
            self.draw_stats(self.message)
            if self.message_counter > 0:
                self.message_counter -= 1
            else:
                self.message = None
                self.message_counter = 0

            self.display_elapsed_time()

        if CLOCK_FPS:
            self.display.fps_render(
                (20, self.display.get_height() - 20),
            )

        self.display.update()

        if not self.paused:
            self.blob_plotter.update_blobs()
            self.elapsed_time += 1

        self.display.fps_clock_tick(FRAME_RATE)

    def draw_stats(self: Self, message: str = None) -> None:
        """
        Draws statistical information to the display instance, and if message is sent, will also draw that
        text in the middle of the display instance.
        """
        if message is not None:
            # Center, showing message, if any
            self.display.blit_text(
                message,
                (
                    (self.display.get_width() / 2),
                    (self.display.get_height() / 2),
                ),
                (BlobDisplay.TEXT_CENTER_x, BlobDisplay.TEXT_CENTER_y),
            )

        # Top left, showing sun mass
        self.display.blit_text(
            f"Sun mass: {self.blob_plotter.blobs[0].mass}",
            (
                20,
                20,
            ),
            (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_TOP),
        )

        # Top right, showing number of orbiting blobs
        self.display.blit_text(
            f"Orbiting blobs: {self.blob_plotter.blobs.size - 1}",
            (
                self.display.get_width() - 20,
                20,
            ),
            (BlobDisplay.TEXT_RIGHT, BlobDisplay.TEXT_TOP),
        )

        # Bottom left, showing number of blobs swallowed by the sun
        self.display.blit_text(
            f"Blobs swallowed by Sun: {self.blob_plotter.blobs_swallowed}",
            (
                20,
                self.display.get_height() - 20,
            ),
            (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM),
        )

        # Bottom right, showing number of blobs escaped the sun
        self.display.blit_text(
            f"Blobs escaped Sun: {self.blob_plotter.blobs_escaped}",
            (
                self.display.get_width() - 20,
                self.display.get_height() - 20,
            ),
            (BlobDisplay.TEXT_RIGHT, BlobDisplay.TEXT_BOTTOM),
        )

    def get_elapsed_time_in(self: Self, divisor: float) -> float:
        """
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns float number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.
        """
        return round((self.elapsed_time * TIMESCALE) / divisor, 2)

    def display_elapsed_time(self: Self) -> None:
        """Draws the elapsed time to the display instance"""
        self.display.blit_text(
            f"Years elapsed: {self.get_elapsed_time_in(self.YEARS)}",
            (20, 20),
            (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_TOP_PLUS),
        )
