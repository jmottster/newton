"""
Newton's Laws, a simulator of physics at the scale of space

A static class used to provide physics methods for MassiveBlobs

by Jason Mott, copyright 2024
"""

import math

from .massive_blob import MassiveBlob
from .globals import *
from .blob_global_vars import BlobGlobalVars

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPhysics:
    """
    A static class used to provide physics methods for MassiveBlobs

    Attributes
    ----------

    Methods
    -------
    set_gravitational_range(scaled_universe_height: float) -> None
        Sets the gravitational range of the center blob. Blobs that go beyond this limit
        are flagged as "escaped" and are deleted
    edge_detection(blob: MassiveBlob, wrap: bool) -> None
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)

    collision_detection(blob1: MassiveBlob, blob2: MassiveBlob) -> None
        Checks to see if blob1 is colliding with blob2, and adjusts velocity of each
        according to Newton's Laws

    gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob) -> None
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
    """

    g: float = G
    GRAVITATIONAL_RANGE: float = 0

    @classmethod
    def set_gravitational_range(cls, scaled_universe_height: float) -> None:
        """
        Sets the gravitational range of the center blob. Blobs that go beyond this limit
        are flagged as "escaped" and are deleted
        """
        cls.GRAVITATIONAL_RANGE = scaled_universe_height

    @staticmethod
    def edge_detection(blob: MassiveBlob, wrap: bool) -> None:
        """
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)
        """
        if wrap:
            # TODO fix wrapping for scale
            # Move real x to other side of screen if it's gone off the edge
            universe_size = blob.universe_size * BlobGlobalVars.scale_up
            if blob.vx < 0 and blob.x < 0:
                blob.x = universe_size
            elif blob.vx > 0 and blob.x > universe_size:
                blob.x = 0

            # Move real y to other side of screen if it's gone off the edge
            if blob.vy < 0 and blob.y < 0:
                blob.y = universe_size
            elif blob.vy > 0 and blob.y > universe_size:
                blob.y = 0

        else:
            zero = 0
            universe_size_w = blob.universe_size
            universe_size_h = blob.universe_size
            scaled_universe_size_w = blob.universe_size
            scaled_universe_size_h = blob.universe_size

            local_x = blob.x * BlobGlobalVars.scale_down
            local_y = blob.y * BlobGlobalVars.scale_down
            local_z = blob.z * BlobGlobalVars.scale_down

            # Change x direction if hitting the edge of screen
            if ((local_x - blob.radius) <= zero) and (blob.vx <= 0):
                blob.vx = -blob.vx
                blob.x = blob.scaled_radius
                blob.vx = blob.vx * 0.995

            if ((local_x + blob.radius) >= universe_size_w) and (blob.vx >= 0):
                blob.vx = -blob.vx
                blob.x = scaled_universe_size_w - blob.scaled_radius
                blob.vx = blob.vx * 0.995

            # Change y direction if hitting the edge of screen
            if ((local_y - blob.radius) <= zero) and (blob.vy <= 0):
                blob.vy = -blob.vy
                blob.y = blob.scaled_radius
                blob.vy = blob.vy * 0.995

            if ((local_y + blob.radius) >= universe_size_h) and blob.vy >= 0:
                blob.vy = -blob.vy
                blob.y = scaled_universe_size_h - blob.scaled_radius
                blob.vy = blob.vy * 0.995

            # Change z direction if hitting the edge of screen
            if ((local_z - blob.radius) <= zero) and (blob.vz <= 0):
                blob.vz = -blob.vz
                blob.z = blob.scaled_radius
                blob.vz = blob.vz * 0.995

            if ((local_z + blob.radius) >= universe_size_h) and blob.vz >= 0:
                blob.vz = -blob.vz
                blob.z = scaled_universe_size_h - blob.scaled_radius
                blob.vz = blob.vz * 0.995

    @staticmethod
    def collision_detection(blob1: MassiveBlob, blob2: MassiveBlob) -> None:
        """
        Checks to see if blob1 is colliding with blob2, and adjusts velocity of each
        according to Newton's Laws
        """
        dd = blob1.orig_radius[0] + blob2.orig_radius[0]
        if abs(blob2.x - blob1.x) > dd:
            return

        dx = blob2.x - blob1.x
        dy = blob2.y - blob1.y
        dz = blob2.z - blob1.z
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))

        # Check if the two blobs are touching
        if d <= dd:
            # x reaction
            ux1, ux2 = blob1.vx, blob2.vx

            blob1.vx = ux1 * (blob1.mass - blob2.mass) / (
                blob1.mass + blob2.mass
            ) + 2 * ux2 * blob2.mass / (blob1.mass + blob2.mass)

            blob2.vx = 2 * ux1 * blob1.mass / (blob1.mass + blob2.mass) + ux2 * (
                blob2.mass - blob1.mass
            ) / (blob1.mass + blob2.mass)

            # y reaction
            uy1, uy2 = blob1.vy, blob2.vy

            blob1.vy = uy1 * (blob1.mass - blob2.mass) / (
                blob1.mass + blob2.mass
            ) + 2 * uy2 * blob2.mass / (blob1.mass + blob2.mass)

            blob2.vy = 2 * uy1 * blob1.mass / (blob1.mass + blob2.mass) + uy2 * (
                blob2.mass - blob1.mass
            ) / (blob1.mass + blob2.mass)

            # z reaction
            uz1, uz2 = blob1.vz, blob2.vz

            blob1.vz = uz1 * (blob1.mass - blob2.mass) / (
                blob1.mass + blob2.mass
            ) + 2 * uz2 * blob2.mass / (blob1.mass + blob2.mass)

            blob2.vz = 2 * uz1 * blob1.mass / (blob1.mass + blob2.mass) + uz2 * (
                blob2.mass - blob1.mass
            ) / (blob1.mass + blob2.mass)

            # some fake energy loss due to collision
            blob1.vx = blob1.vx * 0.995
            blob2.vx = blob2.vx * 0.995
            blob1.vy = blob1.vy * 0.995
            blob2.vy = blob2.vy * 0.995
            blob1.vz = blob1.vz * 0.995
            blob2.vz = blob2.vz * 0.995

            # To prevent (or reduce) cling-ons, we have the center blob swallow blobs
            # that cross the collision boundary too far
            if blob1.name == CENTER_BLOB_NAME or blob2.name == CENTER_BLOB_NAME:
                smaller_blob = blob1
                larger_blob = blob2
                if blob1.name == CENTER_BLOB_NAME:
                    smaller_blob = blob2
                    larger_blob = blob1
                if d <= dd:
                    larger_blob.mass += smaller_blob.mass
                    smaller_blob.dead = True
                    smaller_blob.swallowed = True

    @staticmethod
    def gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob) -> None:
        """
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
        """

        dx = blob2.x - blob1.x
        dy = blob2.y - blob1.y
        dz = blob2.z - blob1.z
        # dd = (blob1.orig_radius[0] * 0.90) + blob2.orig_radius[0]
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))

        if d < BlobPhysics.GRAVITATIONAL_RANGE:
            F = BlobPhysics.g * blob1.mass * blob2.mass / d**2

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            fdx = F * math.sin(theta) * math.cos(phi)
            fdy = F * math.sin(theta) * math.sin(phi)
            fdz = F * math.cos(theta)

            blob1.vx += fdx / blob1.mass * BlobGlobalVars.timescale
            blob1.vy += fdy / blob1.mass * BlobGlobalVars.timescale
            blob1.vz += fdz / blob1.mass * BlobGlobalVars.timescale

            blob2.vx -= fdx / blob2.mass * BlobGlobalVars.timescale
            blob2.vy -= fdy / blob2.mass * BlobGlobalVars.timescale
            blob2.vz -= fdz / blob2.mass * BlobGlobalVars.timescale

        elif blob1.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob2.dead = True
            blob2.escaped = True
