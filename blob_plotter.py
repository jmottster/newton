"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial posisions and velocities of blobs and maintaining them

by Jason Mott, copyright 2024
"""
import pygame
import math
import random
from globals import *
from massive_blob import MassiveBlob

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPlotter:

    """
    A class used for setting up initial posisions and velocities of blobs and maintaining them

    Attributes
    ----------


    Methods
    -------
    setup_blobs()
        populates blob array according to global var values
    draw_blobs(screen, blob_font)
        draws the blobs on the screen (a PyGame screen), also draws a name label if that's turned on
    draw_stats(screen, stat_font)
        draws blob stats on the screen corners (mass of sun, number of blobs left, how many swallowed, how many escaped)
    update_blobs()
        applies collision detection, gravitational pull, and if activated, edge detection

    """

    def __init__(self):
        self.blobs = []
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.square_grid = SQUARE_BLOB_PLOTTER
        self.start_perfect_orbit = START_PERFECT_ORBIT

    def start_over(self):
        self.blobs = []
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.setup_blobs()

    def setup_blobs(self):
        # split the screen up into enough partitions for every blob
        if NUM_BLOBS > 9:
            blob_partition = round((SCALED_SCREEN_SIZE / math.sqrt(NUM_BLOBS)))
        else:
            blob_partition = SCALED_SCREEN_SIZE / 4

        # Set up the center blob, which will be the massive star all other blobs orbit
        x = SCALED_SCREEN_SIZE / 2
        y = SCALED_SCREEN_SIZE / 2

        self.blobs.append(
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

        # Blob placement grid, either square (if SQUARE_BLOB_PLOTTER True) or circular . . .

        # Interators for square grid placement
        y_count = 0
        y_turns = 0
        x_turns = 1

        # Interators for circular grid placement
        plot_rad = 0
        pi_inc = 0.25
        plot_radius = blob_partition

        for z in range(NUM_BLOBS - 1):
            # Set up some random values for this blob
            color = round(random.random() * (len(COLORS) - 1))
            radius = round((random.random() * (MAX_RADIUS - MIN_RADIUS)) + MIN_RADIUS)
            mass = (random.random() * (MAX_MASS - MIN_MASS)) + MIN_MASS

            if self.square_grid == True:  # Square grid x,y plot for this blob
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
            else:  # Circular grid x,y plot for this blob
                # Get x and y for this blob, vars set up from last interation or initial setting
                x = (SCALED_SCREEN_SIZE / 2) + math.cos(plot_rad) * plot_radius
                y = (SCALED_SCREEN_SIZE / 2) + math.sin(plot_rad) * plot_radius

                # Set up vars for next interation, move the "clock dial" another notch,
                # or make it longer by blob_partition if we've gone around 360 degrees
                if round(plot_rad, 8) == round((math.pi * 2) - (math.pi * pi_inc), 8):
                    plot_rad = 0
                    plot_radius += blob_partition
                    pi_inc = pi_inc / 2
                else:
                    plot_rad += math.pi * pi_inc

            # Figure out velocity for this blob
            dx = x - (SCALED_SCREEN_SIZE / 2)
            dy = y - (SCALED_SCREEN_SIZE / 2)

            velocity = 0
            if self.start_perfect_orbit == True:
                # get velocity for a perfect orbit around center blob
                d = math.sqrt(dx**2 + dy**2)
                velocity = math.sqrt(G * CENTER_BLOB_MASS / d)
            else:
                # Just use a random velocity
                velocity = (
                    random.random() * (MAX_VELOCITY - MIN_VELOCITY) + MIN_VELOCITY
                )

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
            self.blobs.append(
                MassiveBlob(
                    str(z + 1), COLORS[color], radius, mass, x, y, velocityx, velocityy
                )
            )

    def draw_blobs(self, screen, blob_font):
        # Draw the blobs
        for blob in self.blobs:
            # get rid of dead blobs
            if blob.dead == True:
                if blob.swallowed == True:
                    self.blobs_swalled += 1
                elif blob.escaped == True:
                    self.blobs_escaped += 1
                self.blobs.remove(blob)
                continue
            x, y = blob.x * SCALE, blob.y * SCALE
            pygame.draw.circle(
                screen,
                blob.color,
                (x, y),
                blob.radius,
            )
            # Uncomment for writting lables on blobs
            # mass_text = blob_font.render(f"{blob.name}", 1, (255, 255, 255), (0, 0, 0))
            # screen.blit(
            #     mass_text,
            #     (
            #         (blob.x * SCALE) - (mass_text.get_width() / 2),
            #         (blob.y * SCALE) - (mass_text.get_height() / 2),
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

    def draw_stats(self, screen, stat_font):
        # Top left, showing sun mass
        stat_text_top_left = stat_font.render(
            f"Sun mass: {self.blobs[0].mass}",
            1,
            (255, 255, 255),
            (19, 21, 21),
        )
        screen.blit(
            stat_text_top_left,
            (
                20,
                20,
            ),
        )

        # Top right, showing number of orbiting blobs
        stat_text_top_right = stat_font.render(
            f"Orbiting blobs: {len(self.blobs)-1}",
            1,
            (255, 255, 255),
            (19, 21, 21),
        )
        screen.blit(
            stat_text_top_right,
            (
                SCREEN_SIZE - stat_text_top_right.get_width() - 20,
                20,
            ),
        )

        # Bottom left, showing number of blobs swallowed by the sun
        stat_text_bottom_left = stat_font.render(
            f"Blobs swallowed by Sun: {self.blobs_swalled}",
            1,
            (255, 255, 255),
            (19, 21, 21),
        )
        screen.blit(
            stat_text_bottom_left,
            (
                20,
                SCREEN_SIZE - stat_text_bottom_left.get_height() - 20,
            ),
        )

        # Bottom right, showing number of blobs escaped the sun
        stat_text_bottom_right = stat_font.render(
            f"Blobs escaped Sun: {self.blobs_escaped}",
            1,
            (255, 255, 255),
            (19, 21, 21),
        )
        screen.blit(
            stat_text_bottom_right,
            (
                SCREEN_SIZE - stat_text_bottom_right.get_width() - 20,
                SCREEN_SIZE - stat_text_bottom_left.get_height() - 20,
            ),
        )

    def update_blobs(self):
        # set up hash to prevent double checking blob pairs for collision
        checked = {}

        # Check blobs
        for blob in self.blobs:
            # Check for and react to any collisions with other blobs
            for blob2 in self.blobs:
                if (id(blob2) != id(blob)) and (checked.get(id(blob2)) == None):
                    blob.collision_detection(blob2)  # TODO ghost collision detection
                blob.gravitational_pull(blob2, G)

            checked[id(blob)] = 1

            # Change direction or wrap if hitting the edge of screen
            # blob.edge_detection(screen, wrap)

            # Apply velocity
            blob.advance()
