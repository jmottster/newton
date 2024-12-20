"""
Newton's Laws, a simulator of physics at the scale of space

Class file for the physics attributes of blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

from typing import Any, ClassVar, Dict, Tuple, Self


from .globals import *
from .blob_global_vars import BlobGlobalVars as bg_vars
from .blob_surface import BlobSurface

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class MassiveBlob:
    """
    A class used to represent a massive space blob's physics related attributes

    A massive blob is like a planet or a star

    Attributes
    ----------
    universe_size : float
        the size of the universe in pixels (this size is cubed for full environment size)
    name : str
        a string to identify the blob
    blob_surface : BlobSurface
        the object responsible for drawing blob and maintaining visual attributes
    mass : float
        the mass of the object -- use planet scale kg values (see global min and max values)
    x : float
        initial x coordinate for center of blob
    y : float
        initial y coordinate for center of blob
    z : float
        initial z coordinate for center of blob
    vx : float
        initial x direction velocity in meters per second
    vy : float
        initial y direction velocity in meters per second
    vz : float
        initial z direction velocity in meters per second

    Methods
    -------
    get_prefs(data: dict) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    grid_key() -> Tuple[int]
        Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)

    draw() -> None
        Tells the instance to call draw on the BlobSurface instance

    fake_blob_z() -> None
        Called by __init__(), advance(), update_pos_vel(), adjusts radius size to to show perspective
        (closer=bigger/further=smaller), a 3d effect according the the z position

    advance(dt: float) -> None
        Applies velocity to blob, changing its x,y coordinates for next frame draw using dt (delta time)

    destroy() -> None
        Call when no longer needed, so it can clean up and disappear

    update_pos_vel(x: float, y: float, z: float, vx: float, vy: float, vz: float) -> None
        direct way to update position and velocity values

    rotate_x() -> None
        For starting position, swap y and z to get a different angle of viewing

    rotate_y() -> None
        For starting position, swap x and z to get a different angle of viewing

    rotate_z() -> None
        For starting position, swap x and y to get a different angle of viewing

    """

    __slots__ = (
        "scaled_universe_size_half_z",
        "universe_size",
        "name",
        "blob_surface",
        "radius",
        "scaled_radius",
        "orig_radius",
        "mass",
        "x",
        "y",
        "z",
        "vx",
        "vy",
        "vz",
        "dead",
        "swallowed",
        "escaped",
        "pause",
    )

    center_blob_x: ClassVar[float] = bg_vars.universe_size_w / 2
    center_blob_y: ClassVar[float] = bg_vars.universe_size_h / 2
    center_blob_z: ClassVar[float] = bg_vars.universe_size_d / 2

    def __init__(
        self: Self,
        universe_size: float,
        name: str,
        blob_surface: BlobSurface,
        mass: float,
        x: float,
        y: float,
        z: float,
        vx: float,
        vy: float,
        vz: float,
    ):

        self.scaled_universe_size_half_z: float = (universe_size * bg_vars.scale_up) / 2
        self.universe_size = universe_size

        self.name: str = name
        self.blob_surface: BlobSurface = blob_surface
        self.radius: float = blob_surface.radius
        self.scaled_radius: float = self.radius * bg_vars.scale_up
        self.orig_radius: Tuple[float, float, float] = (
            self.scaled_radius,
            self.scaled_radius / 2,
            self.radius,
        )
        self.mass: float = mass
        self.x: float = x
        self.y: float = y
        self.z: float = z

        self.vx: float = vx  # x velocity per frame
        self.vy: float = vy  # y velocity per frame
        self.vz: float = vz  # z velocity per frame
        self.dead: bool = False
        self.swallowed: bool = False
        self.escaped: bool = False
        self.pause: bool = False

        if not bg_vars.true_3d:
            self.fake_blob_z()

    def add_orbital(self: Self, orbital: "MassiveBlob") -> None:

        if bg_vars.true_3d:

            vel: Tuple[float, float, float] = None

            vel = self.blob_surface.set_orbital_pos_vel(orbital.blob_surface)

            x = orbital.blob_surface.position[0] * bg_vars.scale_up
            y = orbital.blob_surface.position[1] * bg_vars.scale_up
            z = orbital.blob_surface.position[2] * bg_vars.scale_up

            orbital.update_pos_vel(x, y, z, vel[0], vel[1], vel[2])

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["name"] = self.name
        data["radius"] = self.orig_radius[2] / bg_vars.au_scale_factor
        data["color"] = self.blob_surface.color
        if getattr(self.blob_surface, "texture"):
            data["texture"] = self.blob_surface.texture
        if getattr(self.blob_surface, "ring_texture"):
            data["ring_texture"] = self.blob_surface.ring_texture
        if getattr(self.blob_surface, "rotation_speed"):
            data["rotation_speed"] = self.blob_surface.rotation_speed
        if getattr(self.blob_surface, "rotation_pos"):
            data["rotation_pos"] = self.blob_surface.rotation_pos
        data["mass"] = self.mass
        data["x"] = self.x
        data["y"] = self.y
        data["z"] = self.z
        data["vx"] = self.vx
        data["vy"] = self.vy
        data["vz"] = self.vz

    def grid_key(self: Self) -> Tuple[int, int, int]:
        """Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)"""
        x = int((self.x * bg_vars.scale_down) / bg_vars.grid_cell_size)
        y = int((self.y * bg_vars.scale_down) / bg_vars.grid_cell_size)
        z = int((self.z * bg_vars.scale_down) / bg_vars.grid_cell_size)

        # if x <= 0:
        #     x = 1
        if x > bg_vars.grid_key_check_bound:
            x = bg_vars.grid_key_check_bound

        # if y <= 0:
        #     y = 1
        if y > bg_vars.grid_key_check_bound:
            y = bg_vars.grid_key_check_bound

        # if z <= 0:
        #     z = 1
        if z > bg_vars.grid_key_check_bound:
            z = bg_vars.grid_key_check_bound

        return (
            x,
            y,
            z,
        )

    def draw(self: Self) -> None:
        """Tells the instance to call draw on the BlobSurface instance"""
        x = self.x * bg_vars.scale_down
        y = self.y * bg_vars.scale_down
        z = self.z * bg_vars.scale_down

        if self.name != CENTER_BLOB_NAME:
            self.blob_surface.draw((x, y, z), LIGHTING)
        else:
            MassiveBlob.center_blob_x = x
            MassiveBlob.center_blob_y = y
            MassiveBlob.center_blob_z = z
            self.blob_surface.update_center_blob(x, y, z)
            self.blob_surface.draw_as_center_blob(
                (x, y, z), (LIGHTING and not self.pause)
            )

    def fake_blob_z(self: Self) -> None:
        """
        Called by __init__(), advance(), update_pos_vel(), adjusts radius size to to show perspective
        (closer=bigger/further=smaller), a 3d effect according the the z position
        """
        diff = self.scaled_universe_size_half_z - self.z

        self.scaled_radius = self.orig_radius[0] + (
            self.orig_radius[1] * (diff / self.scaled_universe_size_half_z)
        )
        self.radius = round(self.scaled_radius * bg_vars.scale_down)
        self.blob_surface.resize(self.radius)

    def advance(self: Self, dt: float) -> None:
        """Applies velocity to blob, changing its x,y coordinates for next frame draw using dt (delta time)"""

        if not bg_vars.true_3d and self.name == CENTER_BLOB_NAME:
            self.fake_blob_z()
            return

        timescale: float = bg_vars.timescale * dt

        # Advance x by velocity (one frame, with TIMESCALE elapsed time)
        self.x += self.vx * timescale

        # Advance y by velocity (one frame, with TIMESCALE elapsed time)
        self.y += self.vy * timescale

        # Advance z by velocity (one frame, with TIMESCALE elapsed time)
        self.z += self.vz * timescale

        if not bg_vars.true_3d:
            self.fake_blob_z()

    def destroy(self: Self) -> None:
        """Call when no longer needed, so it can clean up and disappear"""
        self.blob_surface.destroy()
        # self.blob_surface = None

    def update_pos_vel(
        self: Self, x: float, y: float, z: float, vx: float, vy: float, vz: float
    ) -> None:
        """direct way to update position and velocity values"""
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

        if not bg_vars.true_3d:
            self.fake_blob_z()

    def rotate_x(self: Self) -> None:
        """For starting position, swap y and z to get a different angle of viewing"""
        self.y, self.z = self.z, self.y

        self.vy, self.vz = self.vz, self.vy

    def rotate_y(self: Self) -> None:
        """For starting position, swap x and z to get a different angle of viewing"""
        self.x, self.z = self.z, self.x

        self.vx, self.vz = self.vz, self.vx

    def rotate_z(self: Self) -> None:
        """For starting position, swap x and y to get a different angle of viewing"""
        self.x, self.y = self.y, self.x

        self.vx, self.vy = self.vy, self.vx
