"""
Newton's Laws, a simulator of physics at the scale of space

Class file for the physics attributes of blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

from typing import Any, ClassVar, Dict, Tuple, Self
from .globals import *
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

    advance() -> None
        Applies velocity to blob, changing its x,y coordinates for next frame draw

    destroy() -> None
        Call when no longer needed, so it can clean up and disappear

    update_pos_vel(x: float, y: float, z: float, vx: float, vy: float, vz: float) -> None
        direct way to update position and velocity values
    """

    __slots__ = (
        "universe_size_width",
        "universe_size_height",
        "scaled_universe_width",
        "scaled_universe_height",
        "scaled_universe_size_half_z",
        "name",
        "radius",
        "scaled_radius",
        "mass",
        "x",
        "y",
        "z",
        "orig_radius",
        "vx",
        "vy",
        "vz",
        "dead",
        "swallowed",
        "escaped",
        "blob_surface",
        "pause",
    )

    center_blob_x: ClassVar[float] = UNIVERSE_SIZE_W / 2
    center_blob_y: ClassVar[float] = UNIVERSE_SIZE_H / 2
    center_blob_z: ClassVar[float] = UNIVERSE_SIZE_D / 2

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
        self.universe_size_width: float = universe_size
        self.universe_size_height: float = universe_size
        self.scaled_universe_width: float = universe_size * SCALE_UP
        self.scaled_universe_height: float = universe_size * SCALE_UP
        self.scaled_universe_size_half_z: float = self.scaled_universe_height / 2

        self.name: str = name
        self.blob_surface: BlobSurface = blob_surface
        self.radius: float = blob_surface.radius
        if TRUE_3D and self.radius > MAX_RADIUS:
            self.radius = self.radius * 0.75
        self.scaled_radius: float = self.radius * SCALE_UP
        self.mass: float = mass
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.orig_radius: Tuple[float, float, float] = (
            self.scaled_radius,
            self.scaled_radius / 2,
            self.radius,
        )
        self.vx: float = vx  # x velocity per frame
        self.vy: float = vy  # y velocity per frame
        self.vz: float = vz  # z velocity per frame
        self.dead: bool = False
        self.swallowed: bool = False
        self.escaped: bool = False
        self.pause: bool = False

        if not TRUE_3D:
            self.fake_blob_z()

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Loads the provided dict with all the necessary key/value pairs to save the state of the instance."""
        data["name"] = self.name
        data["radius"] = self.orig_radius[2]
        data["color"] = self.blob_surface.color
        if getattr(self.blob_surface, "texture"):
            data["texture"] = self.blob_surface.texture
        if getattr(self.blob_surface, "rotation_speed"):
            data["rotation_speed"] = self.blob_surface.rotation_speed
        data["mass"] = self.mass
        data["x"] = self.x
        data["y"] = self.y
        data["z"] = self.z
        data["vx"] = self.vx
        data["vy"] = self.vy
        data["vz"] = self.vz

    def grid_key(self: Self) -> Tuple[int, int, int]:
        """Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)"""
        x = int((self.x * SCALE_DOWN) / GRID_CELL_SIZE)
        y = int((self.y * SCALE_DOWN) / GRID_CELL_SIZE)
        z = int((self.z * SCALE_DOWN) / GRID_CELL_SIZE)

        if x <= 0:
            x = 1
        if x >= GRID_KEY_CHECK_BOUND:
            x = GRID_KEY_CHECK_BOUND - 1

        if y <= 0:
            y = 1
        if y >= GRID_KEY_CHECK_BOUND:
            y = GRID_KEY_CHECK_BOUND - 1

        if z <= 0:
            z = 1
        if z >= GRID_KEY_CHECK_BOUND:
            z = GRID_KEY_CHECK_BOUND - 1

        return (
            x,
            y,
            z,
        )

    def draw(self: Self) -> None:
        """Tells the instance to call draw on the BlobSurface instance"""
        x = self.x * SCALE_DOWN
        y = self.y * SCALE_DOWN
        z = self.z * SCALE_DOWN

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
        self.radius = round(self.scaled_radius * SCALE_DOWN)
        self.blob_surface.resize(self.radius)

    def advance(self: Self) -> None:
        """Applies velocity to blob, changing its x,y coordinates for next frame draw"""

        # Advance x by velocity (one frame, with TIMESCALE elapsed time)
        self.x += self.vx * TIMESCALE

        # Advance y by velocity (one frame, with TIMESCALE elapsed time)
        self.y += self.vy * TIMESCALE

        # Advance z by velocity (one frame, with TIMESCALE elapsed time)
        self.z += self.vz * TIMESCALE

        if not TRUE_3D:
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

        if not TRUE_3D:
            self.fake_blob_z()
