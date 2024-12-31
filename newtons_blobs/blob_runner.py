"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, Dict, Self

from .globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from .blob_plugin_factory import BlobPluginFactory
from .blob_save_load import BlobSaveLoad
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
    get_prefs(data: Dict[str, Any]) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    set_prefs(data: Dict[str, Any]) -> None
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

    draw_stats(message: str =None) -> None
        Draws statistical information to the display instance, and if message is sent, will also draw that
        text in the middle of the display instance.

    get_elapsed_time_in(divisor: float) -> float
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns float number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.

    display_elapsed_time() -> None
        Draws the elapsed time to the display instance


    """

    def __init__(self: Self, blob_factory: BlobPluginFactory):

        # Set up the rendering objects
        self.blob_factory: BlobPluginFactory = blob_factory
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
        self.blob_save_load: BlobSaveLoad = BlobSaveLoad(
            [blob_factory, self, self.blob_plotter]
        )

        # Store keyboard events
        self.keyboard_events: Dict[int, Callable[[], None]] = (
            self.load_keyboard_events()
        )

        # Runtime preferences/states
        self.auto_save_load: bool = AUTO_SAVE_LOAD
        self.running: bool = True
        self.paused: bool = False
        self.elapsed_time: float = 0
        self.show_stats: bool = True
        self.message: str = None
        self.message_counter: int = 0
        self.fullscreen: bool = self.display.is_fullscreen()
        self.fullscreen_save_w: float = self.display.get_windowed_width()
        self.fullscreen_save_h: float = self.display.get_windowed_height()

        # Display text for option changes
        self.timescale_str: str = self.get_timescale_str()
        self.toggle_start_square_t: str = f"Toggled starting formation to square"
        self.toggle_start_circular_t: str = f"Toggled starting formation to circular"
        self.toggle_start_perfect_orbit_t: str = (
            f"Toggled starting orbit to perfect velocities"
        )
        self.toggle_start_random_orbit_t: str = (
            f"Toggled starting orbit to random velocities"
        )
        self.toggle_start_angular_chaos_t: str = (
            f"Toggled starting orbit with angular chaos"
        )
        self.toggle_start_no_angular_chaos_t: str = (
            f"Toggled starting orbit without angular chaos"
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

        self.fullscreen = not self.fullscreen
        self.keyboard_events[self.display.get_key_code("f")]()

    def get_timescale_str(self: Self) -> str:

        days: int = int(bg_vars.timescale / DAYS)
        hours: int = int(
            ((bg_vars.timescale) - (DAYS * int(bg_vars.timescale / DAYS))) / HOURS
        )
        minutes: int = int(
            ((bg_vars.timescale) - (HOURS * int(bg_vars.timescale / HOURS))) / MINUTES
        )
        seconds: int = int(
            ((bg_vars.timescale) - (MINUTES * int(bg_vars.timescale / MINUTES)))
        )

        return_str: str = ""

        if days > 0:
            return_str += f"{days} days"

        if hours > 0:
            if return_str != "":
                return_str += "-"
            return_str += f"{hours}h"
        elif (minutes + seconds) > 0:
            if return_str != "":
                return_str += "-0h"

        if minutes > 0:
            if return_str != "":
                return_str += "-"
            return_str += f"{minutes}m"
        elif seconds > 0:
            if return_str != "":
                return_str += "-0m"

        if seconds > 0:
            if return_str != "":
                return_str += "-"
            return_str += f"{seconds}s"

        return_str += "/sec"

        return return_str

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
            # if not self.show_stats:
            #     self.message = None
            #     self.message_counter = 0

        def start_over() -> None:
            self.elapsed_time = 0
            self.message = None
            self.message_counter = 0
            self.blob_plotter.start_over()
            self.blob_save_load.save(True, "last_blob_plot.json")

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

        def toggle_angular_chaos() -> None:
            self.blob_plotter.start_angular_chaos = (
                not self.blob_plotter.start_angular_chaos
            )
            if self.blob_plotter.start_angular_chaos:
                self.message = self.toggle_start_angular_chaos_t
            else:
                self.message = self.toggle_start_no_angular_chaos_t
            self.message_counter = 60 * 3

        def toggle_fullscreen() -> None:
            if self.fullscreen:
                self.display.set_mode(
                    (self.fullscreen_save_w, self.fullscreen_save_h),
                    BlobDisplay.RESIZABLE,
                )
                self.fullscreen = False
            else:
                if not self.display.is_fullscreen():
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

        def time_faster() -> None:
            if bg_vars.timescale < (bg_vars.timescale_inc):
                bg_vars.set_timescale(bg_vars.timescale_inc)
            else:
                bg_vars.set_timescale(bg_vars.timescale + (bg_vars.timescale_inc))

            self.timescale_str = self.get_timescale_str()
            self.message = f"Timescale is now {self.timescale_str}"
            self.message_counter = 60 * 2

        def time_slower() -> None:
            if bg_vars.timescale <= (bg_vars.timescale_inc):
                bg_vars.set_timescale(bg_vars.timescale_inc)
            else:
                bg_vars.set_timescale(bg_vars.timescale - (bg_vars.timescale_inc))
            self.timescale_str = self.get_timescale_str()
            self.message = f"Timescale is now {self.timescale_str}"
            self.message_counter = 60 * 2

        keyboard_events[self.display.get_key_code("escape")] = quit_game
        keyboard_events[self.display.get_key_code("space")] = pause_game
        keyboard_events[self.display.get_key_code("f")] = toggle_fullscreen
        keyboard_events[self.display.get_key_code("1")] = start_over
        keyboard_events[self.display.get_key_code("2")] = toggle_stats
        keyboard_events[self.display.get_key_code("3")] = toggle_auto_save_load
        keyboard_events[self.display.get_key_code("4")] = toggle_square_grid
        keyboard_events[self.display.get_key_code("5")] = toggle_perfect_orbit
        keyboard_events[self.display.get_key_code("6")] = toggle_angular_chaos
        keyboard_events[self.display.get_key_code("up")] = time_faster
        keyboard_events[self.display.get_key_code("down")] = time_slower
        keyboard_events[self.display.get_key_code("up arrow")] = time_faster
        keyboard_events[self.display.get_key_code("down arrow")] = time_slower

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
            self.universe = self.blob_factory.get_blob_universe()
        else:
            self.blob_plotter.plot_blobs()
            self.blob_save_load.save(True, "last_blob_plot.json")

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

        self.draw_stats(self.message)
        if self.message_counter > 0:
            self.message_counter -= 1
        else:
            self.message = None
            self.message_counter = 0

        if CLOCK_FPS:
            self.display.fps_render(
                (20, 20),
            )

        self.display.fps_clock_tick(FRAME_RATE)

        if not self.paused:
            self.blob_plotter.update_blobs(self.display.fps_get_dt())
            self.elapsed_time += bg_vars.timescale * self.display.fps_get_dt()

        self.display.update()

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
                (BlobDisplay.TEXT_CENTER_x, BlobDisplay.TEXT_CENTER_z),
            )

        if self.show_stats:
            # Top left, showing sun mass
            self.display.blit_text(
                f"Sun mass: {self.blob_plotter.blobs[0].mass}",
                (
                    20,
                    self.display.get_height() - 20,
                ),
                (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_TOP),
            )

            # Top right, showing number of orbiting blobs
            self.display.blit_text(
                f"Orbiting blobs: {self.blob_plotter.blobs.size - 1}",
                (
                    self.display.get_width() - 20,
                    self.display.get_height() - 20,
                ),
                (BlobDisplay.TEXT_RIGHT, BlobDisplay.TEXT_TOP),
            )

            # Bottom left, showing number of blobs swallowed by the sun
            self.display.blit_text(
                f"Blobs swallowed by Sun: {self.blob_plotter.blobs_swallowed}",
                (
                    20,
                    20,
                ),
                (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM),
            )

            if bg_vars.center_blob_escape:
                # Bottom right, showing number of blobs escaped the sun
                self.display.blit_text(
                    f"Blobs escaped Sun: {self.blob_plotter.blobs_escaped}",
                    (
                        self.display.get_width() - 20,
                        20,
                    ),
                    (BlobDisplay.TEXT_RIGHT, BlobDisplay.TEXT_BOTTOM),
                )

            self.display_elapsed_time()

    def get_elapsed_time_in(self: Self, divisor: float) -> float:
        """
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns float number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.
        """
        return round(self.elapsed_time / divisor, 2)

    def display_elapsed_time(self: Self) -> None:
        """Draws the elapsed time to the display instance"""
        text: str = ""
        if self.paused:
            text = "Paused"
        self.display.blit_text(
            f"Years elapsed: {self.get_elapsed_time_in(YEARS)} {text}\nTimescale: {self.timescale_str}",
            (20, self.display.get_height() - 20),
            (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_TOP_PLUS),
        )
