from typing import ClassVar, Tuple, Self, cast
from collections import deque

from panda3d.core import ClockObject  # type: ignore
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs.resources import relative_resource_path_str
from newtons_blobs.blob_universe import BlobUniverse
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_first_person_ursina import BlobFirstPersonUrsina


class FontUtils:

    font_overlay: urs.Entity = None

    @staticmethod
    def get_text_parent() -> urs.Entity:
        if FontUtils.font_overlay is None:
            FontUtils.font_overlay = urs.Entity(
                parent=urs.camera.ui, x=-0.9, y=-0.5, scale=1, eternal=True
            )
        return FontUtils.font_overlay

    @staticmethod
    def position_text(x: float, y: float, text_entity: urs.Text) -> None:
        x = (x * urs.window.aspect_ratio) / urs.window.size[0]
        y = 1 - (y / urs.window.size[1])

        text_entity.position = (x, y)


class FPS:
    """
    An encapsulation of the fps clock, with display output functionality added

    Attributes
    ----------

    Methods
    -------
    render(x: float, y: float) -> None
        Renders the fps to the display object at x,y coordinates
    """

    def __init__(self: Self):
        class Clock:
            def __init__(self: Self):
                self.frame_rate: float = float(FRAME_RATE)
                self.globalClock = ClockObject.getGlobalClock()
                self.globalClock.setMode(ClockObject.MLimited)
                self.globalClock.setFrameRate(self.frame_rate)
                self.globalClock.setAverageFrameRateInterval(4)

            def tick(self: Self, time: float):
                if time != self.frame_rate:
                    self.frame_rate = time
                    self.globalClock.setFrameRate(time)

            def getAverageFrameRate(self: Self):
                return self.globalClock.getAverageFrameRate()

        self.clock: Clock = Clock()
        self.font = relative_resource_path_str(str(DISPLAY_FONT), "")
        self.font_size = STAT_FONT_SIZE / 100

        self.text = urs.Text(
            font=self.font,
            size=self.font_size,
            resolution=100 * self.font_size,
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb(255, 255, 255),
            enabled=False,
            origin=(-0.5, -0.5),
            eternal=True,
        )

    def render(self: Self, x: float, y: float) -> None:
        """Renders the fps to the display object at x,y coordinates"""

        self.text.text = f"FPS {round(self.clock.getAverageFrameRate(),2)}"

        FontUtils.position_text(x, y, self.text)

        self.text.create_background(
            self.text.size * 0.3,
            self.text.size * 0.5,
            urs.color.rgb(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

        if not self.text.enabled:
            self.text.enabled = True


class TempMessage(urs.Entity):
    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text = kwargs["text"]
        self.pos = kwargs["pos"]

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

        self.temp_text = urs.Text(
            font=relative_resource_path_str(str(DISPLAY_FONT), ""),
            size=(STAT_FONT_SIZE / 100),
            resolution=100 * (STAT_FONT_SIZE / 100),
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb(255, 255, 255),
            enabled=True,
            origin=(0, 0),
            eternal=True,
        )

        self.position = (0, 0)

        self.set_text(self.text, self.pos)

        self.counter = 30

    def set_text(self, text, pos):
        self.temp_text.text = text
        self.update_text_pos(pos)
        self.temp_text.create_background(
            self.temp_text.size * 1.5,
            self.temp_text.size,
            urs.color.rgb(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

    def get_text(self):
        return self.temp_text.text

    def update_text_pos(self, pos):
        self.pos = pos

        FontUtils.position_text(self.pos[0], self.pos[1], self.temp_text)

    def reset_counter(self):
        self.counter = 30
        self.temp_text.enabled = True
        self.enabled = True

    def update(self: Self):
        self.counter -= 1
        if self.counter <= 0:
            self.temp_text.enabled = False
            self.enabled = False

    def on_disable(self: Self):
        self.counter = 0
        self.temp_text.enabled = False

    def on_destroy(self: Self):
        self.counter = 0
        self.temp_text.enabled = False
        # urs.destroy(self.temp_text)
        self.enabled = False
        self.temp_text = None


class StatText(urs.Entity):

    TEXT_LEFT: ClassVar[int] = 1
    TEXT_RIGHT: ClassVar[int] = 2
    TEXT_TOP: ClassVar[int] = 3
    TEXT_TOP_PLUS: ClassVar[int] = 4
    TEXT_BOTTOM: ClassVar[int] = 5
    TEXT_CENTER_x: ClassVar[int] = 6
    TEXT_CENTER_y: ClassVar[int] = 7

    def __init__(self: Self, **kwargs):
        kwargs["eternal"] = True

        self.text = kwargs["text"]
        self.pos = kwargs["pos"]
        self.orientation = kwargs["orientation"]

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
            font=relative_resource_path_str(str(DISPLAY_FONT), ""),
            size=(STAT_FONT_SIZE / 100),
            resolution=100 * (STAT_FONT_SIZE / 100),
            parent=FontUtils.get_text_parent(),
            scale=0.1,
            color=urs.color.rgb(255, 255, 255),
            enabled=True,
            origin=(-0.5, -0.5),
            eternal=True,
        )

        self.set_text(self.text, self.pos, self.orientation)

    def set_text(self, text, pos, orientation):
        self.stat_text.text = text
        self.update_text_pos(pos, orientation)
        self.stat_text.create_background(
            self.stat_text.size * 0.5,
            self.stat_text.size * 0.75,
            urs.color.rgb(
                BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
            ),
        )

    def get_text(self):
        return self.stat_text.text

    def update_text_pos(self, pos, orientation):

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

    def on_disable(self: Self):
        self.stat_text.enabled = False

    def on_destroy(self: Self):
        self.stat_text.enabled = False
        # urs.destroy(self.temp_text)
        self.enabled = False
        self.stat_text = None


class EventQueue(urs.Entity):

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

    def input(self: Self, key: str):
        self.input_queue.append(key)


class FirstPersonSurface:

    def __init__(
        self: Self,
        radius: float,
        color: Tuple[int, int, int],
        universe: BlobUniverse,
        texture: str = None,
        rotation_speed: float = None,
        rotation_pos: Tuple[int, int, int] = None,
    ):
        self.universe: BlobUniverseUrsina = cast(BlobUniverseUrsina, universe)
        self.first_person_viewer: BlobFirstPersonUrsina = BlobFirstPersonUrsina(
            scale=CENTER_BLOB_RADIUS / 5,
            universe=self.universe,
            start_z=radius,
            eternal=True,
            mass=MIN_MASS,
        )
        self.radius = radius
        self.color = color

    def get_position(self: Self) -> urs.Vec3:
        return self.first_person_viewer.position

    def resize(self: Self, radius: float) -> None:
        pass

    def update_center_blob(self: Self, x: float, y: float, z: float) -> None:
        pass

    def draw(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        self.first_person_viewer.position = urs.Vec3(pos)

    def draw_as_center_blob(
        self: Self, pos: Tuple[float, float, float] = None, lighting: bool = True
    ) -> None:
        pass

    def destroy(self: Self) -> None:
        if self.first_person_viewer is not None:
            self.first_person_viewer.enabled = False
