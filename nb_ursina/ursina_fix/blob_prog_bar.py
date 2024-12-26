"""
Newton's Laws, a simulator of physics at the scale of space

Class to create a progress bar

by Jason Mott, copyright 2024
"""

from typing import Any, Self, Tuple
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from .blob_text import BlobText
from .blob_button import BlobButton
from .blob_quad import createBlobQuad

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobProgBar(BlobButton):
    """
    A class

    Attributes
    ----------
    value: int
        The number that indicates progress toward max_value

    show_text: bool
        Whether or not to show the display text

    bar_color: urs.Color
        The color of the progress bar

    """

    def __init__(
        self: Self,
        max_value: int = 100,
        value: int = None,
        roundness: float = 0.125,
        animation_duration: float = 0.1,
        show_text: bool = True,
        text_size: float = 0.7,
        origin: Tuple[float, float, float] = (0, 0, 0),
        **kwargs,
    ):

        super().__init__(
            parent=kwargs.get("parent", urs.camera.ui),
            radius=roundness,
            scale=(2, 1, 0.5),
            position=(-1, 0, 0),
            text="hp / max hp",
            text_size=text_size,
            color=urs.color.black66,
            highlight_color=urs.color.black66,
            origin=origin,
            ignore=True,
        )

        if kwargs.get("parent", None) is not None:
            del kwargs["parent"]

        self.bar: urs.Entity = urs.Entity(
            name="prog bar bar",
            parent=self,
            scale=(2, 1, 0.5),
            model=createBlobQuad(radius=roundness),
            origin=(-0.5, 0, 0),
            y=-0.005,
            x=-self.scale_x / 2,
            color=urs.color.red.tint(-0.2),
            ignore=True,
        )

        self.bar_origin = self.bar.origin

        self.max_value: int = max_value
        self.clamp: bool = True
        self.roundness: float = roundness
        self.animation_duration: float = animation_duration
        if not show_text:
            self.show_text = False
        self._value: int = None
        self.value = self.max_value if value == None else value

        for key in (
            "model",
            "origin",
            "origin_x",
            "origin_y",
            "origin_z",
            "collider",
            "shader",
            "texture",
            "texture_scale",
            "texture_offset",
        ):
            if key in kwargs:
                setattr(self, key, kwargs[key])
                del kwargs[key]

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def value(self: Self) -> int:
        """The number that indicates progress toward max_value"""
        return getattr(self, "_value", None)

    @value.setter
    def value(self: Self, n: int) -> None:
        """Sets the number that indicates progress toward max_value"""
        if self.clamp:
            n = urs.clamp(n, 0, self.max_value)

        self._value = n

        self.bar.scale_x = self.scale_x * (n / self.max_value)
        self.text = f"{n} / {self.max_value}"

        aspect_ratio = (self.bar.scale_x / self.bar.scale_z) * 2
        if aspect_ratio >= 0.5:
            self.bar.model = createBlobQuad(radius=self.roundness, aspect=aspect_ratio)

        self.bar.origin = self.bar.origin

    @property
    def show_text(self: Self) -> bool:
        """Whether or not to show the display text"""
        return self.text_entity.enabled

    @show_text.setter
    def show_text(self: Self, value: bool) -> None:
        """Sets whether or not to show the display text"""
        self.text_entity.enabled = value

    @property
    def bar_color(self: Self) -> urs.Color:
        """The color of the progress bar"""
        return self.bar.color

    @bar_color.setter
    def bar_color(self: Self, value: urs.Color) -> None:
        """Sets the color of the progress bar"""
        self.bar.color = value

    def on_destroy(self: Self) -> None:
        urs.destroy(self.bar)
        super().on_destroy()
