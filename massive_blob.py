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

    edge_detection(screen, wrap)
        Checks to see if blob is hitting the edge of the screen, and reverses velocity if so
        or it wraps to other end of screen if wrap==True (wrap currently not working)

    collision_detection(blob)
        Check to see if this blob is coliding with provided blob, and adjusts velocity of each
        according to Newton's Laws

    gravitational_pull(blob, g)
        Changes velocity of self in relation to gravitational pull with provided blob
        g is the Gravitational Constant to be applied to equation
    """

    def __init__(self, name, color, radius, mass, x, y, vx, vy):
        self.GRAVITATIONAL_RANGE = SCALED_SCREEN_SIZE
        self.mass = mass
        self.name = name
        self.color = color
        self.radius = radius
        self.scaled_radius = (self.radius / SCALE_FACTOR) * AU
        self.x = x
        self.y = y
        self.ghostx = x
        self.ghosty = y
        self.vx = vx  # x velocity per frame
        self.vy = vy  # y velocity per frame
        self.ghosting = False

    def advance(self):
        # Advace x by velocity (one frame, with TIMESTEP elapsed time)
        self.x += self.vx * TIMESCALE

        # Advace y by velocity (one frame, with TIMESTEP elapsed time)
        self.y += self.vy * TIMESCALE

    def edge_detection(self, screen, wrap):
        if (
            wrap == True
        ):  # TODO fix wraping for scale, get ghosting to work (or find a new strategy)
            # Move real x to other side of screen if it's gone off the edge
            if self.vx < 0 and self.x < 0:
                self.x = screen.get_width()
            elif self.vx > 0 and self.x > screen.get_width():
                self.x = 0

            # Move real y to other side of screen if it's gone off the edge
            if self.vy < 0 and self.y < 0:
                self.y = screen.get_height()
            elif self.vy > 0 and self.y > screen.get_height():
                self.y = 0

            self.ghostx, self.ghosty, self.ghosting = self.x, self.y, False

            # If radius has gone off x axis edge, draw ghost selficle on other side of screen for wraping effect
            if (self.x - self.radius) < 0 and self.x >= 0:
                self.ghostx = screen.get_width() + self.x
                self.ghosting = True
            elif (
                self.x + self.radius
            ) > screen.get_width() and self.x <= screen.get_width():
                self.ghostx = 0 - (screen.get_width() - self.x)
                self.ghosting = True

            # If radius has gone off y axis edge, draw ghost selficle on other side of screen for wraping effect
            if (self.y - self.radius) < 0 and self.y >= 0:
                self.ghosty = screen.get_height() + self.y
                self.ghosting = True
            elif (
                self.y + self.radius
            ) > screen.get_height() and self.y <= screen.get_height():
                self.ghosty = 0 - (screen.get_height() - self.y)
                self.ghosting = True

        else:
            zero = 0  # -(SCALED_SCREEN_SIZE / 4)
            screen_size = SCALED_SCREEN_SIZE  # + (SCALED_SCREEN_SIZE / 4)

            # Change x direction if hitting the edge of screen
            if ((self.x - self.scaled_radius) < zero) and (self.vx < 0):
                self.vx = -self.vx
            if ((self.x + self.scaled_radius) > screen_size) and (self.vx > 0):
                self.vx = -self.vx

            # Change y direction if hitting the edge of screen
            if ((self.y - self.scaled_radius) < zero) and (self.vy < 0):
                self.vy = -self.vy
            if ((self.y + self.scaled_radius) > screen_size) and self.vy > 0:
                self.vy = -self.vy

    def collision_detection(self, blob):
        dx = blob.x - self.x
        dy = blob.y - self.y
        d = math.sqrt((dx * dx) + (dy * dy))
        dd = self.scaled_radius + blob.scaled_radius

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

            # some fake energy loss due to collision
            self.vx = self.vx * 0.99
            blob.vx = blob.vx * 0.99
            self.vy = self.vy * 0.99
            blob.vy = blob.vy * 0.99

    def gravitational_pull(self, blob, g):
        dx = blob.x - self.x
        dy = blob.y - self.y
        d = math.sqrt((dx * dx) + (dy * dy))
        dd = self.scaled_radius + blob.scaled_radius

        if d < self.GRAVITATIONAL_RANGE and d > dd:
            F = g * self.mass * blob.mass / d**2

            theta = math.atan2(dy, dx)
            fdx = math.cos(theta) * F
            fdy = math.sin(theta) * F

            # print(
            #     f"s={self.name} to {blob.name} d={round(d)}, F={F} vx={self.vx}, vy={self.vy}, fdx={fdx}, fdy={fdy}"
            # )
            # i = input()

            self.vx += fdx / self.mass * TIMESCALE
            self.vy += fdy / self.mass * TIMESCALE
