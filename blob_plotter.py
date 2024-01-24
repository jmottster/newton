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
        self.z_axis = {}
        self.square_grid = SQUARE_BLOB_PLOTTER
        self.start_perfect_orbit = START_PERFECT_ORBIT
        self.start_perfect_floor_bounce = START_PERFECT_FLOOR_BOUNCE

    def start_over(self):
        self.blobs = []
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.z_axis = {}
        self.plot_blobs()

    def plot_blobs(self):
        # split the screen up into enough partitions for every blob
        if NUM_BLOBS > 9:
            blob_partition = round(((SCALED_SCREEN_SIZE) / math.sqrt(NUM_BLOBS)))
        else:
            blob_partition = SCALED_SCREEN_SIZE / 4

        half_screen = SCALED_SCREEN_SIZE / 2

        # Set up the center blob, which will be the massive star all other blobs orbit
        x = half_screen
        y = half_screen
        z = half_screen

        sun_blob = MassiveBlob(
            CENTER_BLOB_NAME,
            CENTER_BLOB_COLOR,
            CENTER_BLOB_RADIUS,
            CENTER_BLOB_MASS,
            x,
            y,
            z,
            0,
            0,
            0,
        )
        self.blobs.append(sun_blob)

        if self.z_axis.get(sun_blob.z) is None:
            self.z_axis[sun_blob.z] = []
        self.z_axis[sun_blob.z].append(sun_blob)

        # Blob placement grid, either square (if SQUARE_BLOB_PLOTTER True) or circular . . .

        # Interators for square grid placement
        y_count = 0
        y_turns = 0
        x_turns = 1

        # Interators for circular grid placement
        plot_phi = 0.0
        plot_theta = math.pi * 0.5
        pi_inc = 0.25
        plot_radius = blob_partition

        for i in range(NUM_BLOBS - 1):
            # Set up some random values for this blob
            color = round(random.random() * (len(COLORS) - 1))

            # Divide mass and radius ranges in half, put smaller masses with
            # smaller radiuses, and vice versa. Randomize whether we're doing
            # a bigger or smaller blob.
            if round(random.random() * 10) % 2:
                min_radius = MIN_RADIUS + (MAX_RADIUS - MIN_RADIUS) / 2
                min_mass = MIN_MASS + (MAX_MASS - MIN_MASS) / 2
                radius = round(
                    (random.random() * (MAX_RADIUS - min_radius)) + min_radius
                )
                mass = (random.random() * (MAX_MASS - min_mass)) + min_mass
            else:
                max_radius = MAX_RADIUS - (MAX_RADIUS - MIN_RADIUS) / 2
                max_mass = MAX_MASS - (MAX_MASS - MIN_MASS) / 2
                radius = round(
                    (random.random() * (max_radius - MIN_RADIUS)) + MIN_RADIUS
                )
                mass = (random.random() * (max_mass - MIN_MASS)) + MIN_MASS

            if self.square_grid:  # Square grid x,y plot for this blob
                # Get x and y coordinates for this blob
                # x and y take turns moving, each turn gives the other one more turn than
                # last time, which we need to do to spiral around in a square grid
                if y_turns == 0:
                    x_turns -= 1
                    if x_turns == 0:
                        y_turns = y_count + 1
                        y_count = 0

                    if y <= half_screen:
                        x += blob_partition
                    elif y > half_screen:
                        x -= blob_partition
                else:
                    y_count += 1
                    y_turns -= 1
                    if y_turns == 0:
                        x_turns = y_count + 1

                    if x >= half_screen:
                        y += blob_partition
                    elif x < half_screen:
                        y -= blob_partition
            else:  # Circular grid x,y plot for this blob
                # Get x and y for this blob, vars set up from last interation or initial setting
                x = half_screen + plot_radius * math.sin(plot_theta) * math.cos(
                    plot_phi
                )
                y = half_screen + plot_radius * math.sin(plot_theta) * math.sin(
                    plot_phi
                )
                z = half_screen + plot_radius * math.cos(plot_theta)

                # Set up vars for next interation, move the "clock dial" another notch,
                # or make it longer by blob_partition if we've gone around 360 degrees
                if round(plot_phi, 8) == round((math.pi * 2) - (math.pi * pi_inc), 8):
                    plot_phi = 0.0
                    plot_radius += blob_partition
                    pi_inc = pi_inc / 2
                else:
                    plot_phi += math.pi * pi_inc

            # Figure out velocity for this blob
            dx = half_screen - x
            dy = half_screen - y
            dz = half_screen - z
            d = math.sqrt(dx**2 + dy**2 + dz**2)

            velocity = 0
            if self.start_perfect_orbit:
                # get velocity for a perfect orbit around center blob
                velocity = math.sqrt(G * CENTER_BLOB_MASS / d)
            elif self.start_perfect_floor_bounce:
                # get velocity for a perfect floor bounce when that is on
                velocity = math.sqrt(G * FLOOR_MASS / d)
            else:
                # Just use a random velocity
                velocity = (
                    random.random() * (MAX_VELOCITY - MIN_VELOCITY) + MIN_VELOCITY
                )

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            theta = theta - (math.pi * 0.25)
            phi = phi - (math.pi * 0.5)

            velocityx = velocity * math.sin(theta) * math.cos(phi)
            velocityy = velocity * math.sin(theta) * math.sin(phi)
            velocityz = velocity * math.cos(theta)

            # Phew, let's instantiate this puppy . . .
            new_blob = MassiveBlob(
                str(i + 1),
                COLORS[color],
                radius,
                mass,
                z,
                y,
                x,
                velocityz,
                velocityy,
                velocityx,
            )
            self.blobs.append(new_blob)

            if self.z_axis.get(new_blob.z) is None:
                self.z_axis[new_blob.z] = []
            self.z_axis[new_blob.z].append(new_blob)

    def draw_blobs(self, screen, blob_font):
        keys = reversed(sorted(self.z_axis.keys()))

        for key in keys:
            # Draw the blobs
            for blob in self.z_axis[key]:
                # get rid of dead blobs
                if blob.dead:
                    if blob.swallowed:
                        self.blobs_swalled += 1
                    elif blob.escaped:
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
                # mass_text = blob_font.render(
                #     f"{blob.name}", 1, (255, 255, 255), (0, 0, 0)
                # )
                # screen.blit(
                #     mass_text,
                #     (
                #         (blob.x * SCALE) - (mass_text.get_width() / 2),
                #         (blob.y * SCALE) - (mass_text.get_height() / 2),
                #     ),
                # )

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
        self.z_axis = {}

        # Check blobs
        for blob in self.blobs:
            # Check for and react to any collisions with other blobs
            for blob2 in self.blobs:
                if (id(blob2) != id(blob)) and (checked.get(id(blob2)) == None):
                    blob.collision_detection(blob2)  # TODO wraping collision detection
                blob.gravitational_pull(blob2, G)

            checked[id(blob)] = 1

            # Change direction or wrap if hitting the edge of screen
            # blob.edge_detection(wrap)
            # Turn on floor gravity (experimental)
            # blob.floor_gravity(G)

            # Apply velocity
            blob.advance()

            if self.z_axis.get(blob.z) is None:
                self.z_axis[blob.z] = []
            self.z_axis[blob.z].append(blob)
