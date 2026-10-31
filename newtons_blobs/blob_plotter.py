"""
Newton's Laws, a simulator of physics at the scale of space

Class file for setting up initial positions and velocities of blobs and maintaining them

by Jason Mott, copyright 2025
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
__copyright__ = "Copyright 2026"
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
        Iterates the blobs and calls draw(), also calls self.blob_factory.grid_check()

    populate_grid() -> None
        Takes the  get_next_proximity_queue() and puts the current
        self.blobs into it by blob.grid_key, and assigns it to self.proximity_grid

    update_blobs() -> None
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range

    plot_center_blob(universe: BlobUniverse) -> None
        Creates and places the center blob and adds it to self.blobs[0]

    plot_orbitals() -> None
        Iterates through blobs and plots them in a circular (default) or square orbital formation around the center blob

    add_pos_vel(blob: MassiveBlob, position: BVec3) -> None
        Adds position to given blob, and configures velocity for orbit around center blob

    """

    def __init__(
        self: Self,
        blob_factory: BlobPluginFactory,
    ):
        self.blob_factory: BlobPluginFactory = blob_factory
        self.display = self.blob_factory.get_blob_display()

        bp.set_gravitational_range(bg_vars.universe_size * bg_vars.scale_up)

        self.tilt_roll: float = 0
        self.tilt_yaw: float = 0
        self.tilt: BVec3 = None

        # Preferences/states
        self.blobs: npt.NDArray = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        self.blobs_swallowed: int = 0
        self.blobs_escaped: int = 0
        self.proximity_grid: npt.NDArray = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
            ],
            dtype=object,
        )

        self.scaled_universe: float = bg_vars.universe_size * bg_vars.scale_up
        self.num_moons: int = (NUM_BLOBS - 1) - bg_vars.num_planets
        self.square_grid: bool = bg_vars.square_blob_plotter
        self.start_perfect_orbit: bool = bg_vars.start_perfect_orbit
        self.start_angular_chaos: bool = bg_vars.start_angular_chaos

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""

        # Changed the name of this variable, need to deal with old save files
        # that have the old variable name
        if data.get("universe_size_w", None) is not None:
            del data["universe_size_w"]
        if data.get("universe_size_h", None) is not None:
            del data["universe_size_h"]

        data["blobs_swallowed"] = self.blobs_swallowed
        data["blobs_escaped"] = self.blobs_escaped
        data["square_grid"] = self.square_grid
        data["start_perfect_orbit"] = self.start_perfect_orbit
        data["start_angular_chaos"] = self.start_angular_chaos
        data["coll_hits"] = bp.hits
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

        self.blobs_swallowed = data["blobs_swallowed"]
        self.blobs_escaped = data["blobs_escaped"]
        self.square_grid = data["square_grid"]
        self.start_perfect_orbit = data["start_perfect_orbit"]
        self.start_angular_chaos = data["start_angular_chaos"]
        self.blobs = np.empty([NUM_BLOBS], dtype=MassiveBlob)
        bp.set_gravitational_range(bg_vars.universe_size * bg_vars.scale_up)
        bp.hits.clear()
        bp.hits = data.get("coll_hits", dict())

        self.scaled_universe = bg_vars.universe_size * bg_vars.scale_up
        self.proximity_grid.fill(None)
        self.proximity_grid = np.empty(
            [
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
                int(bg_vars.grid_key_upper_bound),
            ],
            dtype=object,
        )

        view_pos: Tuple[float, float, float] = None
        view_rot: Tuple[float, float, float] = None
        view_follow_pos: Tuple[float, float, float] = None
        view_follow_index: int = -1
        if data.get("view_pos", None) is not None:
            view_pos = tuple(data["view_pos"])
            view_rot = tuple(data["view_rot"])
        if data.get("view_follow_index") is not None:
            view_follow_index = int(data["view_follow_index"])

        i = 0
        for blob_pref in data["blobs"]:
            if view_follow_index == int(blob_pref["index"]):
                view_follow_pos = tuple(
                    (
                        blob_pref["x"] * bg_vars.scale_down,
                        blob_pref["y"] * bg_vars.scale_down,
                        blob_pref["z"] * bg_vars.scale_down,
                    )
                )
            else:
                view_follow_pos = None
            self.blobs[blob_pref["index"]] = MassiveBlob(
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
                    view_pos,  # Might not exist
                    view_rot,  # Might not exist
                    view_follow_pos,  # Might not exist
                ),
                blob_pref["mass"],
                BVec3(blob_pref["x"], blob_pref["y"], blob_pref["z"]),
                BVec3(blob_pref["vx"], blob_pref["vy"], blob_pref["vz"]),
            )

            if blob_pref.get("blobs_combined", None) is not None:
                self.blobs[blob_pref["index"]].blobs_combined = blob_pref[
                    "blobs_combined"
                ]

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

        universe = self.blob_factory.get_blob_universe()
        universe.clear()
        self.display.update()

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

        self.scaled_universe = bg_vars.universe_size * bg_vars.scale_up

        bp.hits.clear()
        bp.set_gravitational_range(self.scaled_universe)
        bp.setup()

        self.display.update()
        self.blobs_swallowed = 0
        self.blobs_escaped = 0

        if plot_blobs:
            self.proximity_grid.fill(None)
            self.proximity_grid = np.empty(
                [
                    int(bg_vars.grid_key_upper_bound),
                    int(bg_vars.grid_key_upper_bound),
                    int(bg_vars.grid_key_upper_bound),
                ],
                dtype=object,
            )

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

                if round(blob_random.random() * 100, 2) <= 60:
                    # rocky planet
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
                    # gas/ice giant planet
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

                # For debugging/testing
                # radius = bg_vars.min_radius
                # mass = bg_vars.max_mass * 1
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

                # radius = bg_vars.min_moon_radius
                # mass = bg_vars.max_mass * 1

            # Phew, let's instantiate this puppy . . .
            self.blobs[i] = MassiveBlob(
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

        self.plot_orbitals(planets, self.square_grid)

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
        Iterates the blobs and calls draw(), also calls self.blob_factory.grid_check()
        """
        self.blob_factory.grid_check(self.proximity_grid)

        for blob in self.blobs:
            blob.draw()

    def populate_grid(self: Self) -> None:
        """
        Takes the  get_next_proximity_queue() and puts the current
        self.blobs into it by blob.grid_key, and assigns it to self.proximity_grid
        """
        self.proximity_grid.fill(None)

        blob: MassiveBlob
        for blob in self.blobs:
            grid_key = blob.grid_key

            if self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] is None:
                self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = np.array(
                    [blob], dtype=MassiveBlob
                )
            else:
                self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]] = np.append(
                    self.proximity_grid[grid_key[0]][grid_key[1]][grid_key[2]], blob  # type: ignore
                )

    def print_proximity_grid(self: Self) -> None:
        """for debug purposes . . ."""
        for x in range(len(self.proximity_grid)):
            for y in range(len(self.proximity_grid[x])):
                for z in range(len(self.proximity_grid[x][y])):
                    if self.proximity_grid[x][y][z] is None:
                        # print(f"{x}-{y}-{z}: 0")
                        pass
                    else:
                        print(f"{x}-{y}-{z}: {len(self.proximity_grid[x][y][z])}")
                        for blob in self.proximity_grid[x][y][z]:
                            print(f"{blob.name}")

    def update_blobs(self: Self, dt: float = 1 / FRAME_RATE) -> None:
        """
        Traverses the proximity grid to check blobs for collision and gravitational pull, and populates the z_axis dict
        The center blob is treated differently to ensure all blobs are checked against its gravitational pull rather than just
        blobs within its proximity grid range
        """
        checked: Dict[int, int] = {}
        check_edge: Callable[[MassiveBlob], None] = bp.edge_detection

        def swallow_edge(blob: MassiveBlob) -> None:
            pass

        def check_blobs_wrap(
            blob1: MassiveBlob,
            blobs: npt.NDArray,
            pos_offsets: Tuple[float, float, float],
            offset: bool = False,
        ) -> None:
            if blobs is None:
                return

            blob2: MassiveBlob
            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):

                    if offset:
                        blob2.x += pos_offsets[0]
                        blob2.y += pos_offsets[1]
                        blob2.z += pos_offsets[2]
                        bp.gravity_collision(blob1, blob2)
                        blob2.x -= pos_offsets[0]
                        blob2.y -= pos_offsets[1]
                        blob2.z -= pos_offsets[2]

                    else:

                        bp.gravity_collision(blob1, blob2)

        def check_grid_wrap(blob: MassiveBlob) -> None:

            gk: Tuple[int, int, int] = blob.grid_key

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            x_pos_offset: float = 0
            y_pos_offset: float = 0
            z_pos_offset: float = 0

            check_edge(blob)

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
                                self.proximity_grid[x][y][z],
                                (x_pos_offset, y_pos_offset, z_pos_offset),
                            )
                        except:

                            if x > bg_vars.grid_key_check_bound:
                                x = 0
                                x_pos_offset = self.scaled_universe
                            elif x < 0:
                                x_pos_offset = -self.scaled_universe

                            if y > bg_vars.grid_key_check_bound:
                                y = 0
                                y_pos_offset = self.scaled_universe
                            elif y < 0:
                                y_pos_offset = -self.scaled_universe

                            if z > bg_vars.grid_key_check_bound:
                                z = 0
                                z_pos_offset = self.scaled_universe
                            elif z < 0:
                                z_pos_offset = -self.scaled_universe

                            check_blobs_wrap(
                                blob,
                                self.proximity_grid[x][y][z],
                                (x_pos_offset, y_pos_offset, z_pos_offset),
                                True,
                            )

                            x_pos_offset = 0
                            y_pos_offset = 0
                            z_pos_offset = 0
                            continue

        def check_blobs_edge(blob1: MassiveBlob, blobs: npt.NDArray) -> None:
            if blobs is None:
                return

            blob2: MassiveBlob
            for blob2 in blobs:
                if (id(blob2) != id(blob1)) and (checked.get(id(blob2)) is None):

                    bp.gravity_collision(blob1, blob2)

        def check_grid_edge(blob: MassiveBlob) -> None:

            gk: Tuple[int, int, int] = blob.grid_key

            # Using the grid approach for optimization. Instead of every blob checking every blob,
            # every blob only checks the blobs in their own grid cell and the grid cells surrounding them.

            check_edge(blob)

            for x_i_offset in range(-1, 2):
                x = gk[0] + x_i_offset

                for y_i_offset in range(-1, 2):
                    y = gk[1] + y_i_offset

                    for z_i_offset in range(-1, 2):
                        z = gk[2] + z_i_offset

                        if x_i_offset != 0 and y_i_offset != 0 and z_i_offset != 0:
                            continue
                        try:
                            check_blobs_edge(blob, self.proximity_grid[x][y][z])
                        except Exception:
                            continue

        iterations: int = 1  # round(bg_vars.timescale / bg_vars.timescale_inc)

        itr_dt: Decimal = Decimal(dt) / Decimal(iterations)

        if bg_vars.center_blob_escape:
            check_edge = swallow_edge

        check_grid: Callable[[MassiveBlob], None] = check_grid_edge
        if not bg_vars.center_blob_escape and bg_vars.wrap_if_no_escape:
            check_grid = check_grid_wrap

        for _ in range(iterations):

            checked.clear()

            for i in range(1, len(self.blobs)):
                bp.gravity_collision(self.blobs[0], self.blobs[i])

            checked[id(self.blobs[0])] = 1

            blob: MassiveBlob
            for blob in np.flip(self.blobs):

                check_grid(blob)

                checked[id(blob)] = 1

                if blob.dead:
                    if blob.swallowed:
                        self.blobs_swallowed += 1
                    elif blob.escaped:
                        self.blobs_escaped += 1
                    dgk: Tuple[int, int, int] = blob.grid_key

                    self.proximity_grid[dgk[0]][dgk[1]][dgk[2]] = np.delete(
                        self.proximity_grid[dgk[0]][dgk[1]][dgk[2]],
                        np.where(self.proximity_grid[dgk[0]][dgk[1]][dgk[2]] == blob)[
                            0
                        ],
                    )
                    self.blobs = np.delete(self.blobs, np.where(self.blobs == blob)[0])
                    blob.destroy()
                    continue

                old_key: Tuple[int, int, int] = blob.grid_key

                blob.advance(itr_dt)

                if blob.grid_key_chgd:

                    self.proximity_grid[old_key[0]][old_key[1]][old_key[2]] = np.delete(
                        self.proximity_grid[old_key[0]][old_key[1]][old_key[2]],
                        np.where(
                            self.proximity_grid[old_key[0]][old_key[1]][old_key[2]]
                            == blob
                        )[0],
                    )

                    gk: Tuple[int, int, int] = blob.grid_key

                    if self.proximity_grid[gk[0]][gk[1]][gk[2]] is None:
                        self.proximity_grid[gk[0]][gk[1]][gk[2]] = np.array(
                            [blob], dtype=MassiveBlob
                        )
                    else:
                        self.proximity_grid[gk[0]][gk[1]][gk[2]] = np.append(
                            self.proximity_grid[gk[0]][gk[1]][gk[2]], blob  # type: ignore
                        )

    def plot_center_blob(self: Self) -> None:
        """Creates and places the center blob and adds it to self.blobs[0]"""

        # create the tilt of the solar system
        self.tilt_roll = blob_random.random() * math.pi * 2
        self.tilt_yaw = blob_random.random() * math.pi * 2

        # Define a plane normal vector to tilt the circle
        self.tilt = BVec3.tilt(self.tilt_roll, self.tilt_yaw)

        tilt_roll_deg: float = self.tilt_roll * (180 / math.pi)
        tilt_yaw_deg: float = self.tilt_yaw * (180 / math.pi)

        # Set up the center blob, which will be the massive star all other blobs orbit
        position: BVec3 = BVec3(
            *self.blob_factory.get_blob_universe().get_center_blob_start_pos()
        )

        self.blobs[0] = MassiveBlob(
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

        self.blobs[0].blob_surface.ursina_blob.rotation_pos = (
            0,
            tilt_roll_deg,
            tilt_yaw_deg,
        )

        self.blobs[0].draw()

        self.display.update()

    def plot_orbitals(
        self: Self, planets: list[MassiveBlob], square: bool = False
    ) -> None:
        """Iterates through blobs and plots them in a circular (default) or square orbital formation around the center blob"""

        center: BVec3 = self.blobs[0].position

        cross_a: BVec3 = None
        cross_b: BVec3 = None

        cross_a, cross_b = self.tilt.cross_a_b()

        orbiting_blobs: int = len(planets)

        # Iterators for circular grid placement, blobs will be placed in ever
        # increasing sized circles around the center blob
        plot_phi: float = 0.0
        plot_phi_offset: float = 0.0

        # How much the radius will increase each time we move to the next biggest
        # circle around the center blob (the size will be some multiple of the diameter of the biggest
        # blob)
        plot_radius_partition: float = AU * 4

        # The start radius (smallest circle around center blob)
        plot_radius: float = AU * 4

        # arc length between each blob, i.e. how many blobs in the first orbital circumference
        arc: float = (math.pi * (plot_radius * 2)) / 10

        # How far apart each blob will be on each circumference
        chord_scaled: float = 2 * plot_radius * math.sin(arc / (plot_radius * 2))

        # How many radians to increase for each blob around the circumference (such that
        # we get chord_scaled length between each blob center)
        pi_inc: float = math.asin(chord_scaled / (plot_radius * 2)) * 2

        # Divy up the remainder for a more even distribution
        pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

        blobs_left: int = orbiting_blobs

        stagger_radius: bool = False

        if ((math.pi * 2) / pi_inc) > (orbiting_blobs):
            stagger_radius = True
            pi_inc = (math.pi * 2) / (orbiting_blobs)
            plot_radius_partition /= 2

        mag: float = 0.0

        for i in range(0, len(planets)):

            self.display.update()

            mag = plot_radius

            if square:
                # if angle is evenly divisible by 90 degrees (points straight up/down
                # or straight left/right), radius doesn't need adjustment to reach edge of square
                if plot_phi_offset % (math.pi / 2) == 0:
                    mag = plot_radius
                else:
                    # determine if plot_phi_offset is pointing up (higher than 0.25 rads and lower than 0.75 rads)
                    # or right/left (lower than 0.25 rads or higher than 0.75 rads)
                    # i.e., do we use sine or cosine to stretch the radius (mag) to edge of square?

                    # just use top half of circle to reduce conditional check
                    my_phi: float = plot_phi_offset
                    if plot_phi_offset > math.pi:
                        my_phi = plot_phi_offset - math.pi

                    if my_phi > (math.pi * 0.25) and my_phi < (math.pi * 0.75):
                        mag = abs(plot_radius / math.sin(plot_phi_offset))
                    else:
                        mag = abs(plot_radius / math.cos(plot_phi_offset))

            # position for planets[i] blob
            blob_pos: BVec3 = (
                center
                + (
                    cross_a * math.cos(plot_phi_offset)
                    + cross_b * math.sin(plot_phi_offset)
                ).normalize()
                * mag
            )

            blobs_left -= 1

            # if we're staggering the plots, no two plots share the same radius,
            # so add plot_radius partition
            if blobs_left > 0 and stagger_radius:
                plot_radius += plot_radius_partition + (
                    blob_random.random() * plot_radius_partition
                )

            # otherwise make plot radius longer by plot_radius_partition only if we've gone around 360 degrees
            if not stagger_radius and round(plot_phi + pi_inc, 8) > round(
                (math.pi * 2) - (pi_inc), 8
            ):
                plot_phi = 0.0

                plot_radius += plot_radius_partition

                # How many radians to increase for each blob around the circumference (such that
                # we get chord_scaled length between each blob center)
                pi_inc = math.asin(chord_scaled / (plot_radius * 2)) * 2
                # Divy up the remainder for a more even distribution
                pi_inc += ((math.pi * 2) % pi_inc) / ((math.pi * 2) / pi_inc)

                # if there aren't enough blobs left to go around the circumference with the given increment, adjust increment accordingly
                if blobs_left > 0 and ((math.pi * 2) / pi_inc) > blobs_left:
                    pi_inc = (math.pi * 2) / blobs_left

                plot_phi_offset = blob_random.random() * (math.pi * 2)

            else:
                # move the "clock dial" another notch
                plot_phi += pi_inc
                plot_phi_offset += pi_inc
                if plot_phi_offset > (math.pi * 2):
                    plot_phi_offset -= math.pi * 2

            self.add_pos_vel(planets[i], blob_pos)
            self.blob_factory.loading_screen_add_count()

        self.blob_factory.set_plot_radius(plot_radius)

    def add_pos_vel(self: Self, blob: MassiveBlob, position: BVec3) -> None:
        """Adds position to given blob, and configures velocity for orbit around center blob"""

        orbit_pos: BVec3 = position.relative_to(self.blobs[0].position)
        d: float = orbit_pos.mag()

        # get velocity for a perfect orbit around center blob
        velocity: float = math.sqrt(G * bg_vars.center_blob_mass / d)

        if not self.start_perfect_orbit:
            for _ in range(1, blob_random.randint(1, 3)):
                velocity = velocity * (blob_random.randint(0, 1) + blob_random.random())

        # turn 90 degrees from pointing away from center for beginning velocity (orbit)
        trajectory: BVec3 = self.tilt.cross(orbit_pos).normalize()

        if self.start_angular_chaos:
            # Add some chaos to starting trajectory

            cross_a: BVec3 = trajectory
            cross_b: BVec3 = self.tilt

            phi: float = blob_random.random() * (math.pi * 2)

            trajectory = BVec3(
                (math.cos(phi) * cross_a.x + math.sin(phi) * cross_b.x),
                (math.cos(phi) * cross_a.y + math.sin(phi) * cross_b.y),
                (math.cos(phi) * cross_a.z + math.sin(phi) * cross_b.z),
            ).normalize()

        add_velocity: BVec3 = trajectory * velocity

        # Phew, let's instantiate this puppy . . .
        blob.update_pos_vel(
            position,
            blob.velocity + add_velocity,
        )

        blob.draw()

        self.display.update()
