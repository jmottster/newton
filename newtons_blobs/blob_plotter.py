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
    universe_w : float
        The width of the drawing surface that will represent the universe

    universe_h : float
        The height of the drawing surface that will represent the universe

    display_w : float
        The width of the drawing surface that will represent the display screen

    display_h : float
        The height of the drawing surface that will represent the display screen


    Methods
    -------
    start_over(universe)
        Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs(universe)
    plot_blobs(universe)
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences.
        universe is the object reference needed to instantiate a MassiveBlob
    draw_blobs()
        Interates the blobs according z_axis keys, deletes the ones flaged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates
    update_blobs()
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis hash table
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range

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
        """Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs(universe)"""
        self.blobs = np.empty([NUM_BLOBS], dtype=object)
        self.blobs_swalled = 0
        self.blobs_escaped = 0
        self.z_axis = {}
        self.plot_blobs(universe)

    def plot_blobs(self, universe):
        """
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences.
        universe is the object reference needed to instantiate a MassiveBlob
        """
        # TODO This function is getting unruly, clean it up

        orbiting_blobs = NUM_BLOBS - 1

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
        y_count = 2
        y_turns = 0
        x_turns = 1
        x += blob_partition
        y -= blob_partition

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

        if ((math.pi * 2) / pi_inc) > (orbiting_blobs):
            plot_radius = self.scaled_display_height / 4

            pi_inc = (math.pi * 2) / (orbiting_blobs)

        # Now, for each blob . . .
        for i in range(1, NUM_BLOBS):
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

            if round(random.randint(1, 10)) % 2:
                radius = round(
                    (random.random() * (max_radius_delta - MIN_RADIUS)) + MIN_RADIUS
                )
                mass = random.random() * (max_mass_delta - MIN_MASS) + MIN_MASS
            else:
                radius = round(
                    (random.random() * (MAX_RADIUS - max_radius_delta))
                    + max_radius_delta
                )
                mass = (random.random() * (MAX_MASS - max_mass_delta)) + max_mass_delta

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

                blobs_left = orbiting_blobs - i
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
            else:
                # Generate a random velocity within provided boundaries
                velocity = (
                    random.random() * (MAX_VELOCITY - MIN_VELOCITY)
                ) + MIN_VELOCITY

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            # Add some chaos to starting trajectory
            theta = theta - (math.pi * 0.15)
            # turn 90 degrees from pointing center for begining velocity (orbit)
            phi = phi - (math.pi * 0.5)

            velocityx = velocity * math.sin(theta) * math.cos(phi)
            velocityy = velocity * math.sin(theta) * math.sin(phi)
            velocityz = velocity * math.cos(theta)

            # Phew, let's instantiate this puppy . . .
            new_blob = MassiveBlob(
                self.universe_size_h,
                str(i),
                BlobSurface(radius, COLORS[color], universe),
                mass,
                x,
                y,
                z,
                velocityx,
                velocityy,
                velocityz,
            )
            self.blobs[i] = new_blob

            if self.z_axis.get(new_blob.z) is None:
                self.z_axis[new_blob.z] = np.array([new_blob], dtype=object)
            else:
                self.z_axis[new_blob.z] = np.append(self.z_axis[new_blob.z], new_blob)

    def draw_blobs(self):
        """
        Interates the blobs according z_axis keys, deletes the ones flaged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates
        """
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
        """
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis hash table
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range
        """
        checked = {}
        self.z_axis = {}

        def check_blobs(blob1, blobs):
            if blobs is None:
                return
            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):
                    blob1.collision_detection(blob2)
                    if blob1.name != CENTER_BLOB_NAME:
                        blob1.gravitational_pull(blob2, G)

        def check_grid(blob):
            pg = self.proximity_grid
            gk = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2]])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2]])

            check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2]])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2]])
            check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2]])

            # ---------------------------------------------------#

            # check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2] + 1])
            # check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2] + 1])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2] + 1])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2] + 1])

            # check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2] + 1])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2] + 1])
            # check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2] + 1])

            # ---------------------------------------------------#

            # check_blobs(blob, pg[gk[0] + 1][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0] + 1][gk[1]][gk[2] - 1])
            # check_blobs(blob, pg[gk[0] + 1][gk[1] - 1][gk[2] - 1])

            check_blobs(blob, pg[gk[0]][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0]][gk[1]][gk[2] - 1])
            check_blobs(blob, pg[gk[0]][gk[1] - 1][gk[2] - 1])

            # check_blobs(blob, pg[gk[0] - 1][gk[1] + 1][gk[2] - 1])
            check_blobs(blob, pg[gk[0] - 1][gk[1]][gk[2] - 1])
            # check_blobs(blob, pg[gk[0] - 1][gk[1] - 1][gk[2] - 1])

        for i in range(1, len(self.blobs)):
            self.blobs[0].gravitational_pull(self.blobs[i], G)

        # dirty hack to minimize bouncing off center blob (i.e., since this will run again in loop, that double
        #   check of collision makes getting sucked into center blob more likely)
        check_grid(self.blobs[0])

        for i in range(0, len(self.blobs)):
            blob = self.blobs[i]
            check_grid(blob)

            blob.advance()

            if self.z_axis.get(blob.z) is None:
                self.z_axis[blob.z] = np.array([blob], dtype=object)
            else:
                self.z_axis[blob.z] = np.append(self.z_axis[blob.z], blob)

            checked[id(blob)] = 1
