"""
Newton's Laws, a simulator of physics at the scale of space

Class file for the physics attributes of blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

import math
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
        the size of the universe in pixles (this size is cubed for full environment size)
    name : str
        a string to identify the blob
    blob_surface : BlobSurface
        the object responsible for drawing blob and maintaining visual attributes
    mass : float
        the mass of the object -- use planet scale kg values (see global min and max values)
    x : int
        initial x coordinate for center of blob
    y : int
        initial y coordinate for center of blob
    z : int
        initial z coordinate for center of blob
    vx : float
        initial x direction velocity in meters per second
    vy : float
        initial y direction velocity in meters per second
    vz : float
        initial z direction velocity in meters per second

    Methods
    -------

    grid_key()
        Returns an x,y,z tuple indicating this blob's position in the proximity grid (not the display screen)
    draw()
        Tells the instance to call draw on the BlobSurface instance
    advance()
        Applies velocity to blob, changing its x,y coordinates for next frame draw
        fake_blob_z()
            Called by advance(), adjusts radius size to fake a near/close 3d effect according the the z position
    update_pos_vel(x, y, z, vx, vy, vz)
        direct way to update position and velocity values
    edge_detection(wrap)
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)

    collision_detection(blob)
        Checks to see if this blob is coliding with provided blob, and adjusts velocity of each
        according to Newton's Laws

    gravitational_pull(blob, g)
        Changes velocity of self and provided blob in relation to gravitational pull with each other.
        g is the Gravitational Constant to be applied to equation
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
        "blob_suface",
        "pause",
    )

    center_blob_x = UNIVERSE_SIZE_W / 2
    center_blob_y = UNIVERSE_SIZE_H / 2
    center_blob_z = UNIVERSE_SIZE_D / 2
    GRAVITATIONAL_RANGE = 0

    def __init__(self, universe_size, name, blob_suface, mass, x, y, z, vx, vy, vz):
        self.universe_size_width = universe_size
        self.universe_size_height = universe_size
        self.scaled_universe_width = universe_size * SCALE_UP
        self.scaled_universe_height = universe_size * SCALE_UP
        self.scaled_universe_size_half_z = self.scaled_universe_height / 2
        if MassiveBlob.GRAVITATIONAL_RANGE == 0:
            MassiveBlob.GRAVITATIONAL_RANGE = (self.scaled_universe_height / 8) * 6

        self.name = name
        self.blob_suface = blob_suface
        self.radius = blob_suface.radius
        self.scaled_radius = self.radius * SCALE_UP
        self.mass = mass
        self.x = x
        self.y = y
        self.z = z
        self.orig_radius = (
            self.scaled_radius,
            self.scaled_radius / 2,
        )
        self.vx = vx  # x velocity per frame
        self.vy = vy  # y velocity per frame
        self.vz = vz  # z velocity per frame
        self.dead = False
        self.swallowed = False
        self.escaped = False
        self.pause = False

        self.fake_blob_z()

    def grid_key(self):
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

    def draw(self):
        """Tells the instance to call draw on the BlobSurface instance"""
        x = self.x * SCALE_DOWN
        y = self.y * SCALE_DOWN
        z = self.z * SCALE_DOWN

        if self.name != CENTER_BLOB_NAME:
            self.blob_suface.draw((x, y, z), LIGHTING)  # TODO fix
        else:
            MassiveBlob.center_blob_x = x
            MassiveBlob.center_blob_y = y
            MassiveBlob.center_blob_z = z
            self.blob_suface.update_center_blob(x, y, z)
            self.blob_suface.draw_as_center_blob(
                (x, y, z), (LIGHTING and not self.pause)
            )

    def fake_blob_z(self):
        """Called by advance(), adjusts radius size to to show perspective
        (closer=bigger/further=smaller), a 3d effect according the the z position"""
        diff = self.scaled_universe_size_half_z - self.z

        self.scaled_radius = self.orig_radius[0] + (
            self.orig_radius[1] * (diff / self.scaled_universe_size_half_z)
        )
        self.radius = round(self.scaled_radius * SCALE_DOWN)
        self.blob_suface.resize(self.radius)

    def advance(self):
        """Applies velocity to blob, changing its x,y coordinates for next frame draw"""

        # Advace x by velocity (one frame, with TIMESTEP elapsed time)
        self.x += self.vx * TIMESCALE

        # Advace y by velocity (one frame, with TIMESTEP elapsed time)
        self.y += self.vy * TIMESCALE

        # Advace z by velocity (one frame, with TIMESTEP elapsed time)
        self.z += self.vz * TIMESCALE

        self.fake_blob_z()

    def update_pos_vel(self, x, y, z, vx, vy, vz):
        """direct way to update position and velocity values"""
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

        self.fake_blob_z()

    def edge_detection(self, wrap):
        """Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)"""
        if wrap:
            # TODO fix wraping for scale
            # Move real x to other side of screen if it's gone off the edge
            if self.vx < 0 and self.x < 0:
                self.x = self.scaled_universe_width
            elif self.vx > 0 and self.x > self.scaled_universe_width:
                self.x = 0

            # Move real y to other side of screen if it's gone off the edge
            if self.vy < 0 and self.y < 0:
                self.y = self.scaled_universe_height
            elif self.vy > 0 and self.y > self.scaled_universe_height:
                self.y = 0

        else:
            zero = 0
            universe_size_w = self.universe_size_width
            universe_size_h = self.universe_size_height
            scaled_universe_size_w = self.scaled_universe_width
            scaled_universe_size_h = self.scaled_universe_height

            local_x = self.x * SCALE_DOWN
            local_y = self.y * SCALE_DOWN
            local_z = self.z * SCALE_DOWN

            # Change x direction if hitting the edge of screen
            if ((local_x - self.radius) <= zero) and (self.vx <= 0):
                self.vx = -self.vx
                self.x = self.scaled_radius
                self.vx = self.vx * 0.995

            if ((local_x + self.radius) >= universe_size_w) and (self.vx >= 0):
                self.vx = -self.vx
                self.x = scaled_universe_size_w - self.scaled_radius
                self.vx = self.vx * 0.995

            # Change y direction if hitting the edge of screen
            if ((local_y - self.radius) <= zero) and (self.vy <= 0):
                self.vy = -self.vy
                self.y = self.scaled_radius
                self.vy = self.vy * 0.995

            if ((local_y + self.radius) >= universe_size_h) and self.vy >= 0:
                self.vy = -self.vy
                self.y = scaled_universe_size_h - self.scaled_radius
                self.vy = self.vy * 0.995

            # Change z direction if hitting the edge of screen
            if ((local_z - self.radius) <= zero) and (self.vz <= 0):
                self.vz = -self.vz
                self.z = self.scaled_radius
                self.vz = self.vz * 0.995

            if ((local_z + self.radius) >= universe_size_h) and self.vz >= 0:
                self.vz = -self.vz
                self.z = scaled_universe_size_h - self.scaled_radius
                self.vz = self.vz * 0.995

    def collision_detection(self, blob):
        """Checks to see if this blob is coliding with provided blob, and adjusts velocity of each
        according to Newton's Laws"""
        dd = self.orig_radius[0] + blob.orig_radius[0]
        if abs(blob.x - self.x) > dd:
            return

        dx = blob.x - self.x
        dy = blob.y - self.y
        dz = blob.z - self.z
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))
        dd = self.orig_radius[0] + blob.orig_radius[0]

        # Check if the two blobs are touching
        if d <= dd:
            # x reaction
            ux1, ux2 = self.vx, blob.vx

            self.vx = ux1 * (self.mass - blob.mass) / (
                self.mass + blob.mass
            ) + 2 * ux2 * blob.mass / (self.mass + blob.mass)

            blob.vx = 2 * ux1 * self.mass / (self.mass + blob.mass) + ux2 * (
                blob.mass - self.mass
            ) / (self.mass + blob.mass)

            # y reaction
            uy1, uy2 = self.vy, blob.vy

            self.vy = uy1 * (self.mass - blob.mass) / (
                self.mass + blob.mass
            ) + 2 * uy2 * blob.mass / (self.mass + blob.mass)

            blob.vy = 2 * uy1 * self.mass / (self.mass + blob.mass) + uy2 * (
                blob.mass - self.mass
            ) / (self.mass + blob.mass)

            # z reaction
            uz1, uz2 = self.vz, blob.vz

            self.vz = uz1 * (self.mass - blob.mass) / (
                self.mass + blob.mass
            ) + 2 * uz2 * blob.mass / (self.mass + blob.mass)

            blob.vz = 2 * uz1 * self.mass / (self.mass + blob.mass) + uz2 * (
                blob.mass - self.mass
            ) / (self.mass + blob.mass)

            # some fake energy loss due to collision
            self.vx = self.vx * 0.995
            blob.vx = blob.vx * 0.995
            self.vy = self.vy * 0.995
            blob.vy = blob.vy * 0.995
            self.vz = self.vz * 0.995
            blob.vz = blob.vz * 0.995

            # To prevent (or reduce) cling-ons, we have the center blob swallow blobs
            # that cross the collision boundry too far
            if self.name == CENTER_BLOB_NAME or blob.name == CENTER_BLOB_NAME:
                smaller_blob = self
                larger_blob = blob
                if self.name == CENTER_BLOB_NAME:
                    smaller_blob = blob
                    larger_blob = self
                if abs(dd - d) >= (smaller_blob.orig_radius[0] * 0.6):
                    larger_blob.mass += smaller_blob.mass
                    smaller_blob.dead = True
                    smaller_blob.swallowed = True

    def gravitational_pull(self, blob, g):
        """Changes velocity of self and provided blob in relation to gravitational pull with each other.
        g is the Gravitational Constant to be applied to equation"""

        dx = blob.x - self.x
        dy = blob.y - self.y
        dz = blob.z - self.z
        dd = (self.orig_radius[0] * 0.90) + blob.orig_radius[0]
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))

        if d < MassiveBlob.GRAVITATIONAL_RANGE and d > 0:
            F = g * self.mass * blob.mass / d**2

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            fdx = F * math.sin(theta) * math.cos(phi)
            fdy = F * math.sin(theta) * math.sin(phi)
            fdz = F * math.cos(theta)

            self.vx += fdx / self.mass * TIMESCALE
            self.vy += fdy / self.mass * TIMESCALE
            self.vz += fdz / self.mass * TIMESCALE

            blob.vx -= fdx / blob.mass * TIMESCALE
            blob.vy -= fdy / blob.mass * TIMESCALE
            blob.vz -= fdz / blob.mass * TIMESCALE

        elif d > MassiveBlob.GRAVITATIONAL_RANGE and self.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob.dead = True
            blob.escaped = True
