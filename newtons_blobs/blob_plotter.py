"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial positions and velocities of blobs and maintaining them

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, Dict, Tuple, Self
import numpy as np
import numpy.typing as npt
import math
from decimal import *

from .globals import *
from .blob_global_vars import BlobGlobalVars as bg_vars
from .blob_random import blob_random
from .blob_plugin_factory import BlobPluginFactory
from .massive_blob import MassiveBlob
from .blob_vector import BlobVector as BVec3
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

    get_next_proximity_queue() -> npt.NDArray
        Used to switch proximity queues, so we can prepare one while using the existing one uninterrupted

    populate_grid() -> None
        Takes the  get_next_proximity_queue() and puts the current
        self.blobs into it by blob.grid_key(), and assigns it to self.proximity_grid

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

    add_pos_vel(blob: MassiveBlob, position: BVec3) -> None
        Adds position to given blob, and configures velocity for orbit around center blob

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
        bp.set_gravitational_range(bg_vars.universe_size * bg_vars.scale_up)

        # Preferences/states
        self.blobs: npt.NDArray = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.blobs_swallowed: int = 0
        self.blobs_escaped: int = 0
        self.proximity_queue1: npt.NDArray = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
            ],
            dtype=object,
        )
        self.proximity_queue2: npt.NDArray = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
            ],
            dtype=object,
        )
        self.proximity_grid: npt.NDArray = None
        self.queue_index: int = 1

        self.num_moons: int = (NUM_BLOBS - 1) - bg_vars.num_planets
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
        self.blobs = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        bp.set_gravitational_range(bg_vars.universe_size * bg_vars.scale_up)

        i = 0
        for blob_pref in data["blobs"]:
            self.blobs[blob_pref["index"]] = MassiveBlob(
                self.universe_size_h,
                blob_pref["index"],
                blob_pref["name"],
                self.blob_factory.new_blob_surface(
                    blob_pref["index"],
                    blob_pref["name"],
                    blob_pref["radius"] * bg_vars.au_scale_factor,
                    blob_pref["mass"],
                    tuple(blob_pref["color"]),  # type: ignore
                    blob_pref.get("trail_color", None),  # Might not exist
                    blob_pref.get("texture", None),  # Might not exist
                    blob_pref.get("ring_texture", None),  # Might not exist
                    blob_pref.get("ring_scale", None),  # Might not exist
                    blob_pref.get("rotation_speed", None),  # Might not exist
                    blob_pref.get("rotation_pos", None),  # Might not exist
                ),
                blob_pref["mass"],
                BVec3(blob_pref["x"], blob_pref["y"], blob_pref["z"]),
                BVec3(blob_pref["vx"], blob_pref["vy"], blob_pref["vz"]),
            )

            self.blobs[blob_pref["index"]].blob_surface.barycenter_index = (
                blob_pref.get("barycenter_index", 0)
            )

            i += 1

        for blob in self.blobs:
            if blob is not None:
                if blob.blob_surface.barycenter_index > 0:
                    blob.blob_surface.set_barycenter(
                        self.blobs[blob.blob_surface.barycenter_index].blob_surface
                    )

        self.blobs = np.delete(self.blobs, np.where(self.blobs == None)[0])
        self.populate_grid()

    def start_over(self: Self, plot_blobs: bool = True) -> None:
        """Clears all variables to initial state (i.e. deletes all blobs), and calls plot_blobs()"""

        if plot_blobs:
            self.blob_factory.reset()
        else:
            self.blob_factory.reset(1)

        self.display.update()
        for blob in np.flip(self.blobs):
            blob.destroy()
            self.display.update()

        self.blobs = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.display.update()

        universe = self.blob_factory.get_blob_universe()
        universe.clear()
        self.display.update()

        self.universe_size_w = universe.get_width()
        self.universe_size_h = universe.get_height()

        self.display.update()
        self.blobs_swallowed = 0
        self.blobs_escaped = 0

        if plot_blobs:
            self.plot_blobs()

    def plot_blobs(self: Self) -> None:
        """
        Creates MassiveBlob instances and plots their initial x,y,z coordinates, all according to global constant preferences
        """
        self.plot_center_blob()

        planets: list[MassiveBlob] = []

        radius_min_max_halfway: float = (bg_vars.min_radius + bg_vars.max_radius) / 2

        radius_halfway_min_halfway: float = (
            bg_vars.min_radius + radius_min_max_halfway
        ) / 2

        radius_halfway_max_halfway: float = (
            radius_min_max_halfway + bg_vars.max_radius
        ) / 2

        # ---------------------------------------------------------------------------

        mass_min_max_halfway: float = (bg_vars.min_mass + bg_vars.max_mass) / 2

        mass_halfway_min_halfway: float = (bg_vars.min_mass + mass_min_max_halfway) / 2

        mass_halfway_max_halfway = (mass_min_max_halfway + bg_vars.max_mass) / 2

        ############################################################################

        moons: list[MassiveBlob] = []

        moon_radius_min_max_halfway: float = (
            bg_vars.min_moon_radius + bg_vars.max_moon_radius
        ) / 2

        # ---------------------------------------------------------------------------

        moon_mass_min_max_halfway: float = (
            bg_vars.min_moon_mass + bg_vars.max_moon_mass
        ) / 2

        moon: bool = False

        # Create orbiting blobs without position or velocity
        for i in range(1, NUM_BLOBS):
            # Set up some random values for this blob
            color: int = round(blob_random.random() * (len(COLORS) - 1))
            radius: float = 0.0
            mass: float = 0.0

            if i > self.num_moons:

                moon = False

                if blob_random.randint(1, 10) > 4:
                    radius = round(
                        (
                            blob_random.random()
                            * (radius_halfway_min_halfway - bg_vars.min_radius)
                        )
                        + bg_vars.min_radius,
                        2,
                    )

                    mass = (
                        blob_random.random()
                        * (mass_halfway_min_halfway - bg_vars.min_mass)
                        + bg_vars.min_mass
                    )
                else:
                    radius = round(
                        (
                            blob_random.random()
                            * (bg_vars.max_radius - radius_halfway_max_halfway)
                        )
                        + radius_halfway_max_halfway,
                        2,
                    )

                    mass = (
                        blob_random.random()
                        * (bg_vars.max_mass - mass_halfway_max_halfway)
                    ) + mass_halfway_max_halfway
            else:
                moon = True
                radius = round(
                    (
                        blob_random.random()
                        * (bg_vars.max_moon_radius - bg_vars.min_moon_radius)
                    )
                    + bg_vars.min_moon_radius,
                    2,
                )

                if radius > moon_radius_min_max_halfway:
                    mass = (
                        blob_random.random()
                        * (bg_vars.max_moon_mass - moon_mass_min_max_halfway)
                    ) + moon_mass_min_max_halfway
                else:
                    mass = (
                        blob_random.random()
                        * (moon_mass_min_max_halfway - bg_vars.min_moon_mass)
                    ) + bg_vars.min_moon_mass

            # Phew, let's instantiate this puppy . . .
            self.blobs[i] = MassiveBlob(
                self.universe_size_h,
                i,
                str(i),
                self.blob_factory.new_blob_surface(
                    i, str(i), radius, mass, COLORS[color]
                ),
                mass,
                BVec3(0, 0, 0),
                BVec3(0, 0, 0),
            )

            if moon:
                moons.append(self.blobs[i])
            else:
                planets.append(self.blobs[i])

        self.blob_factory.loading_screen_start(
            len(self.blobs) - 1, "plotting blobs . . . "
        )
        if self.square_grid:
            self.plot_square_grid(planets)
        else:
            self.plot_circular_grid(planets)

        if len(moons) > 0:
            self.plot_moons(moons, planets)

        self.populate_grid()

        self.blob_factory.loading_screen_end(True)

    def plot_moons(
        self: Self, moons: list[MassiveBlob], planets: list[MassiveBlob]
    ) -> None:

        min_distance: float = bg_vars.min_moon_radius * bg_vars.scale_up * 2
        tries: int = 5

        for i in range(0, len(moons)):

            tries = 5
            planet: MassiveBlob = planets[blob_random.randint(0, len(planets) - 1)]

            while tries > 0:
                tries -= 1
                planet.add_orbital(moons[i])
                cleared = True
                for y in range(0, i):
                    if not bp.is_distance_cleared(moons[i], moons[y], min_distance):
                        cleared = False
                if cleared:
                    tries = 0

            moons[i].update_pos_vel(
                moons[i].position, moons[i].velocity + planet.velocity
            )
            self.blob_factory.loading_screen_add_count()

    def draw_blobs(self: Self) -> None:
        """
        Iterates the blobs according z_axis keys, deletes the ones flagged as dead, calls draw() on the live ones, and repopulates
        the proximity_grid array according to new coordinates
        """
        self.blob_factory.grid_check(self.proximity_grid)

        for blob in self.blobs:
            blob.draw()

    def get_next_proximity_queue(self: Self) -> npt.NDArray:
        """Used to switch proximity queues, so we can prepare one while using the existing one uninterrupted"""
        if self.queue_index == 2:
            self.proximity_queue1.fill(None)
            self.queue_index = 1
            return self.proximity_queue1

        else:
            self.proximity_queue2.fill(None)
            self.queue_index = 2
            return self.proximity_queue2

    def populate_grid(self: Self) -> None:
        """
        Takes the  get_next_proximity_queue() and puts the current
        self.blobs into it by blob.grid_key(), and assigns it to self.proximity_grid
        """

        self.proximity_grid = self.get_next_proximity_queue()

        for blob in self.blobs:
            grid_key = blob.grid_key()

            if self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] is None:
                self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = np.array(
                    [blob], dtype=MassiveBlob
                )
            else:
                self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = np.append(
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]],
                    blob,
                )

        # for debug purposes . . .
        # for x in range(len(self.proximity_grid)):
        #     for y in range(len(self.proximity_grid[x])):
        #         for z in range(len(self.proximity_grid[x][y])):
        #             if self.proximity_grid[x][y][z] is None:
        #                 # print(f"{x}-{y}-{z}: 0")
        #                 pass
        #             else:
        #                 print(f"{x}-{y}-{z}: {len(self.proximity_grid[x][y][z])}")
        #                 for blob in self.proximity_grid[x][y][z]:
        #                     print(f"{blob.name}")

    def update_blobs(self: Self, dt: float = 1 / FRAME_RATE) -> None:
        """
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range
        """
        checked: Dict[int, int] = {}
        pg: npt.NDArray = None
        new_pg: npt.NDArray = None
        check_edge: Callable[[MassiveBlob], None] = bp.edge_detection

        def swallow_edge(blob: MassiveBlob) -> None:
            pass

        def check_blobs_wrap(
            blob1: MassiveBlob,
            blobs: npt.NDArray,
            pos_offsets: Tuple[float, float, float],
            this_dt: Decimal,
            offset: bool = False,
        ) -> None:
            if blobs is None:
                return

            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):

                    if offset:
                        blob2.x += pos_offsets[0]
                        blob2.y += pos_offsets[1]
                        blob2.z += pos_offsets[2]
                        bp.gravity_collision(blob1, blob2, this_dt)
                        blob2.x -= pos_offsets[0]
                        blob2.y -= pos_offsets[1]
                        blob2.z -= pos_offsets[2]

                    else:

                        bp.gravity_collision(blob1, blob2, this_dt)

            check_edge(blob1)

        def check_grid_wrap(blob: MassiveBlob, this_dt: Decimal) -> None:

            gk: Tuple[int, int, int] = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            x_pos_offset: float = 0
            y_pos_offset: float = 0
            z_pos_offset: float = 0
            scaled_universe: float = blob.scaled_universe_size

            for x_i_offset in range(-1, 2):
                x = gk[0] + x_i_offset

                for y_i_offset in range(-1, 2):
                    y = gk[1] + y_i_offset

                    for z_i_offset in range(-1, 2):
                        z = gk[2] + z_i_offset

                        # Skip the corners of the cube, worth risking the occasional miss for the performance boost
                        if x_i_offset != 0 and y_i_offset != 0 and z_i_offset != 0:
                            continue

                        try:
                            check_blobs_wrap(
                                blob,
                                pg[x][y][z],
                                (x_pos_offset, y_pos_offset, z_pos_offset),
                                this_dt,
                            )
                        except:

                            if x > bg_vars.grid_key_check_bound:
                                x = 0
                                x_pos_offset = scaled_universe
                            elif x < 0:
                                x_pos_offset = -scaled_universe

                            if y > bg_vars.grid_key_check_bound:
                                y = 0
                                y_pos_offset = scaled_universe
                            elif y < 0:
                                y_pos_offset = -scaled_universe

                            if z > bg_vars.grid_key_check_bound:
                                z = 0
                                z_pos_offset = scaled_universe
                            elif z < 0:
                                z_pos_offset = -scaled_universe

                            check_blobs_wrap(
                                blob,
                                pg[x][y][z],
                                (x_pos_offset, y_pos_offset, z_pos_offset),
                                this_dt,
                                True,
                            )

                            x_pos_offset = 0
                            y_pos_offset = 0
                            z_pos_offset = 0
                            continue

        def check_blobs_edge(
            blob1: MassiveBlob,
            blobs: npt.NDArray,
            this_dt: Decimal,
        ) -> None:
            if blobs is None:
                return

            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):

                    bp.gravity_collision(blob1, blob2, this_dt)

            check_edge(blob1)

        def check_grid_edge(blob: MassiveBlob, this_dt: Decimal) -> None:

            gk: Tuple[int, int, int] = blob.grid_key()

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            for x_i_offset in range(-1, 2):
                x = gk[0] + x_i_offset

                for y_i_offset in range(-1, 2):
                    y = gk[1] + y_i_offset

                    for z_i_offset in range(-1, 2):
                        z = gk[2] + z_i_offset

                        if x_i_offset != 0 and y_i_offset != 0 and z_i_offset != 0:
                            continue
                        try:
                            check_blobs_edge(
                                blob,
                                pg[x][y][z],
                                this_dt,
                            )
                        except:
                            continue

        iterations: int = 1  # round(bg_vars.timescale / bg_vars.timescale_inc)
        # itr_dt: Decimal = Decimal(dt) * Decimal(
        #     bg_vars.timescale_inc / bg_vars.timescale
        # )
        itr_dt: Decimal = Decimal(dt)

        if bg_vars.center_blob_escape:
            check_edge = swallow_edge

        check_grid: Callable[[MassiveBlob, Decimal], None] = check_grid_edge
        if not bg_vars.center_blob_escape and bg_vars.wrap_if_no_escape:
            check_grid = check_grid_wrap

        for _ in range(iterations):

            pg = self.proximity_grid
            new_pg = self.get_next_proximity_queue()

            checked.clear()

            for i in range(1, len(self.blobs)):
                bp.gravity_collision(self.blobs[0], self.blobs[i], itr_dt)

            check_edge(self.blobs[0])

            self.blobs[0].advance(itr_dt)

            checked[id(self.blobs[0])] = 1

            for blob in np.flip(self.blobs):

                check_grid(blob, itr_dt)

                blob.advance(itr_dt)

                checked[id(blob)] = 1

                if blob.dead:
                    if blob.swallowed:
                        self.blobs_swallowed += 1
                    elif blob.escaped:
                        self.blobs_escaped += 1
                    self.blobs = np.delete(self.blobs, np.where(self.blobs == blob)[0])
                    blob.destroy()
                else:

                    grid_key = blob.grid_key()

                    if new_pg[grid_key[0]][grid_key[1]][grid_key[2]] is None:
                        new_pg[grid_key[0]][grid_key[1]][grid_key[2]] = np.array(
                            [blob], dtype=MassiveBlob
                        )
                    else:
                        new_pg[grid_key[0]][grid_key[1]][grid_key[2]] = np.append(
                            new_pg[grid_key[0]][grid_key[1]][grid_key[2]],
                            blob,
                        )

            self.proximity_grid = new_pg

    def plot_center_blob(self: Self) -> None:
        """Creates and places the center blob and adds it to self.blobs[0]"""

        # Set up the center blob, which will be the massive star all other blobs orbit
        position: BVec3 = BVec3(
            *self.blob_factory.get_blob_universe().get_center_blob_start_pos()
        )

        self.blobs[0] = MassiveBlob(
            self.universe_size_h,
            0,
            CENTER_BLOB_NAME,
            self.blob_factory.new_blob_surface(
                0,
                CENTER_BLOB_NAME,
                bg_vars.center_blob_radius,
                bg_vars.center_blob_mass,
                CENTER_BLOB_COLOR,
            ),
            bg_vars.center_blob_mass,
            position,
            BVec3(0, 0, 0),
        )

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

            self.add_pos_vel(planets[i], BVec3(x, y, z))
            self.blob_factory.loading_screen_add_count()

    def plot_circular_grid(self: Self, planets: list[MassiveBlob]) -> None:
        """Iterates through blobs and plots them in a circular grid configuration around the center blob"""

        scaled_half_universe_w: float = self.blobs[0].x
        scaled_half_universe_h: float = self.blobs[0].y

        orbiting_blobs: int = len(planets)
        blobs_per_ring: int = 10
        if self.num_moons > 1:
            blobs_per_ring = bg_vars.num_planets + 1

        # Iterators for circular grid placement, blobs will be placed in ever
        # increasing sized circles around the center blob
        plot_phi: float = 0.0
        plot_phi_offset: float = 0.0
        plot_theta: float = math.pi * 0.5

        # How much the radius will increase each time we move to the next biggest
        # circle around the center blob (the size will be some multiple of the diameter of the biggest
        # blob)
        plot_radius_partition: float = AU * 4  # ((MAX_RADIUS * 10)) * SCALE_UP

        # The start radius (smallest circle around center blob)
        plot_radius: float = AU * 4

        # arc length between each blob, i.e. how many blobs per circumference
        arc: float = (math.pi * (plot_radius * 2)) / blobs_per_ring

        # How far apart each blob will be on each circumference
        chord_scaled: float = 2 * plot_radius * math.sin(arc / (plot_radius * 2))

        if chord_scaled < ((bg_vars.max_radius * 3) * bg_vars.scale_up):
            chord_scaled = (bg_vars.max_radius * 3) * bg_vars.scale_up

        if chord_scaled > (plot_radius * 2):
            chord_scaled = (bg_vars.max_radius * 3) * bg_vars.scale_up

        # How many radians to increase for each blob around the circumference (such that
        # we get chord_scaled length between each blob center)
        pi_inc: float = math.asin(chord_scaled / (plot_radius * 2)) * 2
        # pi_inc: float = (math.pi * 2) / 5

        # Divy up the remainder for a more even distribution
        pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

        blobs_left: int = orbiting_blobs

        stagger_radius: bool = False

        if ((math.pi * 2) / pi_inc) > (orbiting_blobs):
            stagger_radius = True
            pi_inc = (math.pi * 2) / (orbiting_blobs)
            plot_radius_partition /= 2
            # plot_radius -= AU

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

            if blobs_left > 0 and stagger_radius:
                plot_radius += plot_radius_partition + (
                    blob_random.random() * plot_radius_partition
                )

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

                plot_phi_offset = blob_random.random() * (math.pi * 2)

            else:
                plot_phi += pi_inc
                plot_phi_offset += pi_inc

            self.add_pos_vel(planets[i], BVec3(x, y, z))
            self.blob_factory.loading_screen_add_count()

        self.blob_factory.set_plot_radius(plot_radius)

    def add_pos_vel(self: Self, blob: MassiveBlob, position: BVec3) -> None:
        """Adds position to given blob, and configures velocity for orbit around center blob"""
        velocity: float = 0.0
        # Figure out velocity for this blob

        diff: BVec3 = position.diff(self.blobs[0].position)
        d: float = diff.mag()

        # get velocity for a perfect orbit around center blob
        velocity = math.sqrt(G * bg_vars.center_blob_mass / d)

        if not self.start_perfect_orbit:
            for _ in range(1, blob_random.randint(1, 2)):
                velocity *= blob_random.randint(0, 1) + (blob_random.random())

        theta = math.acos(diff.z / d)
        phi = math.atan2(diff.y, diff.x)

        if self.start_angular_chaos:
            # Add some chaos to starting trajectory
            theta = theta - (math.pi * 0.15)

        # turn 90 degrees from pointing center for beginning velocity (orbit)
        phi = phi - (math.pi * 0.5)

        add_velocity: BVec3 = (
            BVec3(
                math.sin(theta) * math.cos(phi),
                math.sin(theta) * math.sin(phi),
                math.cos(theta),
            )
            * velocity
        )

        # Phew, let's instantiate this puppy . . .
        blob.update_pos_vel(
            position,
            blob.velocity + add_velocity,
        )

        blob.draw()

        self.display.update()
