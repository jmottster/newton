"""
Newton's Laws, a simulator of physics at the scale of space

A collection of utility classes

by Jason Mott, copyright 2024
"""

import math
from typing import ClassVar, Self, Tuple
from collections import deque

from panda3d.core import Vec3 as PanVec3, BitMask32  # type: ignore

import ursina as urs  # type: ignore
import ursina.shaders as shd  # type: ignore

from newtons_blobs.globals import *

from .fps import FPS
from .ursina_fix import BlobText


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class MathFunctions:
    """
    Static class to hold math related helper functions

    Attributes
    ----------
    camera_mask_counter : int use to keep track of how many bit_masks you've used

    bit_masks: list a list of available bit masks to use in lights and cameras

    Methods
    -------
    distance(point1: PanVec3, point2: PanVec3) -> float
        returns the distance between the two points

    """

    camera_mask_counter: int = 0
    bit_masks: list = [
        BitMask32(1),
        BitMask32(2),
        BitMask32(4),
        BitMask32(8),
        BitMask32(16),
        BitMask32(32),
        BitMask32(64),
        # BitMask32(128),
    ]

    @staticmethod
    def distance(point1: PanVec3, point2: PanVec3) -> float:
        """returns the distance between the two points"""
        diff: PanVec3 = point2 - point1
        return math.sqrt((diff[0] ** 2) + (diff[1] ** 2) + (diff[2] ** 2))


class FontUtils:
    """
    Static class for repetitive tasks related to setting up text for display

    Methods
    -------
    get_text_parent() -> urs.Entity
        Get the shared parent Entity which is the display field

    position_text(x: float, y: float, text_entity: BlobText) -> None
        Apply standard fixes to x/y positioning for text

    """

    font_overlay: urs.Entity = None

    @staticmethod
    def get_text_parent() -> urs.Entity:
        """Get the shared parent Entity which is the display field"""
        if FontUtils.font_overlay is None:
            FontUtils.font_overlay = urs.Entity(
                parent=urs.camera.ui,
                x=0,
                # y=0,
                z=0,
                scale=1,
                eternal=True,
                unlit=True,
                shader=shd.unlit_shader,
            )
        return FontUtils.font_overlay

    @staticmethod
    def position_text(x: float, z: float, text_entity: BlobText) -> None:
        """Apply standard fixes to x/y positioning for text"""

        width_ratio = urs.window.size[0] / urs.window.size[1]
        height_ratio = 1  # urs.window.size[1] / urs.window.size[0]
        height = urs.window.size[1]
        if urs.window.fullscreen:
            width_ratio = urs.window.main_monitor.width / urs.window.main_monitor.height
            height = urs.window.main_monitor.height
        x = (x * width_ratio) / urs.window.size[0]
        z = (z * height_ratio) / height

        x -= width_ratio / 2
        z -= height_ratio / 2

        text_entity.position = (x, 0, z)


class FPSDisplay:
    """
    A class used to display the current FPS onscreen

    Methods
    -------
    render(x: float, z: float) -> None
        Renders the fps to the display object at x,z coordinates
    """

    def __init__(self: Self):

        self.font = DISPLAY_FONT
        self.font_size = STAT_FONT_SIZE / 100
        self.text = BlobText(
            font=self.font,
            size=self.font_size,
            resolution=100 * self.font_size,
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=False,
            origin=(-0.5, 0, -0.5),
            eternal=True,
        )

    def render(self: Self, fps: FPS, x: float, z: float) -> None:
        """Renders the fps to the display object at x,y coordinates"""

        self.text.text = f"FPS {round(fps.clock.getAverageFrameRate(),2)}"

        FontUtils.position_text(x, z + (self.text.height * 100), self.text)

        self.text.create_background(
            self.text.size * 0.3,
            self.text.size * 0.5,
            urs.color.rgb32(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

        if not self.text.enabled:
            self.text.enabled = True


class TempMessage(urs.Entity):
    """
    An Entity class for controlling temporary text. It expires in "counter" seconds, or 30
    seconds by default


    Attributes
    ----------
    **kwargs
        Specific to this class: text (the text to be displayed),
        pos (the x/y position, in Vec2 format), counter (number of seconds to expire)

    Methods
    -------
    set_text(text: str, pos: urs.Vec3) -> None
        Set the text to be displayed, and its position

    get_text() -> str
        Returns the text set as the display text

    update_text_pos(pos: urs.Vec3) -> None
        Updates the position the text will be displayed at

    reset_counter() -> None
        Reset the counter back to its starting point

    update() -> None
        Called by Ursina, once per frame

    on_disable() -> None
        Called when enabled is set to False

    on_destroy() -> None
        Called when this Entity is destroyed

    """

    default_counter_value: int = 30

    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text: str = kwargs["text"]
        self.pos: urs.Vec3 = kwargs["pos"]
        self.counter: int = TempMessage.default_counter_value
        self.counter_reset: int = TempMessage.default_counter_value
        if kwargs.get("counter") is not None:
            self.counter = kwargs["counter"]
            self.counter_reset = kwargs["counter"]

        super().__init__()

        self.shader = shd.unlit_shader
        self.unlit = True

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

        self.temp_text: BlobText = BlobText(
            font=DISPLAY_FONT,
            size=(STAT_FONT_SIZE / 100),
            resolution=100 * (STAT_FONT_SIZE / 100),
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=True,
            origin=(0, 0, 0),
            eternal=True,
        )

        self.position = urs.Vec3(0, 0, 0)

        self.set_text(self.text, self.pos)

    def set_text(self: Self, text: str, pos: urs.Vec3) -> None:
        """Set the text to be displayed, and its position"""
        self.temp_text.text = text
        self.update_text_pos(pos)
        self.temp_text.create_background(
            self.temp_text.size * 1.5,
            self.temp_text.size,
            urs.color.rgb32(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

    def get_text(self: Self) -> str:
        """Returns the text set as the display text"""
        return self.temp_text.text

    def update_text_pos(self: Self, pos: urs.Vec3) -> None:
        """Updates the position the text will be displayed at"""
        self.pos = pos

        self.temp_text.position = pos

        FontUtils.position_text(self.pos[0], self.pos[2], self.temp_text)

    def reset_counter(self: Self) -> None:
        """Reset the counter back to its starting point"""
        self.counter = self.counter_reset
        self.temp_text.enabled = True
        self.enabled = True

    def update(self: Self) -> None:
        """Called by Ursina, once per frame"""
        self.counter -= 1
        if self.counter <= 0:
            self.temp_text.enabled = False
            self.enabled = False

    def on_disable(self: Self) -> None:
        """Called when enabled is set to False"""
        self.counter = 0
        self.temp_text.enabled = False

    def on_destroy(self: Self) -> None:
        """Called when this Entity is destroyed"""
        self.counter = 0
        self.temp_text.enabled = False
        # urs.destroy(self.temp_text)
        self.enabled = False
        self.temp_text = None


class StatText(urs.Entity):
    """
    A class for displaying information on the four corners of the screen


    Attributes
    ----------
    **kwargs
        Specifics of this class: text (the text to be displayed), pos (the x/z position of
        the text in urs.Vec2 format), orientation (two of the TEXT_* class vars of
        this class, in tuple format)

    Methods
    -------
    set_text(text: str, pos: urs.Vec2, orientation: Tuple[int, int]) -> None
        Sets the text, position, and orientation to be displayed

    get_text() -> str
        Returns the text to be displayed

    update_text_pos(pos: urs.Vec2, orientation: Tuple[int, int]) -> None
        Updates the position and orientation of the displayed text

    on_disable() -> None
        Called when enabled is set to False

    on_destroy() -> None
        Called when destroyed

    """

    TEXT_LEFT: ClassVar[int] = 1
    TEXT_RIGHT: ClassVar[int] = 2
    TEXT_TOP: ClassVar[int] = 3
    TEXT_TOP_PLUS: ClassVar[int] = 4
    TEXT_BOTTOM: ClassVar[int] = 5
    TEXT_CENTER_x: ClassVar[int] = 6
    TEXT_CENTER_z: ClassVar[int] = 7

    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text: str = kwargs["text"]
        self.pos: urs.Vec3 = kwargs["pos"]
        self.orientation: Tuple[int, int] = kwargs["orientation"]
        self.text_size: float = STAT_FONT_SIZE / 100

        super().__init__()

        self.shader = shd.unlit_shader
        self.unlit = True

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

        if self.orientation[1] == StatText.TEXT_TOP_PLUS:
            self.text_size *= 0.75

        self.stat_text = BlobText(
            font=DISPLAY_FONT,
            size=self.text_size,
            resolution=100 * self.text_size,
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=True,
            origin=(-0.5, 0, -0.5),
            eternal=True,
        )

        self.set_text(self.text, self.pos, self.orientation)

    def set_text(
        self: Self, text: str, pos: urs.Vec3, orientation: Tuple[int, int]
    ) -> None:
        """Sets the text, position, and orientation to be displayed"""

        self.stat_text.text = text
        self.update_text_pos(pos, orientation)
        self.stat_text.create_background(
            self.stat_text.size * 0.5,
            self.stat_text.size * 0.75,
            urs.color.rgb32(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

    def get_text(self: Self) -> str:
        """Returns the text to be displayed"""
        return self.stat_text.text

    def update_text_pos(
        self: Self, pos: urs.Vec3, orientation: Tuple[int, int]
    ) -> None:
        """Updates the position and orientation of the displayed text"""

        self.pos = pos
        self.orientation = orientation

        if self.orientation[0] == StatText.TEXT_RIGHT:
            self.stat_text.origin = (0.5, 0, self.stat_text.origin[1])
        elif self.orientation[0] == StatText.TEXT_CENTER_x:
            self.stat_text.origin = (0, 0, self.stat_text.origin[1])

        if self.orientation[1] == StatText.TEXT_TOP:
            self.stat_text.origin = (self.stat_text.origin[0], 0, 0.5)
        elif self.orientation[1] == StatText.TEXT_CENTER_z:
            self.stat_text.origin = (self.stat_text.origin[0], 0, 0)
        elif self.orientation[1] == StatText.TEXT_TOP_PLUS:
            self.stat_text.origin = (self.stat_text.origin[0], 0, 0.5)
            self.pos = (self.pos[0], 0, self.pos[2] - (self.stat_text.height * 100))

        FontUtils.position_text(self.pos[0], self.pos[2], self.stat_text)

    def on_disable(self: Self) -> None:
        """Called when enabled is set to False"""
        self.stat_text.enabled = False

    def on_destroy(self: Self) -> None:
        """Called when destroyed"""
        self.stat_text.enabled = False
        # urs.destroy(self.temp_text)
        self.enabled = False
        self.stat_text = None


class EventQueue(urs.Entity):
    """
    A class the captures and stores  (in a queue) keyboard
    events triggered through Ursina


    Attributes
    ----------
    **kwargs standard urs.Entity args

    Methods
    -------
    input(key: str) -> None
        Method that capture the events (called by Ursina)

    """

    def __init__(self: Self, **kwargs):
        super().__init__()

        self.shader = shd.unlit_shader
        self.unlit = True

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

        self.input_queue: deque[str] = deque([])

    def input(self: Self, key: str) -> None:
        """Method that capture the events (called by Ursina)"""
        self.input_queue.append(key)
