"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial positions and velocities of blobs and maintaining them

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, Tuple, Self
import numpy as np
import numpy.typing as npt
import math, random

from .globals import *
from newtons_blobs import BlobGlobalVars as bg_vars
from .blob_plugin_factory import BlobPluginFactory
from .massive_blob import MassiveBlob
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

    blob_factory: BlobPluginFactory
        An instance of BlobFactory loaded up with the required drawing libraries

    Methods
    -------
    get_prefs(data: dict) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    set_prefs(data, data: dict) -> None
        Sets this instance's variables according to the key/value pairs in the provided dict, restoring the state
        saved in it

    start_over() -> None
        Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs()

    plot_blobs() -> None
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences

    draw_blobs() -> None
        Iterates the blobs according z_axis keys, deletes the ones flagged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates

    update_blobs() -> None
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range

    plot_center_blob(universe: BlobUniverse) -> None
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
        self: Self,
        universe_w: float,
        universe_h: float,
        display_w: float,
        display_h: float,
        blob_factory: BlobPluginFactory,
    ):

        self.universe_size_w: float = universe_w
        self.universe_size_h: float = universe_h
        self.scaled_display_width: float = display_w * bg_vars.scale_up
        self.scaled_display_height: float = display_h * bg_vars.scale_up
        self.blob_factory: BlobPluginFactory = blob_factory
        self.display = self.blob_factory.get_blob_display()

        MassiveBlob.center_blob_x = universe_w / 2
        MassiveBlob.center_blob_y = universe_h / 2
        MassiveBlob.center_blob_z = universe_h / 2
        bp.set_gravitational_range(universe_h * bg_vars.scale_up)

        # Preferences/states
        self.blobs: npt.NDArray = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.blobs_swallowed: int = 0
        self.blobs_escaped: int = 0
        self.z_axis: Dict[float, npt.NDArray] = {}
        self.proximity_grid: npt.NDArray = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
            ],
            dtype=MassiveBlob,
        )
        self.square_grid: bool = bg_vars.square_blob_plotter
        self.start_perfect_orbit: bool = bg_vars.start_perfect_orbit
        self.start_angular_chaos: bool = bg_vars.start_angular_chaos

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["universe_size_w"] = self.universe_size_w / bg_vars.au_scale_factor
        data["universe_size_h"] = self.universe_size_h / bg_vars.au_scale_factor
        data["blobs_swallowed"] = self.blobs_swallowed
        data["blobs_escaped"] = self.blobs_escaped
        data["square_grid"] = self.square_grid
        data["start_perfect_orbit"] = self.start_perfect_orbit
        data["start_angular_chaos"] = self.start_angular_chaos
        data["blobs"] = []

        for blob in self.blobs:
            blob_data: Dict[str, Any] = {}
            blob.get_prefs(blob_data)
            data["blobs"].append(blob_data)

    def set_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        Sets this instances variables according to the key/value pairs in the provided dict, restoring the state
        saved in it
        """

        self.blob_factory.reset(len(data["blobs"]))
        self.display.update()
        self.universe_size_w = data["universe_size_w"] * bg_vars.au_scale_factor
        self.universe_size_h = data["universe_size_h"] * bg_vars.au_scale_factor
        self.blobs_swallowed = data["blobs_swallowed"]
        self.blobs_escaped = data["blobs_escaped"]
        self.square_grid = data["square_grid"]
        self.start_perfect_orbit = data["start_perfect_orbit"]
        self.start_angular_chaos = data["start_angular_chaos"]
        self.blobs = np.empty([len(data["blobs"])], dtype=MassiveBlob)
        self.z_axis.clear()
        bp.set_gravitational_range(self.universe_size_h * bg_vars.scale_up)

        i = 0
        for blob_pref in data["blobs"]:
            self.blobs[i] = MassiveBlob(
                self.universe_size_h,
                blob_pref["name"],
                self.blob_factory.new_blob_surface(
                    blob_pref["name"],
                    blob_pref["radius"] * bg_vars.au_scale_factor,
                    blob_pref["mass"],
                    tuple(blob_pref["color"]),  # type: ignore
                    blob_pref.get("texture"),  # Might not exist
                    blob_pref.get("rotation_speed"),  # Might not exist
                    blob_pref.get("rotation_pos"),  # Might not exist
                ),
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

    def start_over(self: Self) -> None:
        """Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs()"""

        self.blob_factory.reset()
        self.display.update()
        for blob in self.blobs:
            blob.destroy()
            self.display.update()

        universe = self.blob_factory.get_blob_universe()
        universe.clear()
        self.display.update()

        self.display.update()
        self.blobs = np.empty([NUM_BLOBS], dtype=MassiveBlob)

        self.universe_size_w = universe.get_width()
        self.universe_size_h = universe.get_height()

        self.display.update()
        self.blobs_swallowed = 0
        self.blobs_escaped = 0
        self.z_axis.clear()
        self.plot_blobs()

    def plot_blobs(self: Self) -> None:
        """
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences
        """
        self.plot_center_blob()

        planets: list[MassiveBlob] = []
        moons: list[MassiveBlob] = []

        max_radius_delta: float = (bg_vars.min_radius + bg_vars.max_radius) / 2

        min_radius_delta: float = (bg_vars.min_radius + max_radius_delta) / 2

        max_radius_delta = (max_radius_delta + bg_vars.max_radius) / 2

        max_mass_delta: float = (bg_vars.min_mass + bg_vars.max_mass) / 2

        min_mass_delta: float = (bg_vars.min_mass + max_mass_delta) / 2

        max_mass_delta = (max_mass_delta + bg_vars.max_mass) / 2

        moon: bool = False

        # Create orbiting blobs without position or velocity
        for i in range(1, NUM_BLOBS):
            # Set up some random values for this blob
            color: int = round(random.random() * (len(COLORS) - 1))
            radius: float = 0.0
            mass: float = 0.0

            if i > ((NUM_BLOBS - 1) * bg_vars.blob_moon_percent):

                moon = False
                if random.randint(1, 10) > 6:
                    radius = round(
                        (random.random() * (min_radius_delta - bg_vars.min_radius))
                        + bg_vars.min_radius,
                        2,
                    )

                    mass = (
                        random.random() * (min_mass_delta - bg_vars.min_mass)
                        + bg_vars.min_mass
                    )
                else:
                    radius = round(
                        (random.random() * (bg_vars.max_radius - max_radius_delta))
                        + max_radius_delta,
                        2,
                    )

                    mass = (
                        random.random() * (bg_vars.max_mass - max_mass_delta)
                    ) + max_mass_delta
            else:
                moon = True
                radius = round(
                    (
                        random.random()
                        * (bg_vars.max_moon_radius - bg_vars.min_moon_radius)
                    )
                    + bg_vars.min_moon_radius,
                    2,
                )
                mass = (
                    random.random() * (bg_vars.max_moon_mass - bg_vars.min_moon_mass)
                ) + bg_vars.min_moon_mass

            # Phew, let's instantiate this puppy . . .
            self.blobs[i] = MassiveBlob(
                self.universe_size_h,
                str(i),
                self.blob_factory.new_blob_surface(str(i), radius, mass, COLORS[color]),
                mass,
                0,
                0,
                0,
                0,
                0,
                0,
            )

            # planets.append(self.blobs[i])

            if moon:
                moons.append(self.blobs[i])
            else:
                planets.append(self.blobs[i])

        if self.square_grid:
            self.plot_square_grid(planets)
        else:
            self.plot_circular_grid(planets)

        if len(moons) > 0:
            self.plot_moons(moons, planets)

        # print(f"moons num: {len(moons)}")
        # print(f"planets num: {len(planets)}")

    def plot_moons(
        self: Self, moons: list[MassiveBlob], planets: list[MassiveBlob]
    ) -> None:

        for i in range(0, len(moons)):
            planets[random.randint(1, len(planets)) - 1].add_orbital(moons[i])
            self.add_pos_vel(moons[i], moons[i].x, moons[i].y, moons[i].z)

    def draw_blobs(self: Self) -> None:
        """
        Iterates the blobs according z_axis keys, deletes the ones flagged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates
        """
        self.proximity_grid = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
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
                    blob.destroy()
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

    def update_blobs(self: Self, dt: float = 1) -> None:
        """
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range
        """
        checked: Dict[int, int] = {}
        self.z_axis.clear()
        pg = self.proximity_grid

        def check_blobs(
            blob1: MassiveBlob,
            blobs: npt.NDArray,
            pos_offsets: Tuple[float, float, float],
        ) -> None:
            if blobs is None:
                return

            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):

                    blob2.x += pos_offsets[0]
                    blob2.y += pos_offsets[1]
                    blob2.z += pos_offsets[2]

                    bp.gravitational_pull(blob1, blob2, dt)
                    bp.collision_detection(blob1, blob2)

                    blob2.x -= pos_offsets[0]
                    blob2.y -= pos_offsets[1]
                    blob2.z -= pos_offsets[2]

            if not bg_vars.center_blob_escape:
                bp.edge_detection(blob1)

        def check_grid(blob: MassiveBlob) -> None:

            gk: Tuple[int, int, int] = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            z_pos_offset: float = 0
            x_pos_offset: float = 0
            y_pos_offset: float = 0
            scaled_universe: float = bg_vars.universe_size * bg_vars.scale_up
            for z_i_offset in range(-1, 2):
                z = gk[2] + z_i_offset
                if z > bg_vars.grid_key_check_bound:
                    z = 0
                    z_pos_offset = scaled_universe
                elif z < 0:
                    z_pos_offset = -scaled_universe
                else:
                    z_pos_offset = 0
                for x_i_offset in range(-1, 2):
                    x = gk[0] + x_i_offset
                    if x > bg_vars.grid_key_check_bound:
                        x = 0
                        x_pos_offset = scaled_universe
                    elif x < 0:
                        x_pos_offset = -scaled_universe
                    else:
                        x_pos_offset = 0
                    for y_i_offset in range(-1, 2):
                        y = gk[1] + y_i_offset
                        if y > bg_vars.grid_key_check_bound:
                            y = 0
                            y_pos_offset = scaled_universe
                        elif y < 0:
                            y_pos_offset = -scaled_universe
                        else:
                            y_pos_offset = 0
                        # Skip the corners of the cube, worth risking the occasional miss for the performance boost
                        if x_i_offset != 0 and y_i_offset != 0 and z_i_offset != 0:
                            continue
                        check_blobs(
                            blob,
                            pg[x][y][z],
                            (x_pos_offset, y_pos_offset, z_pos_offset),
                        )

        for i in range(1, len(self.blobs)):
            bp.gravitational_pull(self.blobs[0], self.blobs[i], dt)
            bp.collision_detection(self.blobs[0], self.blobs[i])

        if not bg_vars.center_blob_escape:
            bp.edge_detection(self.blobs[0])

        self.blobs[0].advance(dt)
        self.add_z_axis(self.blobs[0])
        checked[id(self.blobs[0])] = 1

        for i in range(1, len(self.blobs)):

            check_grid(self.blobs[i])

            self.blobs[i].advance(dt)

            self.add_z_axis(self.blobs[i])

            checked[id(self.blobs[i])] = 1

    def plot_center_blob(self: Self) -> None:
        """Creates and places the center blob and adds it to self.blobs[0]"""

        # Set up the center blob, which will be the massive star all other blobs orbit
        x, y, z = self.blob_factory.get_blob_universe().get_center_blob_start_pos()

        self.blobs[0] = MassiveBlob(
            self.universe_size_h,
            CENTER_BLOB_NAME,
            self.blob_factory.new_blob_surface(
                CENTER_BLOB_NAME,
                bg_vars.center_blob_radius,
                bg_vars.center_blob_mass,
                CENTER_BLOB_COLOR,
            ),
            bg_vars.center_blob_mass,
            x,
            y,
            z,
            0,
            0,
            0,
        )

        self.add_z_axis(self.blobs[0])

        self.blobs[0].draw()

        self.display.update()

    def plot_square_grid(self: Self, planets: list[MassiveBlob]) -> None:
        """Iterates through blobs and plots them in a square grid configuration around the center blob"""
        x = self.blobs[0].x
        y = self.blobs[0].y
        z = self.blobs[0].z
        scaled_half_universe_w = self.blobs[0].x
        scaled_half_universe_h = self.blobs[0].y
        blob_partition: float = 0.0

        # split the screen up into enough partitions for every blob
        blob_partition = AU * 2

        if blob_partition < ((bg_vars.max_radius * bg_vars.scale_up) * 3):
            blob_partition = round((bg_vars.max_radius * bg_vars.scale_up) * 3)

        clearance = 2.0  # float((blob_partition * 2) / blob_partition)

        if clearance % 2:
            clearance += 1

        # Iterators grid placement
        y_count = round(clearance)
        y_turns = 0
        x_turns = 1
        x += (clearance / 2) * blob_partition
        y -= (clearance / 2) * blob_partition

        for i in range(0, len(planets)):

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

            self.add_pos_vel(planets[i], x, y, z)

    def plot_circular_grid(self: Self, planets: list[MassiveBlob]) -> None:
        """Iterates through blobs and plots them in a circular grid configuration around the center blob"""

        scaled_half_universe_w = self.blobs[0].x
        scaled_half_universe_h = self.blobs[0].y

        orbiting_blobs = len(planets)

        # Iterators for circular grid placement, blobs will be placed in ever
        # increasing sized circles around the center blob
        plot_phi = 0.0
        plot_phi_offset = 0.0
        plot_theta = math.pi * 0.5

        # How much the radius will increase each time we move to the next biggest
        # circle around the center blob (the size will be some multiple of the diameter of the biggest
        # blob)
        plot_radius_partition = AU * 2  # ((MAX_RADIUS * 10)) * SCALE_UP

        # The start radius (smallest circle around center blob)
        plot_radius = AU * 4

        # How far apart each blob will be on each circumference
        chord_scaled = (math.pi * (plot_radius * 2)) / 6

        if chord_scaled < ((bg_vars.max_radius * 3) * bg_vars.scale_up):
            chord_scaled = (bg_vars.max_radius * 3) * bg_vars.scale_up

        if chord_scaled > (plot_radius * 2):
            chord_scaled = (bg_vars.max_radius * 3) * bg_vars.scale_up

        # How many radians to increase for each blob around the circumference (such that
        # we get chord_scaled length between each blob center)
        pi_inc = math.asin(chord_scaled / (plot_radius * 2)) * 2

        # Divy up the remainder for a more even distribution
        pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

        blobs_left = orbiting_blobs

        if ((math.pi * 2) / pi_inc) > (orbiting_blobs):
            pi_inc = (math.pi * 2) / (orbiting_blobs)

        for i in range(0, len(planets)):

            self.display.update()

            # Circular grid x,y plot for this blob
            # Get x and y for this blob, vars set up from last iteration or initial setting
            x = scaled_half_universe_w + plot_radius * math.sin(plot_theta) * math.cos(
                plot_phi_offset
            )
            y = scaled_half_universe_h + plot_radius * math.sin(plot_theta) * math.sin(
                plot_phi_offset
            )
            z = scaled_half_universe_h + plot_radius * math.cos(plot_theta)

            blobs_left -= 1
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

                plot_phi_offset = random.random() * (math.pi * 2)

            else:
                plot_phi += pi_inc
                plot_phi_offset += pi_inc

            self.add_pos_vel(planets[i], x, y, z)

    def add_z_axis(self: Self, blob: MassiveBlob) -> None:
        """Adds the given blob to the z_axis dict according to it z position"""
        if self.z_axis.get(blob.z) is None:
            self.z_axis[blob.z] = np.array([blob], dtype=MassiveBlob)
        else:
            self.z_axis[blob.z] = np.append(
                self.z_axis[blob.z], np.array([blob], dtype=MassiveBlob)
            )

    def add_pos_vel(
        self: Self, blob: MassiveBlob, x: float, y: float, z: float
    ) -> None:
        """Adds z,y,z to given blob, and configures velocity for orbit around center blob"""
        velocity: float = 0.0
        # Figure out velocity for this blob
        dx = self.blobs[0].x - x
        dy = self.blobs[0].y - y
        dz = self.blobs[0].z - z
        d = math.sqrt(dx**2 + dy**2 + dz**2)

        # get velocity for a perfect orbit around center blob
        velocity = math.sqrt(G * bg_vars.center_blob_mass / d)

        if not self.start_perfect_orbit:
            for _ in range(1, random.randint(1, 2)):
                velocity *= random.randint(0, 1) + (random.random())

        theta = math.acos(dz / d)
        phi = math.atan2(dy, dx)

        if self.start_angular_chaos:
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
            y,
            z,
            velocityx + blob.vx,
            velocityy + blob.vy,
            velocityz + blob.vz,
        )

        if bg_vars.start_pos_rotate_x:
            blob.rotate_x()

        if bg_vars.start_pos_rotate_y:
            blob.rotate_y()

        if bg_vars.start_pos_rotate_z:
            blob.rotate_z()

        self.add_z_axis(blob)

        blob.draw()

        self.display.update()
