"""
Newton's Laws, a simulator of physics at the scale of space

Class file for blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

import math
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.1"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class MassiveBlob:

    """
    A class used to represent a massive space blob like a planet or a star

    Attributes
    ----------
    name : str
        a string to identify the blob
    color : tuple
        a three value tuple for RGB color value of blob
    radius : int
        the size of the blob, by radius value
    mass : float
        the mass of the object -- use planet scale kg values (see global min and max values)
    x : int
        initial x coordinate for center of blob
    y : int
        initial y coordinate for center of blob
    vx : float
        initial x direction velocity in meters per second
    vy : float
        initial y direction velocity in meters per second

    Methods
    -------
    advance()
        applies velocity to blob, changing its x,y coordinates for next frame draw

    edge_detection(wrap)
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)

    collision_detection(blob)
        Check to see if this blob is coliding with provided blob, and adjusts velocity of each
        according to Newton's Laws

    gravitational_pull(blob, g)
        Changes velocity of self in relation to gravitational pull with provided blob
        g is the Gravitational Constant to be applied to equation
    """

    def __init__(self, name, color, radius, mass, x, y, z, vx, vy, vz):
        self.GRAVITATIONAL_RANGE = SCALED_SCREEN_SIZE
        self.scaled_screen_size_squared = SCALED_SCREEN_SIZE * 2
        self.scaled_screen_size_half = SCALED_SCREEN_SIZE / 2

        self.name = name
        self.color = color
        self.radius = radius
        self.scaled_radius = (self.radius / SCALE_FACTOR) * AU
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

        self.fake_blob_z()

    def fake_blob_z(self):
        # alters viewed radius to show perspective (closer=bigger/further=smaller)
        diff = self.scaled_screen_size_half - self.z
        self.scaled_radius = self.orig_radius[0] + (
            self.orig_radius[1] * (diff / self.scaled_screen_size_half) * 0.75
        )
        self.radius = self.scaled_radius * SCALE

    def advance(self):
        # Advace x by velocity (one frame, with TIMESTEP elapsed time)
        self.x += self.vx * TIMESCALE

        # Advace y by velocity (one frame, with TIMESTEP elapsed time)
        self.y += self.vy * TIMESCALE

        # Advace z by velocity (one frame, with TIMESTEP elapsed time)
        self.z += self.vz * TIMESCALE

        self.fake_blob_z()

    def edge_detection(self, wrap):
        if wrap:
            # TODO fix wraping for scale
            # Move real x to other side of screen if it's gone off the edge
            if self.vx < 0 and self.x < 0:
                self.x = SCALED_SCREEN_SIZE
            elif self.vx > 0 and self.x > SCALED_SCREEN_SIZE:
                self.x = 0

            # Move real y to other side of screen if it's gone off the edge
            if self.vy < 0 and self.y < 0:
                self.y = SCALED_SCREEN_SIZE
            elif self.vy > 0 and self.y > SCALED_SCREEN_SIZE:
                self.y = 0

        else:
            zero = 0  # -(SCALED_SCREEN_SIZE / 4)
            screen_size = (
                SCREEN_SIZE  # SCALED_SCREEN_SIZE  # + (SCALED_SCREEN_SIZE / 4)
            )
            local_x = self.x * SCALE
            local_y = self.y * SCALE
            local_z = self.z * SCALE

            # Change x direction if hitting the edge of screen
            if ((local_x - self.radius) <= zero) and (self.vx <= 0):
                self.vx = -self.vx
                self.x = self.scaled_radius
                self.vx = self.vx * 0.995

            if ((local_x + self.radius) >= screen_size) and (self.vx >= 0):
                self.vx = -self.vx
                self.x = SCALED_SCREEN_SIZE - self.scaled_radius
                self.vx = self.vx * 0.995

            # Change y direction if hitting the edge of screen
            if ((local_y - self.radius) <= zero) and (self.vy <= 0):
                self.vy = -self.vy
                self.y = self.scaled_radius
                self.vy = self.vy * 0.995

            if ((local_y + self.radius) >= screen_size) and self.vy >= 0:
                self.vy = -self.vy
                self.y = SCALED_SCREEN_SIZE - self.scaled_radius
                self.vy = self.vy * 0.995

            # Change z direction if hitting the edge of screen
            if ((local_z - self.radius) <= screen_size) and (self.vz <= 0):
                self.vz = -self.vz
                self.z = self.scaled_radius
                self.vz = self.vz * 0.995

            if ((local_z + self.radius) >= screen_size - screen_size) and self.vz >= 0:
                self.vz = -self.vz
                self.z = SCALED_SCREEN_SIZE - self.scaled_radius
                self.vz = self.vz * 0.995

    def collision_detection(self, blob):
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
        # Get distance between blobs, and cross over distance
        # where gravity stops (to keep blobs from gluing to each other)
        dx = blob.x - self.x
        dy = blob.y - self.y
        dz = blob.z - self.z

        d = math.sqrt((dx**2) + (dy**2) + (dz**2))
        dd = (self.orig_radius[0] * 0.90) + blob.orig_radius[0]

        # if two blobs are within gravitational range of each other,
        # and not overlapping too much
        if d < self.GRAVITATIONAL_RANGE and d >= dd:
            F = g * self.mass * blob.mass / d**2

            theta = math.acos(dz / d)
            phi = math.atan2(dy, dx)

            fdx = F * math.sin(theta) * math.cos(phi)
            fdy = F * math.sin(theta) * math.sin(phi)
            fdz = F * math.cos(theta)

            self.vx += fdx / self.mass * TIMESCALE
            self.vy += fdy / self.mass * TIMESCALE
            self.vz += fdz / self.mass * TIMESCALE

        elif d > self.GRAVITATIONAL_RANGE and self.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob.dead = True
            blob.escaped = True

    def floor_gravity(self, g):
        other_mass = FLOOR_MASS

        # Get distance between blobs, and cross over distance
        # where gravity stops (to keep blobs from gluing to each other)
        dx = self.scaled_screen_size_half - self.x
        dy = SCALED_SCREEN_SIZE - self.y
        dz = self.scaled_screen_size_half - self.z
        d = dy

        # if two blobs are within gravitational range of each other,
        # and not overlapping too much
        if d > self.orig_radius[0]:
            F = g * self.mass * other_mass / d**2

            # theta = math.acos(dz / d)
            # phi = math.atan2(dy, dx)

            # fdx = F * math.sin(theta) * math.cos(phi)
            # fdy = F * math.sin(theta) * math.sin(phi)
            # fdz = F * math.cos(theta)

            # self.vx += fdx / self.mass * TIMESCALE
            self.vy += F / self.mass * TIMESCALE
            # self.vz += fdz / self.mass * TIMESCALE
