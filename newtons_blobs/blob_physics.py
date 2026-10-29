"""
Newton's Laws, a simulator of physics at the scale of space

A static class used to provide physics methods for MassiveBlobs

by Jason Mott, copyright 2025
"""

import math
from decimal import *
from typing import Tuple


from .massive_blob import MassiveBlob
from .blob_vector import BlobVector as BVec3
from .globals import *
from .blob_global_vars import BlobGlobalVars as bg_vars

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
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
    g : float = G - The gravitational constant, set by the global constant G

    GRAVITATIONAL_RANGE : float = 0 - The distance from the center blob at which we get rid of a blob
                                      set this via the set_gravitational_range() method

    COR : float = 0.5 - Coefficient of restitution used to make blob collisions inelastic

    hits: dict = dict() - holds number of times two blobs have collided

    a_dt: float = 1 / FRAME_RATE - Average delta time, used in cases where time increment is needed in
                                   calculation. Always multiplied by the dynamic bg_vars.timescale variable
                                   before use.

    dt_timescale: float = a_dt * bg_vars.timescale - Adjusted a_dt for running timescale. Use BlobPhysics.set_timescale
                                                     to update when bg_vars.timescale changes

    Methods
    -------
    set_gravitational_range(scaled_universe_height: float) -> None
        Sets the gravitational range of the center blob. Blobs that go beyond this limit
        are flagged as "escaped" and are deleted

    set_average_delta_time(a_dt: float) -> None
        Sets the average delta time, to be used in any subsequent function call that needs it

    set_timescale(timescale: float) -> None
        Updates dt_timescale with timescale. To be called when bg_vars.timescale changes

    edge_detection(blob: MassiveBlob, wrap: bool) -> None
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)

    new_radius(r1: float, r2: float) -> float
        Calculates and returns a new radius based on the combined volumes of
        two spheres with the provided radii (i.e., when two blobs combine,
        this is their new radius)

    is_distance_cleared(blob1: MassiveBlob, blob2: MassiveBlob, distance: float) -> bool
        Returns False if blob1 and blob2 are distance apart
        or closer, True if further than distance

    collision_detection(blob1: MassiveBlob, blob2: MassiveBlob) -> BVec3, float
        Checks to see if blob1 is about to  or is colliding with blob2, and adjusts velocity and possibly position of each
        according to Newton's Laws. it returns the adjusted relative position of blob1 to blob2, and the distance between them

    gravity_collision(blob1: MassiveBlob, blob2: MassiveBlob) -> None
        Changes acceleration of blob1 and blob2 in relation to gravitational pull with each other
        this will also first call collision_detection() with the provided blobs

    """

    g: float = G
    GRAVITATIONAL_RANGE: float = 0

    # coefficient of restitution
    COR: float = 0.65

    hits: dict = dict()

    a_dt: float = 1 / float(FRAME_RATE)

    dt_timescale: float = a_dt * bg_vars.timescale

    half_uni_size: float = bg_vars.universe_size / 2

    uni_center: BVec3 = BVec3(
        half_uni_size,
        half_uni_size,
        half_uni_size,
    )

    edge_radius: float = float(round(uni_center.mag())) * bg_vars.scale_up

    uni_center *= bg_vars.scale_up

    edge_cor: float = 0.9

    collision_range: float = bg_vars.max_radius * 2 * bg_vars.scale_up

    @classmethod
    def setup(cls) -> None:
        """
        Call when bg_vars may have been updated, this will refresh variables that
        depend on bg_vars
        """
        cls.dt_timescale = cls.a_dt * bg_vars.timescale

        cls.half_uni_size = bg_vars.universe_size / 2

        cls.uni_center = BVec3(
            cls.half_uni_size,
            cls.half_uni_size,
            cls.half_uni_size,
        )

        cls.edge_radius = float(round(cls.uni_center.mag())) * bg_vars.scale_up
        cls.uni_center *= bg_vars.scale_up

        cls.collision_range = bg_vars.max_radius * 2 * bg_vars.scale_up

    @classmethod
    def set_gravitational_range(cls, scaled_universe_height: float) -> None:
        """
        Sets the gravitational range of the center blob. Blobs that go beyond this limit
        are flagged as "escaped" and are deleted
        """
        cls.GRAVITATIONAL_RANGE = scaled_universe_height

    @classmethod
    def set_average_delta_time(cls, a_dt: float) -> None:
        """Sets the average delta time, to be used in any subsequent function call that needs it"""
        cls.a_dt = a_dt

    @classmethod
    def set_timescale(cls, timescale: float) -> None:
        """Updates dt_timescale with timescale. To be called when bg_vars.timescale changes"""
        cls.dt_timescale = cls.a_dt * timescale

    @staticmethod
    def edge_detection(blob: MassiveBlob) -> None:
        """
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)
        """

        if bg_vars.wrap_if_no_escape:

            velocity_loss = 0.75
            scaled_up_universe_size: float = BlobPhysics.half_uni_size * 2

            # Move real x to other side of screen if it's gone off the edge
            if blob.vx < 0 and blob.x < 0:
                blob.x += scaled_up_universe_size
                blob.vx = blob.vx * velocity_loss
                blob.vy = -blob.vy
                blob.vz = -blob.vz
            elif blob.vx > 0 and blob.x > scaled_up_universe_size:
                blob.x -= scaled_up_universe_size
                blob.vx = blob.vx * velocity_loss
                blob.vy = -blob.vy
                blob.vz = -blob.vz

            # Move real y to other side of screen if it's gone off the edge
            if blob.vy < 0 and blob.y < 0:
                blob.y += scaled_up_universe_size
                blob.vy = blob.vy * velocity_loss
                blob.vx = -blob.vx
                blob.vz = -blob.vz
            elif blob.vy > 0 and blob.y > scaled_up_universe_size:
                blob.y -= scaled_up_universe_size
                blob.vy = blob.vy * velocity_loss
                blob.vx = -blob.vx
                blob.vz = -blob.vz

            # Move real z to other side of screen if it's gone off the edge
            if blob.vz < 0 and blob.z < 0:
                blob.z += scaled_up_universe_size
                blob.vz = blob.vz * velocity_loss
                blob.vx = -blob.vx
                blob.vy = -blob.vy
            elif blob.vz > 0 and blob.z > scaled_up_universe_size:
                blob.z -= scaled_up_universe_size
                blob.vz = blob.vz * velocity_loss
                blob.vx = -blob.vx
                blob.vy = -blob.vy

        else:

            rel_pos: BVec3 = blob.position.relative_to(BlobPhysics.uni_center)
            dd: float = BlobPhysics.edge_radius - blob.scaled_radius  # * 0.9941
            d: float = rel_pos.mag()

            if d < dd - BlobPhysics.collision_range:
                return

            p_v_dot: float = rel_pos.dot(blob.velocity)

            if p_v_dot <= 0:
                # Moving toward universe center, no need to adjust velocities
                return

            if d < dd:

                vel_dot: float = blob.velocity.dot(blob.velocity)

                disc: float = p_v_dot**2 + vel_dot * (dd**2 - rel_pos.dot(rel_pos))

                if disc < 0:
                    return

                t: float = (-p_v_dot + math.sqrt(disc)) / vel_dot

                if t > 0 and t < BlobPhysics.dt_timescale:

                    blob.position += blob.velocity * t
                    blob.pre_elapsed_time += t
                    d = blob.position.distance(BlobPhysics.uni_center)

            if d >= dd:

                pos_norm: BVec3 = blob.position.relative_to(
                    BlobPhysics.uni_center
                ).normalize()
                vel_norm: float = blob.velocity.dot(pos_norm)

                blob.velocity -= pos_norm * (vel_norm * (1 + BlobPhysics.edge_cor))

    @staticmethod
    def new_radius(r1: float, r2: float) -> float:
        """
        Calculates and returns a new radius based on the combined volumes of
        two spheres with the provided radii (i.e., when two blobs combine,
        this is their new radius)
        """
        v1 = math.pi * r1**3 * 4 / 3
        v2 = math.pi * r2**3 * 4 / 3
        return math.cbrt((v1 + v2) * 3 / (4 * math.pi))

    @staticmethod
    def is_distance_cleared(
        blob1: MassiveBlob, blob2: MassiveBlob, distance: float
    ) -> bool:
        """
        Returns False if blob1 and blob2 are distance apart
        or closer, True if further than distance
        """

        blob_distance: float = blob1.position.distance(blob2.position)

        dd: float = blob1.scaled_radius + blob2.scaled_radius + distance
        if blob_distance <= dd:
            return False

        return True

    @staticmethod
    def collision_detection(
        blob1: MassiveBlob, blob2: MassiveBlob
    ) -> Tuple[BVec3, float]:
        """
        Checks to see if blob1 is about to or is colliding with blob2, and adjusts velocity and possibly position of each
        according to Newton's Laws. it returns the adjusted relative position of blob1 to blob2, and the distance between them
        """
        rel_pos: BVec3 = blob1.position.relative_to(blob2.position)
        d: float = rel_pos.mag()

        if d > BlobPhysics.collision_range:
            return rel_pos, d

        rel_vel: BVec3 = blob1.velocity.relative_to(blob2.velocity)
        p_v_dot: float = rel_pos.dot(rel_vel)

        if p_v_dot > 0:
            # blob1 is moving away from blob2, no need
            # to adjust velocities or handle a collision
            return rel_pos, d

        dd: float = blob1.scaled_radius + blob2.scaled_radius

        # if blobs are not yet touching, let's see if the
        # time left before they touch is small enough to nudge
        # it into place for the d <= dd block, i.e. prevent an
        # overlap on the next time loop
        if d > dd:

            pad_dd: float = dd * 0.999998

            vel_dot: float = rel_vel.dot(rel_vel)
            p_v_dot_2x: float = p_v_dot * 2

            disc: float = p_v_dot_2x**2 - 4 * vel_dot * (
                rel_pos.dot(rel_pos) - pad_dd**2
            )

            if disc <= 0:
                return rel_pos, d

            t: float = (-p_v_dot_2x - math.sqrt(disc)) / (2 * vel_dot)
            # t2: float = (-p_v_dot_2x + math.sqrt(disc)) / (2 * vel_dot)

            # if the time to touch is smaller than the current delta
            # time that is to be applied in the current time loop
            if t > 0 and t < BlobPhysics.dt_timescale:
                blob1.position += blob1.velocity * t
                blob2.position += blob2.velocity * t
                blob1.pre_elapsed_time += t
                blob2.pre_elapsed_time += t
                rel_pos = blob1.position.relative_to(blob2.position)
                d = rel_pos.mag()

        # Check if the two blobs are touching
        if d <= dd:
            d_ratio: float = round((d / dd) * 100, 4)

            u1: BVec3 = blob1.velocity
            u2: BVec3 = blob2.velocity

            p1_p2: BVec3 = u1 * blob1.mass + u2 * blob2.mass

            cor1: BVec3 = u1.relative_to(u2) * BlobPhysics.COR * blob1.mass
            cor2: BVec3 = u2.relative_to(u1) * BlobPhysics.COR * blob2.mass

            m1_p_m2: float = blob1.mass + blob2.mass

            v1: BVec3 = (p1_p2 + cor2) / m1_p_m2
            v2: BVec3 = (p1_p2 + cor1) / m1_p_m2

            # ------------------------------------------------#

            key: str = str(blob1.name + blob2.name)

            BlobPhysics.hits[key] = BlobPhysics.hits.get(key, 0) + 1

            if d_ratio < 99.7 or BlobPhysics.hits[key] > 4:
                smaller_blob = blob1
                larger_blob = blob2
                if smaller_blob.radius > larger_blob.radius:
                    smaller_blob = blob2
                    larger_blob = blob1

                if not smaller_blob.dead_pending:

                    larger_blob.mass += smaller_blob.mass * 0.95
                    larger_blob.radius = BlobPhysics.new_radius(
                        larger_blob.radius, smaller_blob.radius
                    )
                    smaller_blob.dead = True
                    smaller_blob.swallowed = True
                    smaller_blob.swallowed_by(larger_blob)
                    del BlobPhysics.hits[key]

            blob1.velocity = v1
            blob2.velocity = v2

        return rel_pos, d

    @staticmethod
    def gravity_collision(blob1: MassiveBlob, blob2: MassiveBlob) -> None:
        """
        Changes acceleration of blob1 and blob2 in relation to gravitational pull with each other
        this will also first call collision_detection() with the provided blobs
        """

        b1_rel_to_b2: BVec3
        d: float

        b1_rel_to_b2, d = BlobPhysics.collision_detection(blob1, blob2)

        if d < BlobPhysics.GRAVITATIONAL_RANGE:

            blob1.acceleration -= b1_rel_to_b2 * (blob2.mass * BlobPhysics.g / d**3)

            blob2.acceleration += b1_rel_to_b2 * (blob1.mass * BlobPhysics.g / d**3)

        elif bg_vars.center_blob_escape and blob1.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob2.dead = True
            blob2.escaped = True
