"""
Newton's Laws, a simulator of physics at the scale of space

A static class used to provide physics methods for MassiveBlobs

by Jason Mott, copyright 2024
"""

import math
from typing import Self

from .massive_blob import MassiveBlob
from .globals import *
from .blob_global_vars import BlobGlobalVars as bg_vars

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class point:
    def __init__(self: Self, x: float, y: float, z: float):
        self.x: float = x
        self.y: float = y
        self.z: float = z


class distance:
    def __init__(self: Self, point1: point, point2: point) -> None:

        self.dx: float = point1.x - point2.x
        self.dy: float = point1.y - point2.y
        self.dz: float = point1.z - point2.z
        self.d: float = math.sqrt((self.dx**2 + self.dy**2 + self.dz**2))


class position_marker:
    def __init__(self: Self, pos: point, vel: point, time_step: float = 1) -> None:

        self.pos = pos
        self.vel = vel
        self.time_step = time_step

    def move(self: Self) -> None:

        self.pos.x += self.vel.x * self.time_step
        self.pos.y += self.vel.y * self.time_step
        self.pos.z += self.vel.z * self.time_step


class BlobPhysics:
    """
    A static class used to provide physics methods for MassiveBlobs

    Attributes
    ----------
    g : float = G - The gravitational constant, set by the global constant G
    GRAVITATIONAL_RANGE : float = 0 - The distance from the center blob at which we get rid of a blob
                                      set this via the set_gravitational_range() method

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

    partial_step(pos: point, vel: point, time_step: float = 1) -> point
        Will add vel to pos, time_step times and return the new point

    gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob) -> None
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
        uses the Euler method with trig

    euler_gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob, dt: float) -> None
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
        uses the Euler method without trig

    jjm_gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob, dt: float, num_steps: int = 5) -> None
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other.
        Uses the Jason Mott method, which runs several steps (num_steps) to get to the final timescale step,
        thus making it more accurate than a straight line to the final step would be.
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
    def edge_detection(blob: MassiveBlob) -> None:
        """
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)
        """
        velocity_loss = 0.75

        if bg_vars.wrap_if_no_escape:
            # Move real x to other side of screen if it's gone off the edge
            universe_size = blob.universe_size * bg_vars.scale_up
            if blob.vx < 0 and blob.x < 0:
                blob.x += universe_size
                blob.vx = blob.vx * velocity_loss
                blob.vy = -blob.vy
                blob.vz = -blob.vz
            elif blob.vx > 0 and blob.x > universe_size:
                blob.x -= universe_size
                blob.vx = blob.vx * velocity_loss
                blob.vy = -blob.vy
                blob.vz = -blob.vz

            # Move real y to other side of screen if it's gone off the edge
            if blob.vy < 0 and blob.y < 0:
                blob.y += universe_size
                blob.vy = blob.vy * velocity_loss
                blob.vx = -blob.vx
                blob.vz = -blob.vz
            elif blob.vy > 0 and blob.y > universe_size:
                blob.y -= universe_size
                blob.vy = blob.vy * velocity_loss
                blob.vx = -blob.vx
                blob.vz = -blob.vz

            # Move real z to other side of screen if it's gone off the edge
            if blob.vz < 0 and blob.z < 0:
                blob.z += universe_size
                blob.vz = blob.vz * velocity_loss
                blob.vx = -blob.vx
                blob.vy = -blob.vy
            elif blob.vz > 0 and blob.z > universe_size:
                blob.z -= universe_size
                blob.vz = blob.vz * velocity_loss
                blob.vx = -blob.vx
                blob.vy = -blob.vy

        else:
            zero = 0
            universe_size_w = blob.universe_size
            universe_size_h = blob.universe_size
            scaled_universe_size_w = blob.universe_size * bg_vars.scale_up
            scaled_universe_size_h = blob.universe_size * bg_vars.scale_up

            local_x = blob.x * bg_vars.scale_down
            local_y = blob.y * bg_vars.scale_down
            local_z = blob.z * bg_vars.scale_down

            # Change x direction if hitting the edge of screen
            if ((local_x - blob.radius) <= zero) and (blob.vx <= 0):
                blob.vx = -blob.vx
                blob.x = blob.scaled_radius
                blob.vx = blob.vx * velocity_loss

            if ((local_x + blob.radius) >= universe_size_w) and (blob.vx >= 0):
                blob.vx = -blob.vx
                blob.x = scaled_universe_size_w - blob.scaled_radius
                blob.vx = blob.vx * velocity_loss

            # Change y direction if hitting the edge of screen
            if ((local_y - blob.radius) <= zero) and (blob.vy <= 0):
                blob.vy = -blob.vy
                blob.y = blob.scaled_radius
                blob.vy = blob.vy * velocity_loss

            if ((local_y + blob.radius) >= universe_size_h) and blob.vy >= 0:
                blob.vy = -blob.vy
                blob.y = scaled_universe_size_h - blob.scaled_radius
                blob.vy = blob.vy * velocity_loss

            # Change z direction if hitting the edge of screen
            if ((local_z - blob.radius) <= zero) and (blob.vz <= 0):
                blob.vz = -blob.vz
                blob.z = blob.scaled_radius
                blob.vz = blob.vz * velocity_loss

            if ((local_z + blob.radius) >= universe_size_h) and blob.vz >= 0:
                blob.vz = -blob.vz
                blob.z = scaled_universe_size_h - blob.scaled_radius
                blob.vz = blob.vz * velocity_loss

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
    def partial_step(pos: point, vel: point, time_step: float = 1) -> point:
        """Will add vel to pos, time_step times and return the new point"""
        return point(
            pos.x + vel.x * time_step,
            pos.y + vel.y * time_step,
            pos.z + vel.z * time_step,
        )

    @staticmethod
    def gravitational_pull(blob1: MassiveBlob, blob2: MassiveBlob, dt: float) -> None:
        """
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
        """
        timescale: float = bg_vars.timescale * dt
        dx = blob1.x - blob2.x
        dy = blob1.y - blob2.y
        dz = blob1.z - blob2.z
        # dd = (blob1.orig_radius[0] * 0.90) + blob2.orig_radius[0]
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))

        if d < BlobPhysics.GRAVITATIONAL_RANGE:
            F = BlobPhysics.g * blob1.mass * blob2.mass / d**2

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            fdx = F * math.sin(theta) * math.cos(phi)
            fdy = F * math.sin(theta) * math.sin(phi)
            fdz = F * math.cos(theta)

            blob1.vx -= fdx / blob1.mass * timescale
            blob1.vy -= fdy / blob1.mass * timescale
            blob1.vz -= fdz / blob1.mass * timescale

            blob2.vx += fdx / blob2.mass * timescale
            blob2.vy += fdy / blob2.mass * timescale
            blob2.vz += fdz / blob2.mass * timescale

        elif bg_vars.center_blob_escape and blob1.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob2.dead = True
            blob2.escaped = True

    @staticmethod
    def euler_gravitational_pull(
        blob1: MassiveBlob, blob2: MassiveBlob, dt: float
    ) -> None:
        """
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other
        uses the Euler method
        """
        blob1_location: point = point(blob1.x, blob1.y, blob1.z)
        blob2_location: point = point(blob2.x, blob2.y, blob2.z)

        d: distance = distance(blob1_location, blob2_location)

        if d.d < BlobPhysics.GRAVITATIONAL_RANGE:

            timescale: float = bg_vars.timescale * dt

            F = BlobPhysics.g * blob1.mass * blob2.mass / d.d**3

            F1 = F / blob1.mass
            F2 = F / blob2.mass

            blob1.vx -= d.dx * F1 * timescale
            blob1.vy -= d.dy * F1 * timescale
            blob1.vz -= d.dz * F1 * timescale

            blob2.vx += d.dx * F2 * timescale
            blob2.vy += d.dy * F2 * timescale
            blob2.vz += d.dz * F2 * timescale

        elif bg_vars.center_blob_escape and blob1.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob2.dead = True
            blob2.escaped = True

    @staticmethod
    def jjm_gravitational_pull(
        blob1: MassiveBlob, blob2: MassiveBlob, dt: float, num_steps: int = 5
    ) -> None:
        """
        Changes velocity of blob1 and blob2 in relation to gravitational pull with each other.
        Uses the Jason Mott method, which runs several steps (num_steps) to get to the final timescale step,
        thus making it more accurate than a straight line to the final step would be.
        """
        blob1_location: position_marker = position_marker(
            point(blob1.x, blob1.y, blob1.z), point(0, 0, 0)
        )
        blob2_location: position_marker = position_marker(
            point(blob2.x, blob2.y, blob2.z), point(0, 0, 0)
        )
        d: distance = distance(blob1_location.pos, blob2_location.pos)

        if d.d < BlobPhysics.GRAVITATIONAL_RANGE:

            last_step: int = num_steps - 1
            timescale: float = bg_vars.timescale * dt / num_steps

            blob1_location.time_step = timescale
            blob2_location.time_step = timescale

            F: float = 0.0
            F1: float = 0.0
            F2: float = 0.0

            GM: float = BlobPhysics.g * blob1.mass * blob2.mass

            for i in range(0, num_steps):

                F = GM / d.d**3

                F1 = F / blob1.mass
                F2 = F / blob2.mass

                blob1_location.vel.x -= d.dx * F1 * timescale
                blob1_location.vel.y -= d.dy * F1 * timescale
                blob1_location.vel.z -= d.dz * F1 * timescale

                blob2_location.vel.x += d.dx * F2 * timescale
                blob2_location.vel.y += d.dy * F2 * timescale
                blob2_location.vel.z += d.dz * F2 * timescale

                if i < last_step:

                    blob1_location.move()
                    blob2_location.move()

                    d = distance(blob1_location.pos, blob2_location.pos)

            blob1.vx += blob1_location.vel.x
            blob1.vy += blob1_location.vel.y
            blob1.vz += blob1_location.vel.z

            blob2.vx += blob2_location.vel.x
            blob2.vy += blob2_location.vel.y
            blob2.vz += blob2_location.vel.z

        elif bg_vars.center_blob_escape and blob1.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob2.dead = True
            blob2.escaped = True
