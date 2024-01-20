"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2024
"""

import sys
import pygame
import random
from os import path
from massive_blob import MassiveBlob
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


blobs = []
pygame.init()

# Set up the window, frame rate clock, and fonts
screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
pygame.display.set_caption("Newton's Laws")
img = pygame.image.load(resource_path("newton_icon.png"))
pygame.display.set_icon(img)
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 16)


def setup_blobs():
    # split the screen up into enough partitions for every blob
    blob_partition = round((SCALED_SCREEN_SIZE / math.sqrt(NUM_BLOBS)))

    # Set up the center blob, which will be the massive star all other blobs orbit
    x = SCALED_SCREEN_SIZE / 2
    y = SCALED_SCREEN_SIZE / 2

    blobs.append(
        MassiveBlob(
            CENTER_BLOB_NAME,
            CENTER_BLOB_COLOR,
            CENTER_BLOB_RADIUS,
            CENTER_BLOB_MASS,
            x,
            y,
            0,
            0,
        )
    )

    # Spiral around the center in a square grid of partitions,
    # one partition at a time, to place the other blobs
    y_count = 0
    y_turns = 0
    x_turns = 1
    for z in range(NUM_BLOBS - 1):
        # Set up some random values for this blob
        color = round(random.random() * (len(COLORS) - 1))
        radius = round((random.random() * (MAX_RADIUS - MIN_RADIUS)) + MIN_RADIUS)
        mass = (random.random() * (MAX_MASS - MIN_MASS)) + MIN_MASS

        # Get x and y coordinates for this blob
        # x and y take turns moving, each turn gives the other one more turn than
        # last time, which we need to do to spiral around in a square grid
        if y_turns == 0:
            x_turns -= 1
            if x_turns == 0:
                y_turns = y_count + 1
                y_count = 0

            if y <= (SCALED_SCREEN_SIZE / 2):
                x += blob_partition
            elif y > (SCALED_SCREEN_SIZE / 2):
                x -= blob_partition
        else:
            y_count += 1
            y_turns -= 1
            if y_turns == 0:
                x_turns = y_count + 1

            if x >= (SCALED_SCREEN_SIZE / 2):
                y += blob_partition
            elif x < (SCALED_SCREEN_SIZE / 2):
                y -= blob_partition

        dx = x - (SCALED_SCREEN_SIZE / 2)
        dy = y - (SCALED_SCREEN_SIZE / 2)

        velocity = 0
        if START_PERFECT_ORBIT == True:
            # get velocity for a perfect orbit around center blob
            d = math.sqrt(dx**2 + dy**2)
            velocity = math.sqrt(G * CENTER_BLOB_MASS / d)
        else:
            # Just use a random velocity
            velocity = random.random() * (MAX_VELOCITY - MIN_VELOCITY) + MIN_VELOCITY

        # Take our angle to the center and move it 90 degrees
        # to set an orbital trajectory
        rad = math.atan2(dy, dx)
        rad = rad + (math.pi * 0.5)
        # Set x and y velocities proportionate to orbital direction
        velocityx = math.cos(rad) * velocity
        velocityy = math.sin(rad) * velocity

        ## Make sure all velocities are pointing is the right direction

        # Adjust y velocities according to where they are on the x axis
        if x > (SCALED_SCREEN_SIZE / 2) and velocityy < 0:
            velocityy = -velocityy
        elif x < (SCALED_SCREEN_SIZE / 2) and velocityy > 0:
            velocityy = -velocityy

        # Adjust x velocities according to where they are on the y axis
        if y > (SCALED_SCREEN_SIZE / 2) and velocityx > 0:
            velocityx = -velocityx
        elif y < (SCALED_SCREEN_SIZE / 2) and velocityx < 0:
            velocityx = -velocityx

        # Phew, let's instantiate this puppy . . .
        blobs.append(
            MassiveBlob(
                str(z + 1), COLORS[color], radius, mass, x, y, velocityx, velocityy
            )
        )


# Get all the blobs ready to roll
setup_blobs()

# Run until the user asks to quit
running = True

while running:
    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill(BACKGROUND_COLOR)

    # Draw the blobs
    for blob in blobs:
        # get rid of dead blobs
        if blob.dead == True:
            blobs.remove(blob)
            continue
        x, y = blob.x * SCALE, blob.y * SCALE
        pygame.draw.circle(
            screen,
            blob.color,
            (x, y),
            blob.radius,
        )
        # Uncomment for writting lables on blobs
        # mass_text = font.render(
        #     f"D{blob.dead}, vx={blob.vx}, vy={blob.vy}",
        #     1,
        #     (255, 255, 255),
        # )
        # screen.blit(
        #     mass_text,
        #     (
        #         (blob.x * SCALE - mass_text.get_width() / 2),
        #         (blob.y * SCALE) - blob.radius - mass_text.get_height(),
        #     ),
        # )
        #
        # Ghosting not really working at the moment
        # if blob.ghosting == True:
        #     pygame.draw.circle(
        #         screen,
        #         blob.color,
        #         (blob.ghostx, blob.ghosty),
        #         blob.radius,
        #     )

    # Flip the display
    pygame.display.flip()

    # set up hash to prevent double checking blob pairs for collision
    checked = {}

    # Check blobs
    for blob in blobs:
        # Check for and react to any collisions with other blobs
        for blob2 in blobs:
            if (id(blob2) != id(blob)) and (checked.get(id(blob2)) == None):
                blob.collision_detection(blob2)  # TODO ghost collision detection
            blob.gravitational_pull(blob2, G)

        checked[id(blob)] = 1

        blob.advance()

        # Change direction or wrap if hitting the edge of screen
        # blob.edge_detection(screen, wrap)

    # ensure frame rate
    clock.tick(FRAME_RATE)

# Done! Time to quit.
pygame.quit()
