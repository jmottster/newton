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
screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
pygame.display.set_caption("Newton's Laws")
img = pygame.image.load(resource_path(WINDOW_ICON))
pygame.display.set_icon(img)
clock = pygame.time.Clock()
stat_font = pygame.font.Font(resource_path(DISPLAY_FONT), 24)
blob_font = pygame.font.Font(resource_path(DISPLAY_FONT), 18)


# Get all the blobs ready to roll
blob_plotter = BlobPlotter()
blob_plotter.setup_blobs()

# Runtime behavior bools
running = True
paused = False
show_stats = True

while running:
    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                show_stats = not show_stats
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                blob_plotter.start_over()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                blob_plotter.square_grid = not blob_plotter.square_grid
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                blob_plotter.start_perfect_orbit = not blob_plotter.start_perfect_orbit

    # Fill the background
    screen.fill(BACKGROUND_COLOR)

    blob_plotter.draw_blobs(screen, blob_font)

    if show_stats:
        blob_plotter.draw_stats(screen, stat_font)

    # Flip the display
    pygame.display.flip()

    if not paused:
        # Apply changes
        blob_plotter.update_blobs()

    # ensure frame rate
    clock.tick(FRAME_RATE)

# Done! Time to quit.
pygame.quit()
