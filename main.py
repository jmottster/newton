"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2024
"""

import pygame
from resources import resource_path
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


pygame.init()

# Set up the window, frame rate clock, and fonts
screen = pygame.Surface([SCREEN_SIZE_W, SCREEN_SIZE_H])
display = pygame.display.set_mode([DISPLAY_SIZE_W, DISPLAY_SIZE_H], pygame.RESIZABLE)
pygame.display.set_caption("Newton's Blobs")
img = pygame.image.load(resource_path(WINDOW_ICON))
pygame.display.set_icon(img)
clock = pygame.time.Clock()
stat_font = pygame.font.Font(resource_path(DISPLAY_FONT), STAT_FONT_SIZE)
blob_font = pygame.font.Font(resource_path(DISPLAY_FONT), BLOB_FONT_SIZE)


# Get all the blobs ready to roll
blob_plotter = BlobPlotter(screen, display)
blob_plotter.plot_blobs()

# Runtime behavior bools
running = True
paused = False
show_stats = True
message = None
message_counter = 0
fullscreen = False
fullscreen_save_w = DISPLAY_SIZE_W
fullscreen_save_h = DISPLAY_SIZE_H
toggle_start_square_t = f"Toggled starting formation to square"
toggle_start_circular_t = f"Toggled starting formation to circular"

toggle_start_perfect_orbit = f"Toggled starting orbit to perfect velocities"
toggle_start_random_orbit = f"Toggled starting orbit to random velocities"

while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    blob_plotter.blobs[0].pause = True
                else:
                    blob_plotter.blobs[0].pause = False
            if event.key == pygame.K_d:
                show_stats = not show_stats
            if event.key == pygame.K_s:
                blob_plotter.start_over()
            if event.key == pygame.K_a:
                blob_plotter.square_grid = not blob_plotter.square_grid
                if blob_plotter.square_grid:
                    message = toggle_start_square_t
                else:
                    message = toggle_start_circular_t
                message_counter = 60 * 3
            if event.key == pygame.K_w:
                blob_plotter.start_perfect_orbit = not blob_plotter.start_perfect_orbit
                if blob_plotter.start_perfect_orbit:
                    message = toggle_start_perfect_orbit
                else:
                    message = toggle_start_random_orbit
                message_counter = 60 * 3
            if event.key == pygame.K_f:
                if fullscreen:
                    pygame.display.set_mode(
                        (fullscreen_save_w, fullscreen_save_h), pygame.RESIZABLE
                    )
                    fullscreen = False
                else:
                    fullscreen_save_w = display.get_width()
                    fullscreen_save_h = display.get_height()
                    pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    fullscreen = True

    # Fill the background, then draw stuff
    display.fill(BACKGROUND_COLOR)
    screen.fill(BACKGROUND_COLOR)

    blob_plotter.draw_blobs(blob_font)

    if show_stats:
        blob_plotter.draw_stats(stat_font, message)
        if message_counter > 0:
            message_counter -= 1
        else:
            message = None
            message_counter = 0

    # Flip the display
    pygame.display.flip()

    if not paused:
        # Apply changes
        blob_plotter.update_blobs()

    # ensure frame rate
    clock.tick(FRAME_RATE)

# Done! Time to quit.
pygame.quit()
