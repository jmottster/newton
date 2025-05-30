"""
Newton's Laws, a simulator of physics at the scale of space

Class file for the physics attributes of blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2025
"""

from decimal import *
from collections import deque
from typing import Any, ClassVar, Dict, Tuple, Self

import numpy as np
import numpy.typing as npt


from .globals import *
from .blob_global_vars import BlobGlobalVars as bg_vars
from .blob_surface import BlobSurface
from .blob_vector import BlobVector as BVec3

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
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
    index : int
        An order number in a group of blobs
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
    swallowed_by(blob: "BlobSurface") -> None
        Tells this blob what other blob is swallowing it

    add_orbital(orbital: "MassiveBlob") -> None
        Positions the provided blob around this blob (randomly) and sets the velocity accordingly

    get_prefs(data: dict) -> None
        Loads the provided dict with all the necessary key/value pairs to save the state of the instance.

    grid_key() -> Tuple[int]
        Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)

    draw() -> None
        Tells the instance to call draw on the BlobSurface instance

    advance(dt: float) -> None
        Applies velocity to blob, changing its x,y coordinates for next frame draw using dt (delta time)

    destroy() -> None
        Call when no longer needed, so it can clean up and disappear

    update_pos_vel(x: float, y: float, z: float, vx: float, vy: float, vz: float) -> None
        direct way to update position and velocity values

    """

    __slots__ = (
        "scaled_universe_size",
        "universe_size",
        "index",
        "name",
        "blob_surface",
        "_radius",
        "scaled_radius",
        "_mass",
        "position",
        "velocity",
        "_dead",
        "_swallowed",
        "escaped",
        "pause",
        "pos_log",
    )

    center_blob_x: ClassVar[float] = bg_vars.universe_size_w / 2
    center_blob_y: ClassVar[float] = bg_vars.universe_size_h / 2
    center_blob_z: ClassVar[float] = bg_vars.universe_size_d / 2

    def __init__(
        self: Self,
        universe_size: float,
        index: int,
        name: str,
        blob_surface: BlobSurface,
        mass: float,
        position: BVec3,
        velocity: BVec3,
    ):

        self.scaled_universe_size: float = universe_size * bg_vars.scale_up
        self.universe_size = universe_size

        self.index: int = index
        self.name: str = name
        self.blob_surface: BlobSurface = blob_surface
        self._radius: float = None
        self.scaled_radius: float = None
        self.radius = blob_surface.radius
        self._mass: float = None
        self.mass = mass

        self.position: BVec3 = position
        self.velocity: BVec3 = velocity

        self._dead: bool = False
        self._swallowed: bool = False
        self.escaped: bool = False
        self.pause: bool = False
        # self.pos_log: deque[npt.NDArray] = deque(
        #     [np.array([x, y, z], dtype=float), np.array([x, y, z], dtype=float)]
        # )

    @property
    def x(self: Self) -> float:
        """Returns x coordinate of 3D position"""
        return self.position.values[0]

    @x.setter
    def x(self: Self, value: float) -> None:
        """Sets x coordinate of 3D position"""
        self.position.values[0] = value

    @property
    def y(self: Self) -> float:
        """Returns y coordinate of 3D position"""
        return self.position.values[1]

    @y.setter
    def y(self: Self, value: float) -> None:
        """Sets y coordinate of 3D position"""
        self.position.values[1] = value

    @property
    def z(self: Self) -> float:
        """Returns z coordinate of 3D position"""
        return self.position.values[2]

    @z.setter
    def z(self: Self, value: float) -> None:
        """Sets z coordinate of 3D position"""
        self.position.values[2] = value

    @property
    def vx(self: Self) -> float:
        """Returns vx length of 3D velocity (meters/sec)"""
        return self.velocity.values[0]

    @vx.setter
    def vx(self: Self, value: float) -> None:
        """Sets vx length of 3D velocity (meters/sec)"""
        self.velocity.values[0] = value

    @property
    def vy(self: Self) -> float:
        """Returns vy length of 3D velocity (meters/sec)"""
        return self.velocity.values[1]

    @vy.setter
    def vy(self: Self, value: float) -> None:
        """Sets vy length of 3D velocity (meters/sec)"""
        self.velocity.values[1] = value

    @property
    def vz(self: Self) -> float:
        """Returns vz length of 3D velocity (meters/sec)"""
        return self.velocity.values[2]

    @vz.setter
    def vz(self: Self, value: float) -> None:
        """Sets vz length of 3D velocity (meters/sec)"""
        self.velocity.values[2] = value

    @property
    def radius(self: Self) -> float:
        """Returns the radius of the blob"""
        return self.blob_surface.radius

    @radius.setter
    def radius(self: Self, radius: float) -> None:
        """Sets the radius of the blob and updates self.org_radius"""
        self._radius = radius

        self.scaled_radius = self._radius * bg_vars.scale_up

        if self._radius != self.blob_surface.radius:
            self.blob_surface.radius = self._radius

    @property
    def mass(self: Self) -> float:
        """Returns the mass of the blob"""

        if self.blob_surface is not None:
            return self.blob_surface.mass
        else:
            return self._mass

    @mass.setter
    def mass(self: Self, mass: float) -> None:
        """Sets the mass of the blob"""
        self._mass = mass

        if (
            self.blob_surface is not None
            and hasattr(self.blob_surface, "mass")
            and self.blob_surface.mass != self._mass
        ):
            self.blob_surface.mass = self._mass

    @property
    def swallowed(self: Self) -> bool:
        """Returns bool indicating if this blob has been swallowed"""
        if self.blob_surface.swallowed:
            return self._swallowed
        else:
            return False

    @swallowed.setter
    def swallowed(self: Self, swallowed: bool) -> None:
        """Sets bool indicating if this blob has been swallowed"""
        self.blob_surface.swallowed = swallowed
        self._swallowed = swallowed

    def swallowed_by(self: Self, blob: "MassiveBlob") -> None:
        """Tells this blob what other blob is swallowing it"""
        self.blob_surface.swallowed_by(blob.blob_surface)

    @property
    def dead(self: Self) -> bool:
        """Returns bool indicating if this is a dead blob"""
        if self.swallowed or self.escaped:
            return self._dead
        else:
            return False

    @dead.setter
    def dead(self: Self, dead: bool) -> None:
        """Sets bool indicating if this is a dead blob"""
        self._dead = dead

    @property
    def dead_pending(self: Self) -> bool:
        """Returns the real dead state, even when swallowed or escaped are not True"""
        return self._dead

    def add_orbital(self: Self, orbital: "MassiveBlob") -> None:
        """Positions the provided blob around this blob (randomly) and sets the velocity accordingly"""

        vel: Tuple[float, float, float] = None

        vel = self.blob_surface.set_orbital_pos_vel(orbital.blob_surface)

        orbital.update_pos_vel(
            BVec3(*orbital.blob_surface.position) * bg_vars.scale_up, BVec3(*vel)
        )

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["index"] = self.index
        data["barycenter_index"] = self.blob_surface.barycenter_index
        data["name"] = self.blob_surface.name
        data["radius"] = self.radius / bg_vars.au_scale_factor
        data["color"] = self.blob_surface.color
        if getattr(self.blob_surface, "trail_color"):
            data["trail_color"] = self.blob_surface.trail_color
        if getattr(self.blob_surface, "texture"):
            data["texture"] = self.blob_surface.texture
        if getattr(self.blob_surface, "ring_texture"):
            data["ring_texture"] = self.blob_surface.ring_texture
        if getattr(self.blob_surface, "ring_scale"):
            data["ring_scale"] = self.blob_surface.ring_scale
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

    def grid_key(
        self: Self, alt_pos: Tuple[float, float, float] = None
    ) -> Tuple[int, int, int]:
        """Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)"""

        if alt_pos is None:
            alt_pos = (
                self.x * bg_vars.scale_down,
                self.y * bg_vars.scale_down,
                self.z * bg_vars.scale_down,
            )

        x = int(alt_pos[0] / bg_vars.grid_cell_size)
        y = int(alt_pos[1] / bg_vars.grid_cell_size)
        z = int(alt_pos[2] / bg_vars.grid_cell_size)

        if x > bg_vars.grid_key_check_bound:
            x = bg_vars.grid_key_check_bound

        if y > bg_vars.grid_key_check_bound:
            y = bg_vars.grid_key_check_bound

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

    def advance(self: Self, dt: Decimal) -> None:
        """Applies velocity to blob, changing its x,y coordinates for next frame draw using dt (delta time)"""

        timescale: float = float(Decimal(bg_vars.timescale) * dt)

        # Advance position by velocity (one frame, with TIMESCALE elapsed time)
        self.position += self.velocity * timescale

        # self.pos_log.append(
        #     np.array(
        #         [
        #             self.x * bg_vars.scale_down,
        #             self.y * bg_vars.scale_down,
        #             self.z * bg_vars.scale_down,
        #         ],
        #         dtype=float,
        #     )
        # )
        # self.pos_log.popleft()

    def destroy(self: Self) -> None:
        """Call when no longer needed, so it can clean up and disappear"""
        self.blob_surface.destroy()
        # self.blob_surface = None

    def update_pos_vel(self: Self, position: BVec3, velocity: BVec3) -> None:
        """direct way to update position and velocity values"""
        self.position = position
        self.velocity = velocity
