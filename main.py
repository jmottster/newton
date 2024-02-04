"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2024
"""

import pygame

from resources import resource_path, FPS
from massive_blob import MassiveBlob
from blob_plotter import BlobPlotter
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobRunner:

    MINUTES = 60
    HOURS = MINUTES * 60
    DAYS = HOURS * 24
    YEARS = DAYS * 365.25

    def __init__(self):

        self.pg = pygame
        self.pg.init()

        # Set up the window, frame rate clock, and fonts
        self.universe = self.pg.Surface([UNIVERSE_SIZE_W, UNIVERSE_SIZE_H])
        self.display = self.pg.display.set_mode(
            [DISPLAY_SIZE_W, DISPLAY_SIZE_H], self.pg.RESIZABLE
        )
        self.pg.display.set_caption("Newton's Blobs")
        self.img = self.pg.image.load(resource_path(WINDOW_ICON))
        self.pg.display.set_icon(self.img)
        self.fps = FPS()
        self.stat_font = self.pg.font.Font(resource_path(DISPLAY_FONT), STAT_FONT_SIZE)
        self.blob_font = self.pg.font.Font(resource_path(DISPLAY_FONT), BLOB_FONT_SIZE)

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
        self.fullscreen_save_w = DISPLAY_SIZE_W
        self.fullscreen_save_h = DISPLAY_SIZE_H
        self.toggle_start_square_t = f"Toggled starting formation to square"
        self.toggle_start_circular_t = f"Toggled starting formation to circular"

        self.toggle_start_perfect_orbit = (
            f"Toggled starting orbit to perfect velocities"
        )
        self.toggle_start_random_orbit = f"Toggled starting orbit to random velocities"

    def run(self):
        while self.running:
            # Check for events
            for event in self.pg.event.get():
                if event.type == self.pg.QUIT:
                    self.running = False
                if event.type == self.pg.KEYDOWN:
                    if event.key == self.pg.K_q:
                        self.running = False
                    if event.key == self.pg.K_SPACE:
                        self.paused = not self.paused
                        if self.paused:
                            self.blob_plotter.blobs[0].pause = True
                        else:
                            self.blob_plotter.blobs[0].pause = False
                    if event.key == self.pg.K_d:
                        self.show_stats = not self.show_stats
                    if event.key == self.pg.K_s:
                        self.elapsed_time = 0
                        self.blob_plotter.start_over()
                    if event.key == self.pg.K_a:
                        self.blob_plotter.square_grid = (
                            not self.blob_plotter.square_grid
                        )
                        if self.blob_plotter.square_grid:
                            self.message = self.toggle_start_square_t
                        else:
                            self.message = self.toggle_start_circular_t
                        self.message_counter = 60 * 3
                    if event.key == self.pg.K_w:
                        self.blob_plotter.start_perfect_orbit = (
                            not self.blob_plotter.start_perfect_orbit
                        )
                        if self.blob_plotter.start_perfect_orbit:
                            self.message = self.toggle_start_perfect_orbit
                        else:
                            self.message = self.toggle_start_random_orbit
                        self.message_counter = 60 * 3
                    if event.key == self.pg.K_f:
                        if self.fullscreen:
                            self.pg.display.set_mode(
                                (self.fullscreen_save_w, self.fullscreen_save_h),
                                self.pg.RESIZABLE,
                            )
                            self.fullscreen = False
                        else:
                            self.fullscreen_save_w = self.display.get_width()
                            self.fullscreen_save_h = self.display.get_height()
                            self.pg.display.set_mode((0, 0), self.pg.FULLSCREEN)
                            self.fullscreen = True

            self.render_frame()

        # While loop broke! Time to quit.
        self.pg.quit()

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
        self.pg.display.flip()

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
            (19, 21, 21),
        )
        self.display.blit(self.time_text, (20, self.time_text.get_height() + 20))


if __name__ == "__main__":
    blober = BlobRunner()
    blober.run()
