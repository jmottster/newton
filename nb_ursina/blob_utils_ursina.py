"""
Newton's Laws, a simulator of physics at the scale of space

A collection of utility classes

by Jason Mott, copyright 2024
"""

from typing import ClassVar, Self, Tuple
from collections import deque

from panda3d.core import ClockObject  # type: ignore
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs.resources import resource_path


class FontUtils:
    """
    Static class for repetitive tasks related to setting up text for display

    Methods
    -------
    get_text_parent() -> urs.Entity
        Get the shared parent Entity which is the display field

    position_text(x: float, y: float, text_entity: urs.Text) -> None
        Apply standard fixes to x/y positioning for text

    """

    font_overlay: urs.Entity = None

    @staticmethod
    def get_text_parent() -> urs.Entity:
        """Get the shared parent Entity which is the display field"""
        if FontUtils.font_overlay is None:
            FontUtils.font_overlay = urs.Entity(
                parent=urs.camera.ui, x=-0.9, y=-0.5, scale=1, eternal=True
            )
        return FontUtils.font_overlay

    @staticmethod
    def position_text(x: float, y: float, text_entity: urs.Text) -> None:
        """Apply standard fixes to x/y positioning for text"""
        aspect_ratio = urs.window.aspect_ratio
        height = urs.window.size[1]
        if urs.window.fullscreen:
            aspect_ratio = (
                urs.window.main_monitor.width / urs.window.main_monitor.height
            )
            height = urs.window.main_monitor.height
        x = (x * aspect_ratio) / urs.window.size[0]
        y = 1 - (y / height)

        text_entity.position = (x, y)


class FPS:
    """
    An encapsulation of the fps clock, with display output functionality added

    Methods
    -------
    render(x: float, y: float) -> None
        Renders the fps to the display object at x,y coordinates
    """

    paused: bool = False

    def __init__(self: Self):
        class Clock:
            def __init__(self: Self):
                self.frame_rate: float = float(FRAME_RATE)
                self.globalClock = ClockObject.getGlobalClock()
                self.globalClock.setMode(ClockObject.MLimited)
                self.globalClock.setFrameRate(self.frame_rate + 10)
                if CLOCK_FPS:
                    self.globalClock.setAverageFrameRateInterval(4)
                else:
                    self.globalClock.setAverageFrameRateInterval(0)
                self.dt: float = 1 / self.frame_rate  # self.globalClock.getDt()

            def tick(self: Self, time: float):
                if time != self.frame_rate:
                    self.frame_rate = time
                    self.globalClock.setFrameRate(time)

                self.dt = 1 / self.frame_rate  # self.globalClock.getDt()

            def getAverageFrameRate(self: Self):
                return self.globalClock.getAverageFrameRate()

        self.clock: Clock = Clock()
        self.font = DISPLAY_FONT
        self.font_size = STAT_FONT_SIZE / 100

        self.text = urs.Text(
            font=self.font,
            size=self.font_size,
            resolution=100 * self.font_size,
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=False,
            origin=(-0.5, -0.5),
            eternal=True,
        )

    def render(self: Self, x: float, y: float) -> None:
        """Renders the fps to the display object at x,y coordinates"""

        self.text.text = f"FPS {round(self.clock.getAverageFrameRate(),2)}"

        FontUtils.position_text(x, y - (self.text.height * 100), self.text)

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

    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text: str = kwargs["text"]
        self.pos: urs.Vec2 = kwargs["pos"]
        self.counter: int = 30
        if kwargs.get("counter") is not None:
            self.counter = kwargs["counter"]

        super().__init__()
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

        self.temp_text: urs.Text = urs.Text(
            font=DISPLAY_FONT,
            size=(STAT_FONT_SIZE / 100),
            resolution=100 * (STAT_FONT_SIZE / 100),
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=True,
            origin=(0, 0),
            eternal=True,
        )

        self.position = urs.Vec2(0, 0)

        self.set_text(self.text, self.pos)

    def set_text(self: Self, text: str, pos: urs.Vec2) -> None:
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

    def update_text_pos(self: Self, pos: urs.Vec2) -> None:
        """Updates the position the text will be displayed at"""
        self.pos = pos

        FontUtils.position_text(self.pos[0], self.pos[1], self.temp_text)

    def reset_counter(self: Self) -> None:
        """Reset the counter back to its starting point"""
        self.counter = 30
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
    TEXT_CENTER_y: ClassVar[int] = 7

    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text: str = kwargs["text"]
        self.pos: urs.Vec2 = kwargs["pos"]
        self.orientation: Tuple[int, int] = kwargs["orientation"]

        super().__init__()
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

        self.stat_text = urs.Text(
            font=DISPLAY_FONT,
            size=(STAT_FONT_SIZE / 100),
            resolution=100 * (STAT_FONT_SIZE / 100),
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb32(255, 255, 255),
            enabled=True,
            origin=(-0.5, -0.5),
            eternal=True,
        )

        self.set_text(self.text, self.pos, self.orientation)

    def set_text(
        self: Self, text: str, pos: urs.Vec2, orientation: Tuple[int, int]
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
        self: Self, pos: urs.Vec2, orientation: Tuple[int, int]
    ) -> None:
        """Updates the position and orientation of the displayed text"""

        self.pos = pos
        self.orientation = orientation

        if self.orientation[0] == StatText.TEXT_RIGHT:
            self.stat_text.origin = (0.5, self.stat_text.origin[1])
        elif self.orientation[0] == StatText.TEXT_CENTER_x:
            self.stat_text.origin = (0, self.stat_text.origin[1])

        if self.orientation[1] == StatText.TEXT_TOP:
            self.stat_text.origin = (self.stat_text.origin[0], 0.5)
        elif self.orientation[1] == StatText.TEXT_CENTER_y:
            self.stat_text.origin = (self.stat_text.origin[0], 0)
        elif self.orientation[1] == StatText.TEXT_TOP_PLUS:
            self.stat_text.origin = (self.stat_text.origin[0], 0.5)
            self.pos = (self.pos[0], self.pos[1] + (self.stat_text.height * 100))

        FontUtils.position_text(self.pos[0], self.pos[1], self.stat_text)

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
