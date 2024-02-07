"""
Newton's Laws, a simulator of physics at the scale of space

The class that runs the application

by Jason Mott, copyright 2024
"""

import pygame

from resources import resource_path, FPS
from blob_plotter import BlobPlotter
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobRunner:

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
        self.blob_font = pygame.font.Font(resource_path(DISPLAY_FONT), BLOB_FONT_SIZE)

        # Get all the blobs ready to roll
        self.blob_plotter = BlobPlotter(self.universe, self.display)
        self.blob_plotter.plot_blobs()

        # Runtime behavior bools
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
                    if event.key == pygame.K_q:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        if self.paused:
                            self.blob_plotter.blobs[0].pause = True
                        else:
                            self.blob_plotter.blobs[0].pause = False
                    if event.key == pygame.K_d:
                        self.show_stats = not self.show_stats
                    if event.key == pygame.K_s:
                        self.elapsed_time = 0
                        self.blob_plotter.start_over()
                    if event.key == pygame.K_a:
                        self.blob_plotter.square_grid = (
                            not self.blob_plotter.square_grid
                        )
                        if self.blob_plotter.square_grid:
                            self.message = self.toggle_start_square_t
                        else:
                            self.message = self.toggle_start_circular_t
                        self.message_counter = 60 * 3
                    if event.key == pygame.K_w:
                        self.blob_plotter.start_perfect_orbit = (
                            not self.blob_plotter.start_perfect_orbit
                        )
                        if self.blob_plotter.start_perfect_orbit:
                            self.message = self.toggle_start_perfect_orbit
                        else:
                            self.message = self.toggle_start_random_orbit
                        self.message_counter = 60 * 3
                    if event.key == pygame.K_f:
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

            self.render_frame()

        # While loop broke! Time to quit.
        pygame.quit()

    def render_frame(self):

        # Fill the background, then draw stuff
        self.display.fill(BACKGROUND_COLOR)
        self.universe.fill(BACKGROUND_COLOR)

        self.blob_plotter.draw_blobs(self.blob_font)

        if self.show_stats:
            self.blob_plotter.draw_stats(self.stat_font, self.message)
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
