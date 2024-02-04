"""
Newton's Laws, a simulator of physics at the scale of space

Class file for blobs that will interact with each other (like planets and stars)

by Jason Mott, copyright 2024
"""

import numpy as np
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
    screen : pygame.Surface
        the main surface everything will be drawn on
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

    center_blob_x = UNIVERSE_SIZE_W / 2
    center_blob_y = UNIVERSE_SIZE_H / 2
    center_blob_z = UNIVERSE_SIZE_D / 2

    def __init__(self, universe, name, color, radius, mass, x, y, z, vx, vy, vz):
        self.universe = universe
        self.scaled_universe_width = universe.get_width() * SCALE_UP
        self.scaled_universe_height = universe.get_height() * SCALE_UP

        self.scaled_universe_size_squared_x = self.scaled_universe_width * 2
        self.scaled_universe_size_squared_y = self.scaled_universe_height * 2
        self.scaled_universe_size_half_x = self.scaled_universe_width / 2
        self.scaled_universe_size_half_y = self.scaled_universe_height / 2
        self.scaled_universe_size_eighth_x = self.scaled_universe_width / 8
        self.scaled_universe_size_eighth_y = self.scaled_universe_height / 8
        self.GRAVITATIONAL_RANGE = self.scaled_universe_size_eighth_y * 6

        self.name = name
        self.color = color
        self.radius = radius
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
        self.blob_suface = BlobSurface(radius, color)
        self.pause = False

        self.fake_blob_z()

    def grid_key(self):
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
        x = self.x * SCALE_DOWN
        y = self.y * SCALE_DOWN
        z = self.z * SCALE_DOWN

        if self.name != CENTER_BLOB_NAME:
            self.blob_suface.draw(self.universe, (x, y, z), LIGHTING)
        else:
            MassiveBlob.center_blob_x = x
            MassiveBlob.center_blob_y = y
            MassiveBlob.center_blob_z = z
            pygame.draw.circle(self.universe, self.color, (x, y), self.radius)

            if not self.pause:
                glow_radius = self.radius + random.randint(1, 4)
            else:
                glow_radius = self.radius
            surf = pygame.Surface((glow_radius * 2, glow_radius * 2))
            pygame.draw.circle(
                surf, self.color, (glow_radius, glow_radius), glow_radius
            )
            self.universe.blit(
                surf,
                (
                    x - glow_radius,
                    y - glow_radius,
                ),
                special_flags=pygame.BLEND_RGB_ADD,
            )

    def fake_blob_z(self):
        # alters viewed radius to show perspective (closer=bigger/further=smaller)
        diff = self.scaled_universe_size_half_y - self.z

        self.scaled_radius = self.orig_radius[0] + (
            self.orig_radius[1] * (diff / self.scaled_universe_size_half_y)
        )
        self.radius = round(self.scaled_radius * SCALE_DOWN)
        self.blob_suface.resize(self.radius)

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
            universe_size_w = self.universe.get_width()
            universe_size_h = self.universe.get_height()
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
        # Get distance between blobs, and cross over distance
        # where gravity stops (to keep blobs from gluing to each other)
        dx = blob.x - self.x
        dy = blob.y - self.y
        dz = blob.z - self.z
        dd = (self.orig_radius[0] * 0.90) + blob.orig_radius[0]
        d = math.sqrt((dx**2) + (dy**2) + (dz**2))

        # if two blobs are within gravitational range of each other,
        # and not overlapping too much
        if d < self.GRAVITATIONAL_RANGE and d > 0:
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

        elif d > self.GRAVITATIONAL_RANGE and self.name == CENTER_BLOB_NAME:
            # If out of Sun's gravitational range, kill it
            blob.dead = True
            blob.escaped = True

    def floor_gravity(self, g):
        other_mass = FLOOR_MASS

        # Get distance between blobs, and cross over distance
        # where gravity stops (to keep blobs from gluing to each other)
        # dx = self.scaled_screen_size_half_x - self.x
        dy = self.scaled_universe_size_half_y - self.y
        # dz = self.scaled_screen_size_half_y - self.z
        d = dy

        # if two blobs are within gravitational range of each other,
        # and not overlapping too much
        if d > self.orig_radius[0]:
            F = g * self.mass * other_mass / d**2
            self.vy += F / self.mass * TIMESCALE


class BlobSurface(pygame.Surface):
    """
    A class used to draw blobs that have shadows from the center blob glow. It is a
    sub class of pygame.Surface

    Attributes
    ----------
    radius : int
        the size of the blob, by radius value
    color : tuple
        a three value tuple for RGB color value of blob



    Methods
    -------
    Except for the two below, all the methods are internal use only. Comment annotations explain what's going on
    as best they can. :)

    get_rect()
        Get the Rect object for this Surface
    draw(screen, pos=None)
        Draws this blob to the given screen, with the given posision (or uses posision already set)


    """

    def __init__(self, radius, color):
        self.LIGHT_RADIUS_MULTI = 6
        self.radius = radius
        # Double size of box, because radius can get twice the size
        self.width_center = radius + (radius)
        self.height_center = radius + (radius)
        pygame.Surface.__init__(self, (self.width_center * 2, self.height_center * 2))
        self.position = (0, 0, 0)
        self.animation_scale_div = 0.15
        self.animation_cache_size = round(1 / self.animation_scale_div)
        self.animation_radius = self.radius * self.LIGHT_RADIUS_MULTI
        self.animation_small_radius = self.animation_radius * (
            0.1 + self.animation_scale_div
        )
        self.animation_width_center = self.width_center * self.LIGHT_RADIUS_MULTI
        self.animation_height_center = self.height_center * self.LIGHT_RADIUS_MULTI
        self.rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (self.width_center * 2, self.height_center * 2),
        )
        self.color = color
        self.colorkey = (0, 0, 0)
        self.light_radius = self.animation_radius
        self.light_flag = pygame.BLEND_RGB_ADD
        self.light_color = (75, 75, 75)
        self.light_cache = np.empty([self.animation_cache_size + 1], dtype=object)
        self.light_index = self.animation_cache_size
        self.shade_radius = self.animation_radius
        self.shade_color = color
        self.shade_cache = np.empty([self.animation_cache_size + 1], dtype=object)
        self.shade_index = self.animation_cache_size
        self.alpha_image = None
        self.mask_image = None
        self.parent_blob = self.draw_blob()
        self.draw_alpha_image()
        self.draw_mask()
        # self.draw_light()
        # self.draw_shade()

    def resize(self, radius):
        # Self explanotory, I think. A way to resize without having to delete and reinstantiate
        self.radius = radius

    def get_rect(self):
        return self.rect

    def draw_blob(self):
        # Create the main blob this instance will represent. For now, just drawing to self,
        # not to any screen. This is created only once per instance no matter how many times
        # it is drawn. Called in the constructor.
        self.fill(self.colorkey)
        pygame.draw.circle(
            self, self.color, (self.width_center, self.height_center), self.radius
        )
        pygame.Surface.set_colorkey(self, self.colorkey)

    def draw_alpha_image(self):
        # Create/draw the prerequisite for the mask. Called from get_lighting_blob()
        # for each draw, but also in the constructor because it's needed to create the mask.
        # Created the first time it's called, just a fill and draw every time after.

        if self.alpha_image is None:
            self.alpha_image = self.subsurface(
                pygame.Rect(0, 0, self.width_center * 2, self.height_center * 2)
            ).convert_alpha()
            self.alpha_image.set_colorkey(self.colorkey)

        self.alpha_image.fill(self.color)

    def draw_mask(self):
        # Create/draw the mask, which will hide the parts of the overlay that go beyond the boundary
        # of the main blob. This is called in the constructor and from get_lighting_blob().
        # Created the first time it's called, just a fill and draw every time after.
        if self.mask_image is None:
            self.mask_image = pygame.Surface(self.get_size(), pygame.SRCALPHA)

        self.mask_image.fill(self.colorkey)
        pygame.draw.circle(
            self.mask_image,
            (255, 255, 255, 255),
            (self.width_center, self.height_center),
            self.radius,
        )

    def draw_light(self):
        # Create/draw the overlay the will add shine to the blob in the direction of the center blob.
        # Called in the constructor and from check_animation_radius().
        # Created the first time it's called, just a fill and draw every time after.
        if self.light_cache[self.light_index] is None:
            width = self.light_radius * 2
            height = self.light_radius * 2
            self.light_cache[self.light_index] = pygame.Surface((width, height))
            self.light_cache[self.light_index].set_colorkey(self.colorkey)

            self.light_cache[self.light_index].fill(self.colorkey)
            pygame.draw.circle(
                self.light_cache[self.light_index],
                self.light_color,
                (
                    self.light_radius,
                    self.light_radius,
                ),
                self.light_radius,
            )

        self.light_radius = self.light_cache[self.light_index].get_width() / 2

    def draw_shade(self):
        # Create/draw the overlay the will add shade (true color of blob) to the blob in the opposite
        # direction of the center blob. Called in the constructor and from check_animation_radius().
        # Created the first time it's called, just a fill and draw every time after.
        if self.shade_cache[self.shade_index] is None:
            width = self.shade_radius * 2
            height = self.shade_radius * 2
            self.shade_cache[self.shade_index] = pygame.Surface((width, height))
            self.shade_cache[self.shade_index].set_colorkey(self.colorkey)

            self.shade_cache[self.shade_index].fill(self.colorkey)
            pygame.draw.circle(
                self.shade_cache[self.shade_index],
                self.shade_color,
                (
                    self.shade_radius,
                    self.shade_radius,
                ),
                self.shade_radius,
            )

        self.shade_radius = self.shade_cache[self.shade_index].get_width() / 2

    def get_lighting_blob(self):
        # Create the final package for drawing. This puts all the peices together. Everything
        # is cached for every call, it just does a fill/draw on all the peices. This is called
        # by the draw() method.

        self.draw_alpha_image()
        self.draw_mask()

        self.check_animation_radius(self.position[2])
        offset = self.get_lighting_direction()

        self.alpha_image.blit(
            self.light_cache[self.light_index],
            (
                (self.width_center - self.light_radius) + offset[0],
                (self.height_center - self.light_radius) + offset[1],
            ),
            special_flags=self.light_flag,
        )

        if self.position[2] < MassiveBlob.center_blob_z:
            self.alpha_image.blit(
                self.shade_cache[self.shade_index],
                (
                    (self.width_center - self.shade_radius) - offset[2],
                    (self.height_center - self.shade_radius) - offset[3],
                ),
            )

        self.alpha_image.blit(
            self.mask_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
        )

        return self.alpha_image

    def check_animation_radius(self, z):
        # This points the lighted up side of the blob toward the center
        # blob, the shade side opposite of the center blob, and ensures
        # radius is honering z depth and realistic curvature.
        scale_zone_start = MassiveBlob.center_blob_z * 0.95
        scale_zone = scale_zone_start * 0.2
        scale_zone_stop = scale_zone_start - scale_zone

        diff = 0

        if z > 0 and z < MassiveBlob.center_blob_z * 2:
            diff = MassiveBlob.center_blob_z - abs(MassiveBlob.center_blob_z - z)

        real_diff = diff

        if diff < scale_zone_start:

            if diff > scale_zone_stop:
                diff = diff - scale_zone_stop
                scale = round(diff / scale_zone, 2)
            else:
                scale = self.animation_scale_div
        else:
            scale = 1

        radius = self.animation_radius * 0.13

        if scale < self.animation_scale_div:
            scale = self.animation_scale_div

        cache_index = round((scale / self.animation_scale_div))

        scale = self.animation_scale_div * cache_index

        radius = radius + round((self.animation_radius - radius) * (scale))

        if z > MassiveBlob.center_blob_z:
            self.light_radius = radius
            self.light_index = cache_index
            self.shade_index = self.animation_cache_size
        elif z < MassiveBlob.center_blob_z:
            self.shade_radius = radius
            self.shade_index = cache_index
            self.light_index = self.animation_cache_size

        self.draw_light()
        self.draw_shade()

    def get_lighting_direction(self):
        # Get the x,y,z coordinates for the center of the overlay. This will point to the
        # center blob relative to offset of the main blob center in this instance (i.e., if a line were draw between the center of
        # the main blob and the center of the overlay, the offset would point to the center blob). This is called by the get_lighting_blob()
        # method.
        x1 = self.position[0]
        y1 = self.position[1]
        z1 = self.position[2]
        x2 = MassiveBlob.center_blob_x
        y2 = MassiveBlob.center_blob_y
        z2 = MassiveBlob.center_blob_z

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        d = math.sqrt(dx**2 + dy**2 + dz**2)

        theta = math.acos(dz / d)
        phi = math.atan2(dy, dx)

        lx = self.light_radius * math.sin(theta) * math.cos(phi)
        ly = self.light_radius * math.sin(theta) * math.sin(phi)

        sx = self.shade_radius * math.sin(theta) * math.cos(phi)
        sy = self.shade_radius * math.sin(theta) * math.sin(phi)

        return (lx, ly, sx, sy)

    def draw(self, screen, pos=None, lighting=True):
        # Draw the blob to the screen.
        if pos is not None:
            self.position = pos

        if lighting:
            screen.blit(
                self.get_lighting_blob(),
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
        else:
            screen.blit(
                self,
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
