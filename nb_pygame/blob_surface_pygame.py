"""
Newton's Laws, a simulator of physics at the scale of space

Class for building the blob objects for display

by Jason Mott, copyright 2024
"""

from typing import ClassVar, Tuple, Self, cast
import numpy as np
import numpy.typing as npt
import math, random
import pygame

from newtons_blobs.globals import *
from newtons_blobs.resources import resource_path
from newtons_blobs.blob_universe import BlobUniverse

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobSurfacePygame:
    """
    A class used to draw blobs that have shadows from the center blob glow.

    Attributes
    ----------
    radius : float
        the size of the blob, by radius value
    color : Tuple[int, int, int]
        a three value tuple for RGB color value of blob
    universe : BlobUniverse
        object representing the universe space to draw blobs onto
    texture : str = None
        Not used, this is a 2d implementation
    rotation_speed : float = None
        Not used, this is a 2d implementation
    rotation_pos : Tuple[int, int, int] = None
        Not used, this is a 2d implementation

    Methods
    -------
    Except for the three below, all the methods are internal use only. Comment annotations explain what's going on
    as best they can. :)

    resize(radius: float) -> None
        Sets a new radius for this blob

    get_size() -> Tuple[float]
        Returns the largest possible size for this instance (not affected by resize())

    update_center_blob(x: float, y: float, z: float) -> None
        Update the x,y,z of the center blob (the blob all other blobs get lighting from)

    draw_alpha_image(self: Self) -> None
        Create/draw the prerequisite for the mask. Called from get_lighting_blob()
        for each draw, but also in the constructor because it's needed to create the mask.
        Created the first time it's called, just a fill and draw every time after

    draw_mask(self: Self) -> None
        Create/draw the mask, which will hide the parts of the overlay that go beyond the boundary
        of the main blob. This is called in the constructor and from get_lighting_blob().
        Created the first time it's called, just a fill and draw every time after

    draw_light(self: Self) -> None
        Create/draw the overlay the will add shine to the blob in the direction of the center blob.
        Called from check_animation_radius().
        This is an array of cached sizes, selected via the value of self.light_index.
        Each is created the first time it's called, and just a fill and draw every time after

    draw_shade(self: Self) -> None
        Create/draw the overlay the will add shade (true color of blob) to the blob in the opposite
        direction of the center blob. Called from check_animation_radius().
        This is an array of cached sizes, selected via the value of self.light_index.
        Each is created the first time it's called, and just a fill and draw every time after

    get_lighting_blob(self: Self) -> pygame.Surface
        Create the final package for drawing. This puts all the pieces together. Everything
        is cached for every call, it just does a fill/draw on all the pieces. This is called
        by the draw() method

    check_animation_radius(self: Self, z: float) -> None
        This points the lighted up side of the blob toward the center
        blob, the shade side opposite of the center blob, and ensures
        radius is honoring z depth and realistic curvature

    get_lighting_direction(self: Self) -> Tuple[float, float, float, float]
        Get the x,y,z coordinates for the center of the overlay. This will point to the
        center blob relative to offset of the main blob center in this instance (i.e., if a line were drawn between the center of
        the main blob and the center of the overlay, the offset would point to the center blob). This is called by the get_lighting_blob()
        method

    draw(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects

    draw_as_center_blob(pos: Tuple[float] = None, lighting: bool = True) -> None
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect

    destroy() -> None
        Call to get rid of this instance, so it can clean up
    """

    __slots__ = (
        "texture",
        "rotation_speed",
        "rotation_pos",
        "py_universe",
        "radius",
        "width_center",
        "height_center",
        "size",
        "blob_font",
        "position",
        "animation_scale_div",
        "animation_cache_size",
        "animation_radius",
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
    )

    center_blob_x: ClassVar[float] = UNIVERSE_SIZE_W / 2
    center_blob_y: ClassVar[float] = UNIVERSE_SIZE_H / 2
    center_blob_z: ClassVar[float] = UNIVERSE_SIZE_D / 2
    LIGHT_RADIUS_MULTI: ClassVar[float] = 6

    def __init__(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ):

        self.texture = texture
        self.rotation_speed = rotation_speed
        self.rotation_pos = rotation_pos

        self.py_universe: pygame.Surface = cast(
            pygame.Surface, universe.get_framework()
        )
        self.radius: float = radius
        # Double size of box, because radius can get twice the size
        self.width_center: float = radius + (radius)
        self.height_center: float = radius + (radius)
        self.size: Tuple[float, float] = (self.width_center * 2, self.height_center * 2)
        self.blob_font: pygame.font.Font = pygame.font.Font(
            resource_path(Path(DISPLAY_FONT)), BLOB_FONT_SIZE
        )
        self.position: Tuple[float, float, float] = (0, 0, 0)
        self.animation_scale_div: float = 0.15
        self.animation_cache_size: int = round(1 / self.animation_scale_div)
        self.animation_radius: float = (
            self.radius * BlobSurfacePygame.LIGHT_RADIUS_MULTI
        )
        self.color: Tuple[int, int, int] = color
        self.colorkey: Tuple[int, int, int] = (0, 0, 0)
        self.light_radius: float = self.animation_radius
        self.light_flag: int = pygame.BLEND_RGB_ADD
        self.light_color: Tuple[int, int, int] = (75, 75, 75)
        self.light_cache: npt.NDArray = np.empty(
            [self.animation_cache_size + 1], dtype=pygame.Surface
        )
        self.light_index: int = self.animation_cache_size
        self.shade_radius: float = self.animation_radius
        self.shade_color: Tuple[int, int, int] = color
        self.shade_cache: npt.NDArray = np.empty(
            [self.animation_cache_size + 1], dtype=pygame.Surface
        )
        self.shade_index: int = self.animation_cache_size
        self.alpha_image: pygame.Surface = None
        self.mask_image: pygame.Surface = None
        self.draw_alpha_image()
        self.draw_mask()

    def resize(self: Self, radius: float) -> None:
        """Sets a new radius for this blob"""
        self.radius = radius

    def get_size(self: Self) -> Tuple[float, float]:
        """Returns the largest possible size for this instance (not affected by resize())"""
        return self.size

    def update_center_blob(self: Self, x: float, y: float, z: float) -> None:
        """Update the x,y,z of the center blob (the blob all other blobs get lighting from)"""
        BlobSurfacePygame.center_blob_x = x
        BlobSurfacePygame.center_blob_y = y
        BlobSurfacePygame.center_blob_z = z

    def draw_alpha_image(self: Self) -> None:
        """
        Create/draw the prerequisite for the mask. Called from get_lighting_blob()
        for each draw, but also in the constructor because it's needed to create the mask.
        Created the first time it's called, just a fill and draw every time after
        """

        if self.alpha_image is None:
            self.alpha_image = pygame.Surface(self.get_size()).convert_alpha()
            self.alpha_image.set_colorkey(self.colorkey)

        self.alpha_image.fill(self.color)

    def draw_mask(self: Self) -> None:
        """
        Create/draw the mask, which will hide the parts of the overlay that go beyond the boundary
        of the main blob. This is called in the constructor and from get_lighting_blob().
        Created the first time it's called, just a fill and draw every time after
        """
        if self.mask_image is None:
            self.mask_image = pygame.Surface(self.get_size(), pygame.SRCALPHA)

        self.mask_image.fill(self.colorkey)
        pygame.draw.circle(
            self.mask_image,
            (255, 255, 255, 255),
            (self.width_center, self.height_center),
            self.radius,
        )

    def draw_light(self: Self) -> None:
        """
        Create/draw the overlay the will add shine to the blob in the direction of the center blob.
        Called from check_animation_radius().
        This is an array of cached sizes, selected via the value of self.light_index.
        Each is created the first time it's called, and just a fill and draw every time after
        """
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

    def draw_shade(self: Self) -> None:
        """
        Create/draw the overlay the will add shade (true color of blob) to the blob in the opposite
        direction of the center blob. Called from check_animation_radius().
        This is an array of cached sizes, selected via the value of self.light_index.
        Each is created the first time it's called, and just a fill and draw every time after
        """
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

    def get_lighting_blob(self: Self) -> pygame.Surface:
        """
        Create the final package for drawing. This puts all the pieces together. Everything
        is cached for every call, it just does a fill/draw on all the pieces. This is called
        by the draw() method
        """

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

        if self.position[2] < BlobSurfacePygame.center_blob_z:
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

    def check_animation_radius(self: Self, z: float) -> None:
        """
        This points the lighted up side of the blob toward the center
        blob, the shade side opposite of the center blob, and ensures
        radius is honoring z depth and realistic curvature
        """
        scale_zone_start: float = BlobSurfacePygame.center_blob_z * 0.95
        scale_zone: float = scale_zone_start * 0.2
        scale_zone_stop: float = scale_zone_start - scale_zone

        diff: float = 0.0

        if z > 0 and z < BlobSurfacePygame.center_blob_z * 2:
            diff = BlobSurfacePygame.center_blob_z - abs(
                BlobSurfacePygame.center_blob_z - z
            )

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

        if z > BlobSurfacePygame.center_blob_z:
            self.light_radius = radius
            self.light_index = cache_index
            self.shade_index = self.animation_cache_size
        elif z < BlobSurfacePygame.center_blob_z:
            self.shade_radius = radius
            self.shade_index = cache_index
            self.light_index = self.animation_cache_size

        self.draw_light()
        self.draw_shade()

    def get_lighting_direction(self: Self) -> Tuple[float, float, float, float]:
        """
        Get the x,y,z coordinates for the center of the overlay. This will point to the
        center blob relative to offset of the main blob center in this instance (i.e., if a line were drawn between the center of
        the main blob and the center of the overlay, the offset would point to the center blob). This is called by the get_lighting_blob()
        method
        """
        x1 = self.position[0]
        y1 = self.position[1]
        z1 = self.position[2]
        x2 = BlobSurfacePygame.center_blob_x
        y2 = BlobSurfacePygame.center_blob_y
        z2 = BlobSurfacePygame.center_blob_z

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

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draws this blob to the universe surface, with the given position (or uses position already set),
        send (pos,False) to turn off lighting effects
        """
        if pos is not None:
            self.position = pos

        if lighting:
            self.py_universe.blit(
                self.get_lighting_blob(),
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
        else:
            self.alpha_image.blit(
                self.mask_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
            )
            self.py_universe.blit(
                self.alpha_image,
                (
                    self.position[0] - self.width_center,
                    self.position[1] - self.height_center,
                ),
            )
        # Uncomment for writing labels on blobs
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

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        """
        Draw the blob to the universe surface as the center blob (special glowing effect, no light/shade effect)
        send (pos,False) to turn off glowing effect
        """
        if pos is not None:
            self.position = pos

        pygame.draw.circle(
            self.py_universe,
            self.color,
            (self.position[0], self.position[1]),
            self.radius,
        )

        if lighting:
            glow_radius = self.radius + random.randint(1, 4)
        else:
            glow_radius = self.radius

        surf = pygame.Surface((glow_radius * 2, glow_radius * 2))

        pygame.draw.circle(surf, self.color, (glow_radius, glow_radius), glow_radius)

        self.py_universe.blit(
            surf,
            (
                self.position[0] - glow_radius,
                self.position[1] - glow_radius,
            ),
            special_flags=pygame.BLEND_RGB_ADD,
        )

    def destroy(self: Self) -> None:
        """Call to get rid of this instance, so it can clean up"""
        pass
