"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial positions and velocities of blobs and maintaining them

by Jason Mott, copyright 2024
"""

from typing import Dict
import pygame
import numpy as np
import math, random
from .globals import *
from .massive_blob import MassiveBlob
from .blob_surface import BlobSurface
from .blob_physics import BlobPhysics as bp

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
    get_prefs(data: dict) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    set_prefs(data, data: dict, universe: pygame.Surface) -> None
        Sets this instances variables according to the key/value pairs in the provided dict, restoring the state
        saved in it and writing to the universe instance for display

    start_over(universe: pygame.Surface) -> None
        Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs(universe)

    plot_blobs(universe: pygame.Surface) -> None
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences.
        universe is the object reference needed to instantiate a MassiveBlob

    draw_blobs() -> None
        Iterates the blobs according z_axis keys, deletes the ones flagged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates

    update_blobs() -> None
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range

    plot_center_blob(universe: pygame.Surface) -> None
        Creates and places the center blob and adds it to self.blobs[0]

    plot_square_grid() -> None
        Iterates through blobs and plots them in a square grid configuration around the center blob

    plot_circular_grid() -> None
        Iterates through blobs and plots them in a circular grid configuration around the center blob

    add_z_axis(blob: MassiveBlob) -> None
        Adds the given blob to the z_axis dict according to it z position

    add_pos_vel(blob: MassiveBlob, x: float, y: float, z: float) -> None
        Adds z,y,z to given blob, and configures velocity for orbit around center blob

    """

    def __init__(
        self, universe_w: float, universe_h: float, display_w: float, display_h: float
    ):

        self.universe_size_w: float = universe_w
        self.universe_size_h: float = universe_h
        self.scaled_universe_width: float = universe_w * SCALE_UP
        self.scaled_universe_height: float = universe_h * SCALE_UP
        self.scaled_display_width: float = display_w * SCALE_UP
        self.scaled_display_height: float = display_h * SCALE_UP

        MassiveBlob.center_blob_x = universe_w / 2
        MassiveBlob.center_blob_y = universe_h / 2
        MassiveBlob.center_blob_z = universe_h / 2
        bp.set_gravitational_range(self.scaled_universe_height)

        # Preferences/states
        self.blobs: np.ndarray[MassiveBlob] = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.blobs_swallowed: int = 0
        self.blobs_escaped: int = 0
        self.z_axis: Dict[float, np.ndarray[MassiveBlob]] = {}
        self.proximity_grid: np.ndarray[MassiveBlob] = np.empty(
            [
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
            ],
            dtype=MassiveBlob,
        )
        self.square_grid: bool = SQUARE_BLOB_PLOTTER
        self.start_perfect_orbit: bool = START_PERFECT_ORBIT

    def get_prefs(self, data: dict) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["universe_size_w"] = self.universe_size_w
        data["universe_size_h"] = self.universe_size_h
        data["scaled_universe_width"] = self.scaled_universe_width
        data["scaled_universe_height"] = self.scaled_universe_height
        data["blobs_swallowed"] = self.blobs_swallowed
        data["blobs_escaped"] = self.blobs_escaped
        data["square_grid"] = self.square_grid
        data["start_perfect_orbit"] = self.start_perfect_orbit
        data["blobs"] = []

        for blob in self.blobs:
            blob_data = {}
            blob.get_prefs(blob_data)
            data["blobs"].append(blob_data)

    def set_prefs(self, data: dict, universe: pygame.Surface) -> None:
        """
        Sets this instances variables according to the key/value pairs in the provided dict, restoring the state
        saved in it and writing to the universe instance for display
        """
        self.universe_size_w = data["universe_size_w"]
        self.universe_size_h = data["universe_size_h"]
        self.scaled_universe_width = data["scaled_universe_width"]
        self.scaled_universe_height = data["scaled_universe_height"]
        self.blobs_swallowed = data["blobs_swallowed"]
        self.blobs_escaped = data["blobs_escaped"]
        self.square_grid = data["square_grid"]
        self.start_perfect_orbit = data["start_perfect_orbit"]
        self.blobs = np.empty([len(data["blobs"])], dtype=MassiveBlob)
        self.z_axis.clear()
        i = 0
        for blob_pref in data["blobs"]:
            self.blobs[i] = MassiveBlob(
                self.universe_size_h,
                blob_pref["name"],
                BlobSurface(blob_pref["radius"], blob_pref["color"], universe),
                blob_pref["mass"],
                blob_pref["x"],
                blob_pref["y"],
                blob_pref["z"],
                blob_pref["vx"],
                blob_pref["vy"],
                blob_pref["vz"],
            )

            self.add_z_axis(self.blobs[i])
            i += 1

    def start_over(self, universe: pygame.Surface) -> None:
        """Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs(universe)"""
        self.blobs = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.blobs_swallowed = 0
        self.blobs_escaped = 0
        self.z_axis.clear()
        self.plot_blobs(universe)

    def plot_blobs(self, universe: pygame.Surface) -> None:
        """
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences.
        universe is the object reference needed to instantiate a MassiveBlob
        """

        self.plot_center_blob(universe)

        # Create orbiting blobs without position or velocity
        for i in range(1, NUM_BLOBS):
            # Set up some random values for this blob
            color = round(random.random() * (len(COLORS) - 1))
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

            # Phew, let's instantiate this puppy . . .
            self.blobs[i] = MassiveBlob(
                self.universe_size_h,
                str(i),
                BlobSurface(radius, COLORS[color], universe),
                mass,
                0,
                0,
                0,
                0,
                0,
                0,
            )

        if self.square_grid:
            self.plot_square_grid()
        else:
            self.plot_circular_grid()

    def draw_blobs(self) -> None:
        """
        Iterates the blobs according z_axis keys, deletes the ones flagged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates
        """
        self.proximity_grid = np.empty(
            [
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
                int(GRID_KEY_UPPER_BOUND),
            ],
            dtype=MassiveBlob,
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
                        self.blobs_swallowed += 1
                    elif blob.escaped:
                        self.blobs_escaped += 1
                    self.blobs = np.delete(self.blobs, np.where(self.blobs == blob)[0])
                    continue
                blob.draw()

                grid_key = blob.grid_key()

                if self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] is None:
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = (
                        np.array([blob], dtype=MassiveBlob)
                    )
                else:
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = (
                        np.append(
                            self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]],
                            blob,
                        )
                    )

    def update_blobs(self) -> None:
        """
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range
        """
        checked = {}
        self.z_axis.clear()

        def check_blobs(blob1: MassiveBlob, blobs: np.ndarray[MassiveBlob]) -> None:
            if blobs is None:
                return
            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):
                    bp.collision_detection(blob1, blob2)
                    if blob1.name != CENTER_BLOB_NAME:
                        bp.gravitational_pull(blob1, blob2)

        def check_grid(blob: MassiveBlob) -> None:
            pg = self.proximity_grid
            gk = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            for z_offset in range(-1, 2):
                for x_offset in range(-1, 2):
                    for y_offset in range(-1, 2):
                        # Skip the corners of the cube, worth risking the occasional miss for the performance boost
                        if x_offset != 0 and y_offset != 0 and z_offset != 0:
                            continue
                        check_blobs(
                            blob,
                            pg[gk[0] + x_offset][gk[1] + y_offset][gk[2] + z_offset],
                        )

        for i in range(1, len(self.blobs)):
            bp.gravitational_pull(self.blobs[0], self.blobs[i])

        # dirty hack to minimize bouncing off center blob (i.e., since this will run again in loop, that double
        #   check of collision with center blob makes getting sucked into center blob more likely)
        check_grid(self.blobs[0])

        for i in range(0, len(self.blobs)):

            check_grid(self.blobs[i])

            self.blobs[i].advance()

            self.add_z_axis(self.blobs[i])

            checked[id(self.blobs[i])] = 1

    def plot_center_blob(self, universe: pygame.Surface) -> None:
        """Creates and places the center blob and adds it to self.blobs[0]"""
        scaled_half_universe_h = self.scaled_universe_height / 2
        scaled_half_universe_w = self.scaled_universe_width / 2

        # Set up the center blob, which will be the massive star all other blobs orbit
        x = scaled_half_universe_w
        y = scaled_half_universe_h
        z = scaled_half_universe_h

        self.blobs[0] = MassiveBlob(
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

        self.add_z_axis(self.blobs[0])

    def plot_square_grid(self) -> None:
        """Iterates through blobs and plots them in a square grid configuration around the center blob"""
        x = self.blobs[0].x
        y = self.blobs[0].y
        z = self.blobs[0].z
        scaled_half_universe_w = self.blobs[0].x
        scaled_half_universe_h = self.blobs[0].y

        # split the screen up into enough partitions for every blob
        if NUM_BLOBS > 5:
            blob_partition = round(
                ((self.scaled_display_height) / math.sqrt(NUM_BLOBS))
            )
        else:
            blob_partition = self.scaled_display_height / 4

        # Iterators grid placement
        y_count = 2
        y_turns = 0
        x_turns = 1
        x += blob_partition
        y -= blob_partition

        for i in range(1, NUM_BLOBS):
            # Get x and y coordinates for this blob
            # x and y take turns moving, each turn gives the other one more turn than
            # last time, which we need to do to spiral around in a square grid
            if y_turns == 0:
                x_turns -= 1
                if x_turns == 0:
                    y_turns = y_count + 1
                    y_count = 0

                if y <= scaled_half_universe_h:
                    x += blob_partition
                elif y > scaled_half_universe_h:
                    x -= blob_partition
            else:
                y_count += 1
                y_turns -= 1
                if y_turns == 0:
                    x_turns = y_count + 1

                if x >= scaled_half_universe_w:
                    y += blob_partition
                elif x < scaled_half_universe_w:
                    y -= blob_partition

            self.add_pos_vel(self.blobs[i], x, y, z)

    def plot_circular_grid(self) -> None:
        """Iterates through blobs and plots them in a circular grid configuration around the center blob"""

        scaled_half_universe_w = self.blobs[0].x
        scaled_half_universe_h = self.blobs[0].y

        orbiting_blobs = NUM_BLOBS - 1
        # Iterators for circular grid placement, blobs will be placed in ever
        # increasing sized circles around the center blob
        plot_phi = 0.0
        plot_theta = math.pi * 0.5
        # How much the radius will increase each time we move to the next biggest
        # circle around the center blob (the size will be some multiple of the diameter of the biggest
        # blob)
        plot_radius_partition = ((MAX_RADIUS * 4)) * SCALE_UP
        # How far apart each blob will be on each circumference
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

        for i in range(1, NUM_BLOBS):

            # Circular grid x,y plot for this blob
            # Get x and y for this blob, vars set up from last iteration or initial setting
            x = scaled_half_universe_w + plot_radius * math.sin(plot_theta) * math.cos(
                plot_phi
            )
            y = scaled_half_universe_h + plot_radius * math.sin(plot_theta) * math.sin(
                plot_phi
            )
            z = scaled_half_universe_h + plot_radius * math.cos(plot_theta)

            blobs_left = orbiting_blobs - i
            # Set up vars for next iteration, move the "clock dial" another notch,
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

            self.add_pos_vel(self.blobs[i], x, y, z)

    def add_z_axis(self, blob: MassiveBlob) -> None:
        """Adds the given blob to the z_axis dict according to it z position"""
        if self.z_axis.get(blob.z) is None:
            self.z_axis[blob.z] = np.array([blob], dtype=MassiveBlob)
        else:
            self.z_axis[blob.z] = np.append(self.z_axis[blob.z], blob)

    def add_pos_vel(self, blob: MassiveBlob, x: float, y: float, z: float) -> None:
        """Adds z,y,z to given blob, and configures velocity for orbit around center blob"""
        velocity = 0
        # Figure out velocity for this blob
        dx = self.blobs[0].x - x
        dy = self.blobs[0].y - y
        dz = self.blobs[0].z - z
        d = math.sqrt(dx**2 + dy**2 + dz**2)

        if self.start_perfect_orbit:
            # get velocity for a perfect orbit around center blob
            velocity = math.sqrt(G * CENTER_BLOB_MASS / d)
        else:
            # Generate a random velocity within provided boundaries
            velocity = (random.random() * (MAX_VELOCITY - MIN_VELOCITY)) + MIN_VELOCITY

        theta = math.acos(dz / d)
        phi = math.atan2(dy, dx)

        # Add some chaos to starting trajectory
        theta = theta - (math.pi * 0.15)
        # turn 90 degrees from pointing center for beginning velocity (orbit)
        phi = phi - (math.pi * 0.5)

        velocityx = velocity * math.sin(theta) * math.cos(phi)
        velocityy = velocity * math.sin(theta) * math.sin(phi)
        velocityz = velocity * math.cos(theta)

        # Phew, let's instantiate this puppy . . .
        blob.update_pos_vel(
            x,
            z,
            y,
            velocityx,
            velocityz,
            velocityy,
        )

        self.add_z_axis(blob)
