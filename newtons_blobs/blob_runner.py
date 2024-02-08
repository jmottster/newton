"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

import pygame

from .resources import resource_path, FPS
from .blob_plotter import BlobPlotter
from .globals import *

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

    Methods
    -------
    load_keyboard_events()
        Populates a hash table that holds function references for key board events.

    getDisplay()
        Returns a pygame display instance configured for the current monitor.

    run()
        Starts the application and maintains the while loop.

    render_frame()
        Calls all the draw methods to display a frame on the screen/monitor

    get_elapsed_time_in(divisor)
        divisor: float number of seconds to divide clocked frames by (see constants)
        Returns int number of units determined by divisor. E.g., if YEARS is divisor,
        returns number of years elapsed since last start.

    display_elapsed_time()
        Draws the elapsed time to the screen/monitor


    """

    MINUTES = 60
    HOURS = MINUTES * 60
    DAYS = HOURS * 24
    YEARS = DAYS * 365.25

    def __init__(self):

        pygame.init()

        # Set up the window, frame rate clock, and fonts
        self.universe = pygame.Surface([UNIVERSE_SIZE_W, UNIVERSE_SIZE_H])
        self.display = self.getDisplay()
        pygame.display.set_caption("Newton's Blobs")
        self.img = pygame.image.load(resource_path(WINDOW_ICON))
        pygame.display.set_icon(self.img)
        self.fps = FPS()
        self.stat_font = pygame.font.Font(resource_path(DISPLAY_FONT), STAT_FONT_SIZE)

        # Get all the blobs ready to roll
        self.blob_plotter = BlobPlotter(
            self.universe.get_width(),
            self.universe.get_height(),
            self.display.get_width(),
            self.display.get_height(),
        )
        self.blob_plotter.plot_blobs(self.universe)

        # Store keyboard events
        self.keyboard_events = self.load_keyboard_events()

        # Runtime behavior vars
        self.running = True
        self.paused = False
        self.elapsed_time = 0
        self.show_stats = True
        self.message = None
        self.message_counter = 0
        self.fullscreen = False
        self.fullscreen_save_w = self.display.get_width()
        self.fullscreen_save_h = self.display.get_height()
        self.toggle_start_square_t = f"Toggled starting formation to square"
        self.toggle_start_circular_t = f"Toggled starting formation to circular"

        self.toggle_start_perfect_orbit = (
            f"Toggled starting orbit to perfect velocities"
        )
        self.toggle_start_random_orbit = f"Toggled starting orbit to random velocities"

    def load_keyboard_events(self):
        keyboard_events = {}

        def quit_game():
            self.running = False

        def psuse_game():
            self.paused = not self.paused
            if self.paused:
                self.blob_plotter.blobs[0].pause = True
            else:
                self.blob_plotter.blobs[0].pause = False

        def toggle_stats():
            self.show_stats = not self.show_stats

        def start_over():
            self.elapsed_time = 0
            self.blob_plotter.start_over(self.universe)

        def toggle_square_grid():
            self.blob_plotter.square_grid = not self.blob_plotter.square_grid
            if self.blob_plotter.square_grid:
                self.message = self.toggle_start_square_t
            else:
                self.message = self.toggle_start_circular_t
            self.message_counter = 60 * 3

        def toggle_perfect_orbit():
            self.blob_plotter.start_perfect_orbit = (
                not self.blob_plotter.start_perfect_orbit
            )
            if self.blob_plotter.start_perfect_orbit:
                self.message = self.toggle_start_perfect_orbit
            else:
                self.message = self.toggle_start_random_orbit
            self.message_counter = 60 * 3

        def toggle_fullscreen():
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

        keyboard_events[pygame.K_q] = quit_game
        keyboard_events[pygame.K_SPACE] = psuse_game
        keyboard_events[pygame.K_d] = toggle_stats
        keyboard_events[pygame.K_s] = start_over
        keyboard_events[pygame.K_a] = toggle_square_grid
        keyboard_events[pygame.K_w] = toggle_perfect_orbit
        keyboard_events[pygame.K_f] = toggle_fullscreen

        return keyboard_events

    def getDisplay(self):
        current_height = pygame.display.get_desktop_sizes()[0][1]

        if current_height < DISPLAY_SIZE_H:
            return pygame.display.set_mode(
                [current_height, current_height - 70], pygame.RESIZABLE
            )

        return pygame.display.set_mode(
            [DISPLAY_SIZE_W, DISPLAY_SIZE_H], pygame.RESIZABLE
        )

    def run(self):
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
        pygame.quit()

    def render_frame(self):

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

    def draw_universe(self):
        self.display.blit(
            self.universe,
            (
                (self.display.get_width() - self.universe.get_width()) / 2,
                (self.display.get_height() - self.universe.get_height()) / 2,
            ),
        )

    def draw_stats(self, stat_font, message=None):
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
            f"Blobs swallowed by Sun: {self.blob_plotter.blobs_swalled}",
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

    def get_elapsed_time_in(self, divisor):
        return round((self.elapsed_time * TIMESCALE) / divisor, 2)

    def display_elapsed_time(self):

        self.time_text = self.stat_font.render(
            f"Years elapsed: {self.get_elapsed_time_in(self.YEARS)}",
            True,
            (255, 255, 255),
            BACKGROUND_COLOR,
        )
        self.display.blit(self.time_text, (20, self.time_text.get_height() + 20))
