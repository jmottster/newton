"""
Newton's Laws, a simulator of physics at the scale of space

Class file for building the blob objects for display

by Jason Mott, copyright 2024
"""

import numpy as np
import math, random
import pygame

from .globals import *
from .resources import resource_path

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobSurface(pygame.Surface):
    """
    A class used to draw blobs that have shadows from the center blob glow. It is a
    sub class of pygame.Surface

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : tuple
        a three value tuple for RGB color value of blob



    Methods
    -------
    Except for the three below, all the methods are internal use only. Comment annotations explain what's going on
    as best they can. :)

    resize(radius)
        radius: float the new size
        Sets a new radius for this blob
    get_rect()
        Get the Rect object for this Surface
    draw(screen, pos=None)
        Draws this blob to the given screen, with the given posision (or uses posision already set)


    """

    __slots__ = (
        "universe",
        "LIGHT_RADIUS_MULTI",
        "radius",
        "width_center",
        "height_center",
        "blob_font",
        "position",
        "animation_scale_div",
        "animation_cache_size",
        "animation_radius",
        "animation_small_radius",
        "animation_width_center",
        "animation_height_center",
        "rect",
        "color",
        "colorkey",
        "light_radius",
        "light_flag",
        "light_color",
        "light_cache",
        "light_index",
        "shade_radius",
        "shade_color",
        "shade_cache",
        "shade_index",
        "alpha_image",
        "mask_image",
        "parent_blob",
    )

    center_blob_x = UNIVERSE_SIZE_W / 2
    center_blob_y = UNIVERSE_SIZE_H / 2
    center_blob_z = UNIVERSE_SIZE_D / 2

    def __init__(self, radius, color, universe):
        self.universe = universe
        self.LIGHT_RADIUS_MULTI = 6
        self.radius = radius
        # Double size of box, because radius can get twice the size
        self.width_center = radius + (radius)
        self.height_center = radius + (radius)
        pygame.Surface.__init__(self, (self.width_center * 2, self.height_center * 2))
        self.blob_font = pygame.font.Font(resource_path(DISPLAY_FONT), BLOB_FONT_SIZE)
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

    def resize(self, radius):
        # Self explanotory, I think. A way to resize without having to delete and reinstantiate
        self.radius = radius

    def update_center_blob(self, x, y, z):
        BlobSurface.center_blob_x = x
        BlobSurface.center_blob_y = y
        BlobSurface.center_blob_z = z

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

        if self.position[2] < BlobSurface.center_blob_z:
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
        scale_zone_start = BlobSurface.center_blob_z * 0.95
        scale_zone = scale_zone_start * 0.2
        scale_zone_stop = scale_zone_start - scale_zone

        diff = 0

        if z > 0 and z < BlobSurface.center_blob_z * 2:
            diff = BlobSurface.center_blob_z - abs(BlobSurface.center_blob_z - z)

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

        if z > BlobSurface.center_blob_z:
            self.light_radius = radius
            self.light_index = cache_index
            self.shade_index = self.animation_cache_size
        elif z < BlobSurface.center_blob_z:
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
        x2 = BlobSurface.center_blob_x
        y2 = BlobSurface.center_blob_y
        z2 = BlobSurface.center_blob_z

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

    def draw(self, pos=None, lighting=True):
        # Draw the blob to the screen.
        if pos is not None:
            self.position = pos

        if lighting:
            self.universe.blit(
                self.get_lighting_blob(),
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
        else:
            self.universe.blit(
                self,
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
        # Uncomment for writting lables on blobs
        # mass_text = blob_font.render(
        #     f"{}",
        #     1,
        #     (255, 255, 255),
        #     BACKGROUND_COLOR,
        # )
        # self.universe.blit(
        #     mass_text,
        #     (
        #         (self.position[0]) - (mass_text.get_width() / 2),
        #         (self.position[1])
        #         - (self.radius)
        #         - (mass_text.get_height()),
        #     ),
        # )

    def draw_as_center_blob(self, pos=None, lighting=True):
        if pos is not None:
            self.position = pos

        pygame.draw.circle(
            self.universe, self.color, (self.position[0], self.position[1]), self.radius
        )

        if lighting:
            glow_radius = self.radius + random.randint(1, 4)
        else:
            glow_radius = self.radius

        surf = pygame.Surface((glow_radius * 2, glow_radius * 2))

        pygame.draw.circle(surf, self.color, (glow_radius, glow_radius), glow_radius)

        self.universe.blit(
            surf,
            (
                self.position[0] - glow_radius,
                self.position[1] - glow_radius,
            ),
            special_flags=pygame.BLEND_RGB_ADD,
        )
