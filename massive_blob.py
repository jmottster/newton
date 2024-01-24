"""
Newton's Laws, a simulator of physics at the scale of space

Class file for blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

import math, random
import pygame
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
        self.vx = vx  # x velocity per frame
        self.vy = vy  # y velocity per frame
        self.dead = False
        self.swallowed = False
        self.escaped = False
        self.blob_suface = BlobSurface(radius, color)

    def draw(self, screen):
        x = self.x * SCALE
        y = self.y * SCALE

        if self.name != CENTER_BLOB_NAME:
            self.blob_suface.draw(screen, (x, y))
        else:
            pygame.draw.circle(screen, self.color, (x, y), self.radius)

            sun_radius = self.radius + random.randint(1, 4)
            surf = pygame.Surface((sun_radius * 2, sun_radius * 2))
            pygame.draw.circle(surf, self.color, (sun_radius, sun_radius), sun_radius)
            screen.blit(
                surf,
                (500 - sun_radius, 500 - sun_radius),
                special_flags=pygame.BLEND_RGB_ADD,
            )

    def advance(self):
        # Advace x by velocity (one frame, with TIMESTEP elapsed time)
        self.x += self.vx * TIMESCALE

        # Advace y by velocity (one frame, with TIMESTEP elapsed time)
        self.y += self.vy * TIMESCALE

    def edge_detection(self, screen, wrap):
        if wrap:
            # TODO fix wraping for scale
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
            self.vx = self.vx * 0.995
            blob.vx = blob.vx * 0.995
            self.vy = self.vy * 0.995
            blob.vy = blob.vy * 0.995

            # To prevent (or reduce) cling-ons, we have the center blob swallow blobs
            # that cross the collision boundry too far
            if self.name == CENTER_BLOB_NAME or blob.name == CENTER_BLOB_NAME:
                smaller_blob = self
                larger_blob = blob
                if self.name == CENTER_BLOB_NAME:
                    smaller_blob = blob
                    larger_blob = self
                if abs(dd - d) >= (smaller_blob.scaled_radius * 0.6):
                    larger_blob.mass += smaller_blob.mass
                    smaller_blob.dead = True
                    smaller_blob.swallowed = True

    def gravitational_pull(self, blob, g):
        # Get distance between blobs, and cross over distance
        # where gravity stops (to keep blobs from gluing to each other)
        dx = blob.x - self.x
        dy = blob.y - self.y
        d = math.sqrt((dx * dx) + (dy * dy))
        dd = (self.scaled_radius * 0.90) + blob.scaled_radius

        # if two blobs are within gravitational range of each other,
        # and not overlapping too much
        if d < self.GRAVITATIONAL_RANGE and d >= dd:
            F = g * self.mass * blob.mass / d**2

            rad = math.atan2(dy, dx)
            fdx = math.cos(rad) * F
            fdy = math.sin(rad) * F

            self.vx += fdx / self.mass * TIMESCALE
            self.vy += fdy / self.mass * TIMESCALE

        elif d > self.GRAVITATIONAL_RANGE and self.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob.dead = True
            blob.escaped = True


class BlobSurface(pygame.Surface):
    def __init__(self, radius, color):
        pygame.Surface.__init__(self, (radius * 2, radius * 2))
        self.position = (0, 0)
        self.radius = radius
        self.rect = pygame.Rect(self.position, (radius * 2, radius * 2))
        self.color = color
        self.parent_blob = self.create_blob()
        self.center_blob_pos = (SCREEN_SIZE / 2, SCREEN_SIZE / 2)
        self.shade_radius = radius * 10
        self.shade_flag_light = pygame.BLEND_RGB_ADD
        self.shade_flag_dark = pygame.BLEND_RGB_SUB
        self.shade_colorkey = (0, 0, 0)
        self.shade_color = (50, 50, 50)
        self.shade = None
        self.alpha_image = None
        self.mask_image = None
        self.create_alpha_image()
        self.create_mask()
        self.create_shade()

    def get_rect(self):
        return self.rect

    def create_blob(self):
        pygame.draw.circle(self, self.color, (self.radius, self.radius), self.radius)

    def create_shade(self):
        self.shade = pygame.Surface((self.shade_radius * 2, self.shade_radius * 2))
        pygame.draw.circle(
            self.shade,
            self.shade_color,
            (self.shade_radius, self.shade_radius),
            self.shade_radius,
        )
        self.shade.set_colorkey(self.shade_colorkey)

    def create_alpha_image(self):
        self.alpha_image = self.subsurface(
            pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        ).convert_alpha()

    def create_mask(self):
        self.mask_image = pygame.Surface(self.alpha_image.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(
            self.mask_image,
            (255, 255, 255, 255),
            (self.radius, self.radius),
            self.radius,
        )

    def get_shaded_blob(self):
        self.create_alpha_image()

        offset = self.get_lighting_direction()

        self.alpha_image.blit(
            self.shade,
            (
                -(self.shade_radius - self.radius) + offset[0],
                -(self.shade_radius - self.radius) + offset[1],
            ),
            special_flags=self.shade_flag_light,
        )

        self.alpha_image.blit(
            self.mask_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
        )

        return self.alpha_image

    def get_lighting_direction(self):
        x1 = self.position[0]
        y1 = self.position[1]
        x2 = self.center_blob_pos[0]
        y2 = self.center_blob_pos[1]

        dx = x2 - x1
        dy = y2 - y1

        theta = math.atan2(dy, dx)

        x = self.shade_radius * math.cos(theta)
        y = self.shade_radius * math.sin(theta)

        return (x, y)

    def draw(self, screen, pos=None):
        if pos is not None:
            self.position = pos

        screen.blit(
            self.get_shaded_blob(),
            (self.position[0] - self.radius, self.position[1] - self.radius),
        )
