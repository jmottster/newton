"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial posisions and velocities of blobs and maintaining them

by Jason Mott, copyright 2024
"""

import numpy as np
import math, random
from .globals import *
from .massive_blob import MassiveBlob, BlobSurface

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPlotter:
    """
    A class used for setting up initial positions and velocities of blobs and maintaining them

    Attributes
    ----------
    screen : pygame.Surface
        the main surface everything will be drawn on
    display : pygame.Surface
        the display representing the monitor


    Methods
    -------
    setup_blobs()
        populates blob array according to global var values
    draw_blobs(blob_font)
        draws the blobs on the screen (a PyGame screen), also draws a name label if that's turned on
    draw_stats(stat_font)
        draws blob stats on the screen corners (mass of sun, number of blobs left, how many swallowed, how many escaped)
    update_blobs()
        applies collision detection, gravitational pull, and if activated, edge detection

    """

    def __init__(self, universe_w, universe_h, display_w, display_h):
        self.blobs = np.empty([NUM_BLOBS], dtype=object)
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.z_axis = {}
        self.proximity_grid = np.empty(
            [
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
            ],
            dtype=object,
        )
        self.square_grid = SQUARE_BLOB_PLOTTER
        self.start_perfect_orbit = START_PERFECT_ORBIT
        self.start_perfect_floor_bounce = START_PERFECT_FLOOR_BOUNCE
        self.universe_size_w = universe_w
        self.universe_size_h = universe_h
        self.scaled_universe_width = universe_w * SCALE_UP
        self.scaled_universe_height = universe_h * SCALE_UP
        self.scaled_display_width = display_w * SCALE_UP
        self.scaled_display_height = display_h * SCALE_UP
        MassiveBlob.center_blob_x = universe_w / 2
        MassiveBlob.center_blob_y = universe_h / 2
        MassiveBlob.center_blob_z = universe_h / 2

    def start_over(self, universe):
        self.blobs = np.empty([NUM_BLOBS], dtype=object)
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.z_axis = {}
        self.plot_blobs(universe)

    def plot_blobs(self, universe):
        # TODO This function is getting unruly, clean it up

        # split the screen up into enough partitions for every blob
        if NUM_BLOBS > 5:
            blob_partition = round(
                ((self.scaled_display_height) / math.sqrt(NUM_BLOBS))
            )
        else:
            blob_partition = self.scaled_display_height / 4

        half_universe_h = self.scaled_universe_height / 2
        half_universe_w = self.scaled_universe_width / 2

        # Set up the center blob, which will be the massive star all other blobs orbit
        x = half_universe_w
        y = half_universe_h
        z = half_universe_h

        sun_blob = MassiveBlob(
            self.universe_size_h,
            CENTER_BLOB_NAME,
            BlobSurface(CENTER_BLOB_RADIUS, CENTER_BLOB_COLOR, universe),
            CENTER_BLOB_MASS,
            x,
            y,
            z,
            0,
            0,
            0,
        )
        self.blobs[0] = sun_blob

        if self.z_axis.get(sun_blob.z) is None:
            self.z_axis[sun_blob.z] = np.array([sun_blob], dtype=object)
        else:
            self.z_axis[sun_blob.z] = np.append(self.z_axis[sun_blob.z], sun_blob)

        # Blob placement grid, either square (if SQUARE_BLOB_PLOTTER True) or circular . . .

        # Interators for square grid placement
        y_count = 0
        y_turns = 0
        x_turns = 1

        # Interators for circular grid placement, blobs will be placed in ever
        # increasing sized circles around the center blob
        plot_phi = 0.0
        plot_theta = math.pi * 0.5
        # How much the radius will increase each time we move to the next biggest
        # circle around the center blob (the size will be some multiple of the diameter of the biggest
        # blob)
        plot_radius_partition = ((MAX_RADIUS * 4)) * SCALE_UP
        # How far apart each blob will be on each circumferance
        chord_scaled = (MAX_RADIUS * 3) * SCALE_UP
        # The start radius (smallest circle around center blob)
        plot_radius = ((MAX_RADIUS * 3) + (CENTER_BLOB_RADIUS * 2)) * SCALE_UP
        # How many radians to increase for each blob around the circumference (such that
        # we get chord_scaled length between each blob center)
        pi_inc = math.asin(chord_scaled / (plot_radius * 2)) * 2
        # Divy up the remainder for a more even distribution
        pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

        if ((math.pi * 2) / pi_inc) > (NUM_BLOBS - 1):
            plot_radius = self.scaled_display_height / 4

            pi_inc = (math.pi * 2) / (NUM_BLOBS - 1)
            pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

        # Now, for each blob . . .
        for i in range(NUM_BLOBS - 1):
            # Set up some random values for this blob
            color = round(random.random() * (len(COLORS) - 1))
            velocity = 0
            radius = 0
            mass = 0
            # Divide mass and radius ranges in half, put smaller masses with
            # smaller radiuses, and vice versa. Randomize whether we're doing
            # a bigger or smaller blob.
            max_radius_delta = MIN_RADIUS + ((MAX_RADIUS - MIN_RADIUS) / 2)
            max_mass_delta = MIN_MASS + ((MAX_MASS - MIN_MASS) / 2)
            max_velocity_delta = MIN_VELOCITY + ((MAX_VELOCITY - MIN_VELOCITY) / 2)
            if round(random.randint(1, 10)) % 2:
                radius = round(
                    (random.random() * (max_radius_delta - MIN_RADIUS)) + MIN_RADIUS
                )
                mass = random.random() * (max_mass_delta - MIN_MASS) + MIN_MASS
                velocity = (
                    random.random() * (max_velocity_delta - MIN_VELOCITY) + MIN_VELOCITY
                )

            else:
                radius = round(
                    (random.random() * (MAX_RADIUS - max_radius_delta))
                    + max_radius_delta
                )
                mass = (random.random() * (MAX_MASS - max_mass_delta)) + max_mass_delta
                velocity = (
                    random.random() * (MAX_VELOCITY - max_velocity_delta)
                    + max_velocity_delta
                )

            if self.square_grid:  # Square grid x,y plot for this blob
                # Get x and y coordinates for this blob
                # x and y take turns moving, each turn gives the other one more turn than
                # last time, which we need to do to spiral around in a square grid
                if y_turns == 0:
                    x_turns -= 1
                    if x_turns == 0:
                        y_turns = y_count + 1
                        y_count = 0

                    if y <= half_universe_h:
                        x += blob_partition
                    elif y > half_universe_h:
                        x -= blob_partition
                else:
                    y_count += 1
                    y_turns -= 1
                    if y_turns == 0:
                        x_turns = y_count + 1

                    if x >= half_universe_w:
                        y += blob_partition
                    elif x < half_universe_w:
                        y -= blob_partition
            else:  # Circular grid x,y plot for this blob
                # Get x and y for this blob, vars set up from last interation or initial setting
                x = half_universe_w + plot_radius * math.sin(plot_theta) * math.cos(
                    plot_phi
                )
                y = half_universe_h + plot_radius * math.sin(plot_theta) * math.sin(
                    plot_phi
                )
                z = half_universe_h + plot_radius * math.cos(plot_theta)

                blobs_left = NUM_BLOBS - (i + 2)
                # Set up vars for next interation, move the "clock dial" another notch,
                # or make it longer by plot_radius_partition if we've gone around 360 degrees
                if round(plot_phi + pi_inc, 8) > round((math.pi * 2) - (pi_inc), 8):
                    plot_phi = 0.0
                    # Increase the radius for the next go around the center blob
                    plot_radius += plot_radius_partition
                    # How many radians to increase for each blob around the circumference (such that
                    # we get chord_scaled length between each blob center)
                    pi_inc = math.asin(chord_scaled / (plot_radius * 2)) * 2
                    # Divy up the remainder for a more even distribution
                    pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

                    if blobs_left > 0 and ((math.pi * 2) / pi_inc) > blobs_left:
                        pi_inc = (math.pi * 2) / blobs_left
                        pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

                else:
                    plot_phi += pi_inc

            # Figure out velocity for this blob
            dx = half_universe_w - x
            dy = half_universe_h - y
            dz = half_universe_h - z
            d = math.sqrt(dx**2 + dy**2 + dz**2)

            if self.start_perfect_orbit:
                # get velocity for a perfect orbit around center blob
                velocity = math.sqrt(G * CENTER_BLOB_MASS / d)
            elif self.start_perfect_floor_bounce:
                # get velocity for a perfect floor bounce when that is on
                velocity = math.sqrt(G * FLOOR_MASS / d)

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            # Add some chaos to starting trajectory
            theta = theta - (math.pi * 0.25)
            # turn 90 degrees from pointing center for begining velocity (orbit)
            phi = phi - (math.pi * 0.5)

            velocityx = velocity * math.sin(theta) * math.cos(phi)
            velocityy = velocity * math.sin(theta) * math.sin(phi)
            velocityz = velocity * math.cos(theta)

            # Phew, let's instantiate this puppy . . .
            new_blob = MassiveBlob(
                self.universe_size_h,
                str(i + 1),
                BlobSurface(radius, COLORS[color], universe),
                mass,
                x,
                z,
                y,
                velocityx,
                velocityz,
                velocityy,
            )
            self.blobs[i + 1] = new_blob

            if self.z_axis.get(new_blob.z) is None:
                self.z_axis[new_blob.z] = np.array([new_blob], dtype=object)
            else:
                self.z_axis[new_blob.z] = np.append(self.z_axis[new_blob.z], new_blob)

    def draw_blobs(self):
        self.proximity_grid = np.empty(
            [
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
            ],
            dtype=object,
        )

        keys = np.flip(
            np.sort(np.array([k for k in self.z_axis], dtype=float), axis=None)
        )

        for key in keys:
            # Draw the blobs
            for blob in self.z_axis[key]:
                # get rid of dead blobs
                if blob.dead:
                    if blob.swallowed:
                        self.blobs_swalled += 1
                    elif blob.escaped:
                        self.blobs_escaped += 1
                    self.blobs = np.delete(self.blobs, np.where(self.blobs == blob)[0])
                    continue
                blob.draw()

                grid_key = blob.grid_key()

                if self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] is None:
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = (
                        np.array([blob], dtype=object)
                    )
                else:
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = (
                        np.append(
                            self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]],
                            blob,
                        )
                    )

    def update_blobs(self):
        # set up hash to prevent double checking blob pairs for collision, so no
        # unique pair of blobs are ever checked twice.
        checked = {}
        self.z_axis = {}

        def check_blobs(blob1, blobs):
            # Check for and react to any collisions with other blobs
            if blobs is None:
                return
            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):
                    blob1.collision_detection(blob2)  # TODO wraping collision detection
                    if blob1.name != CENTER_BLOB_NAME:
                        blob1.gravitational_pull(blob2, G)

                    # These are not used, and probably out of date.
                    # Might just scrap them altogether.
                    # blob1.edge_detection(wrap)
                    # Turn on floor gravity (experimental)
                    # blob1.floor_gravity(G)

        # Do the center blob by itself because we want all blobs to be under its gravitational pull
        for i in range(1, len(self.blobs)):
            self.blobs[0].gravitational_pull(self.blobs[i], G)
        check_blobs(self.blobs[0], self.blobs)
        # checked[id(self.blobs[0])] = 1
        self.z_axis[self.blobs[0].z] = np.array([self.blobs[0]], dtype=object)

        # Check blobs
        for i in range(0, len(self.blobs)):
            blob = self.blobs[i]
            pg = self.proximity_grid
            gk = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them. The center
            # blob is the only exception, which is done before this loop.

            # Check my cell, and all the cells on the y axis around me

            check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2]])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2]])

            check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2]])

            # move up one from me on z axis, and do it again, the
            # commented out lines are the corners of this "rubik's cube",
            # to improve performance, we'll take our chances on skiping them.

            # check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2] + 1])
            # check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2] + 1])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2] + 1])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2] + 1])

            # check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2] + 1])
            # check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2] + 1])

            # Move down one from me on z axis, and do it again

            # check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2] - 1])
            # check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2] - 1])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2] - 1])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2] - 1])

            # check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2] - 1])
            # check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2] - 1])

            # Apply velocity
            blob.advance()

            if self.z_axis.get(blob.z) is None:
                self.z_axis[blob.z] = np.array([blob], dtype=object)
            else:
                self.z_axis[blob.z] = np.append(self.z_axis[blob.z], blob)

            checked[id(blob)] = 1
