"""
Newton's Laws, a simulator of physics at the scale of space

Class file for displaying a splash screen showing progress of loading blobs

by Jason Mott, copyright 2024
"""

from typing import Self

import ursina as urs  # type: ignore
from ursina.prefabs.health_bar import HealthBar  # type: ignore
from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobLoadingScreenUrsina(urs.Entity):
    """
    A class used for displaying a splash screen showing progress of loading blobs

    Attributes
    ----------
    **kwargs

    max_value : int
        The value that represents a full bar on the progress bar

    health_bar : HealthBar
        The Entity that renders the progress bar on the bottom of the loading screen

    self.point : urs.Entity
        The Entity that renders the outer circle of circles that spin

    self.points : urs.Entity
        The Entity that renders the inner circle of circles that spin

    self.point_center : urs.Entity
        The Entity that renders the inner yellow circle inside the circles that spin

    text_entity_title_shadow : urs.Text
        The Entity that puts a shadow behind the title

    text_entity_title : urs.Text
        The Entity that renders the title

    text_entity_credit_shadow : urs.Text
        The Entity that puts a shadow behind the author's name

    text_entity_credit : urs.Text
        The Entity that renders the author's name

    text_entity_loading : urs.Text
        The Entity that renders the "Loading" message

    bg : urs.Entity
        The Entity that renders the background of the loading screen


    Methods
    -------
    add_to_bar(i: int) -> None
        increments the bar counter by i, indicates how close to max_value progress should show

    increment_bar() -> None
        increments the bar counter by one, indicates how close to max_value progress should show

    bar_at_max() -> bool
        Returns true if the bar count has reached the max value, false otherwise

    reset_bar() -> None
        Resets the bar counter to zero

    update() -> None
        Called by Ursina while rendering Entities

    on_enable() -> None
        Called by Ursina when enabled=True is set

    on_disable() -> None
        Called by Ursina when enabled=False is set

    on_destroy() -> None
        Called by Ursina when destroying this instance

    """

    def __init__(self: Self, **kwargs):

        self.max_value: int = 0

        if kwargs.get("max_value") is not None:
            self.max_value = kwargs.get("max_value")

        self.health_bar: HealthBar = HealthBar(
            max_value=self.max_value,
            value=0,
            position=(-0.25, -0.25, -2),
            animation_duration=0,
            parent=self,
            bar_color=urs.color.rgba(20, 92, 158, 255),
            enabled=False,
            eternal=True,
        )
        self.health_bar.value = 0

        self.eternal = True

        super().__init__()

        self.parent = urs.camera.ui

        self.point: urs.Entity = urs.Entity(
            parent=self,
            model=urs.Circle(24, mode="point", thickness=0.03),
            color=urs.color.rgba(20, 92, 158, 255),
            scale=2,
            texture="circle",
            eternal=True,
        )
        self.point2: urs.Entity = urs.Entity(
            parent=self,
            model=urs.Circle(12, mode="point", thickness=0.03),
            color=urs.color.rgba(20, 92, 158, 255),
            scale=1,
            texture="circle",
            eternal=True,
        )

        self.point_center: urs.Entity = urs.Entity(
            parent=self,
            model=urs.Circle(16, radius=1, mode="ngon"),
            color=urs.color.rgba(
                CENTER_BLOB_COLOR[0], CENTER_BLOB_COLOR[1], CENTER_BLOB_COLOR[2], 255
            ),
            scale=0.1,
            eternal=True,
        )

        self.text_entity_title_shadow: urs.Text = urs.Text(
            parent=self,
            font=DISPLAY_FONT,
            size=1,
            scale=20,
            text="Newton's Blobs!",
            origin=(0, 0),
            position=(-0.01, 1.99),
            color=urs.color.rgba(175, 175, 175, 255),
            eternal=True,
        )

        self.text_entity_title: urs.Text = urs.Text(
            parent=self,
            font=DISPLAY_FONT,
            size=1,
            scale=20,
            text="Newton's Blobs!",
            origin=(0, 0),
            position=(0, 2),
            color=urs.color.rgba(20, 92, 158, 255),
            eternal=True,
        )

        self.text_entity_credit_shadow: urs.Text = urs.Text(
            parent=self,
            font=DISPLAY_FONT,
            size=1,
            scale=8,
            text="by Jason Mott",
            origin=(0, 0),
            position=(0.99, 1.49),
            color=urs.color.rgba(0, 0, 0, 255),
            eternal=True,
        )

        self.text_entity_credit: urs.Text = urs.Text(
            parent=self,
            font=DISPLAY_FONT,
            size=1,
            scale=8,
            text="by Jason Mott",
            origin=(0, 0),
            position=(1, 1.5),
            color=urs.color.rgba(20, 92, 158, 255),
            eternal=True,
        )

        self.text_entity_loading: urs.Text = urs.Text(
            parent=self,
            font=DISPLAY_FONT,
            size=(STAT_FONT_SIZE / 100),
            scale=6,
            text="loading blobs . . . ",
            origin=(0, 0),
            position=(0, -1.5),
            color=urs.color.white,
            eternal=True,
        )

        self.scale = 0.15

        self.bg: urs.Entity = urs.Entity(
            parent=self,
            model=urs.Quad(radius=0.025, scale=(urs.camera.aspect_ratio, 1)),
            scale=(5, 5),
            color=urs.color.rgba(0, 21, 36, 255),
            z=1,
            eternal=True,
        )

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

        if kwargs.get("enabled") is None:
            self.enabled = False

    def add_to_bar(self: Self, i: int) -> None:
        """increments the bar counter by i, indicates how close to max_value progress should show"""
        self.health_bar.value += i

    def increment_bar(self: Self) -> None:
        """increments the bar counter by one, indicates how close to max_value progress should show"""
        self.add_to_bar(1)

    def bar_at_max(self: Self) -> bool:
        """Returns true if the bar count has reached the max value, false otherwise"""
        return self.health_bar.value == self.health_bar.max_value

    def reset_bar(self: Self) -> None:
        """Resets the bar counter to zero"""
        self.health_bar.value = 0

    def update(self: Self) -> None:
        """Called by Ursina while rendering Entities"""
        self.point.rotation_z += 2.5
        self.point2.rotation_z -= 2.5

    def on_enable(self: Self) -> None:
        """Called by Ursina when enabled=True is set"""
        self.health_bar.enabled = True
        self.enabled = True

    def on_disable(self: Self) -> None:
        """Called by Ursina when enabled=False is set"""
        self.health_bar.enabled = False
        self.enabled = False

    def on_destroy(self: Self) -> None:
        """Called by Ursina when destroying this instance"""
        urs.destroy(self.bg)
        urs.destroy(self.text_entity_loading)
        urs.destroy(self.text_entity_title)
        urs.destroy(self.text_entity_title_shadow)
        urs.destroy(self.text_entity_credit)
        urs.destroy(self.text_entity_credit_shadow)
        urs.destroy(self.point_center)
        urs.destroy(self.point2)
        urs.destroy(self.point)
        urs.destroy(self.health_bar)
