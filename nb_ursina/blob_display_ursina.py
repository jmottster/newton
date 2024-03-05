"""
Newton's Laws, a simulator of physics at the scale of space

Protocol class to represent an object that holds and controls a drawing area intended for screen display

by Jason Mott, copyright 2024
"""

from typing import Any, Callable, ClassVar, Dict, Tuple, Self, cast

from direct.showbase import DirectObject  # type: ignore
import ursina as urs  # type: ignore

from newtons_blobs.resources import resource_path
from newtons_blobs.globals import *
from newtons_blobs.blob_universe import BlobUniverse
from newtons_blobs.blob_display import BlobDisplay
from .blob_utils_ursina import *
from .blob_first_person_surface import FirstPersonSurface


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class WindowHandler(DirectObject.DirectObject):
    def __init__(self: Self, last_size: urs.Vec2, display: "BlobDisplayUrsina"):
        self.last_size: urs.Vec2 = last_size
        self.accept("window-event", self.possible_resize)
        self.display = display
        self.orig_fov: float = 90.0
        urs.camera.fov = self.orig_fov

    def possible_resize(self, arg):

        if urs.window.size[0] != self.last_size[0]:
            urs.camera.fov = urs.camera.fov * (urs.window.size[0] / self.last_size[0])
            self.display.width = urs.window.size[0]
            self.display.height = urs.window.size[1]
            self.last_size = urs.window.size
            for _, item in self.display.text_entity_cache.items():
                item.enabled = False
                urs.destroy(item)

            self.display.text_entity_cache.clear()


class BlobDisplayUrsina:
    """
    Protocol class to represent an object that holds and controls a drawing
    area intended for screen display (the viewable area of the Universe object)

    Attributes
    ----------
    size_w: float
        The desired width of the display in pixels
    size_h: float
        The desired height of the display in pixels

    Methods
    -------
    get_framework(self: Self) -> Any
        Returns the underlying framework implementation of the drawing area for display, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_windowed_width() -> float
        Returns the default width of the non-fullscreen display object

    get_windowed_height() -> float
        Returns the default height of the non-fullscreen display object

    get_width(self: Self) -> float
        Returns the current width of the display object

    get_height(self: Self) -> float
        Returns the current height of the display object

    get_key_code(self: Self, key: str) -> int
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict

    check_events(self: Self, keyboard_events: Dict[int, Callable[[], None]]) -> None
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.

    fps_clock_tick(self: Self, fps: int) -> None
        Control the FPS rate by sending the desired rate here every frame of while loop

    fps_render(self: Self, pos: Tuple[float, float]) -> None
        Will print the current achieved rate on the screen

    set_mode(size: Tuple[float, float], mode: int) -> None
        Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)

    is_fullscreen() -> bool:
        Whether of not the display is in fullscreen mode (False if in windowed mode)

    fill(self: Self, color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    blit_text(self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]) -> None
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)

    draw_universe(self: Self, universe: BlobUniverse) -> None
        Draw the universe area inside the display area (note that universe may be larger than display)

    update(self: Self) -> None
        Draw the prepared frame to the screen/window

    quit(self: Self) -> None
        Exit the application

    """

    FULLSCREEN: ClassVar[int] = 1
    RESIZABLE: ClassVar[int] = 2

    size_w: float
    size_h: float

    def __init__(self: Self, size_w: float, size_h: float):

        self.paused = False
        self.show_stats = True

        self.windowed_width = size_w
        self.windowed_height = size_h

        self.app: urs.Ursina = urs.Ursina(
            title=WINDOW_TITLE,
            icon=WINDOW_ICON,
            borderless=False,
            fullscreen=True,
            editor_ui_enabled=False,
            development_mode=False,
            exit_button=False,
            cog_menu=False,
        )

        # urs.forced_aspect_ratio = (
        #     urs.window.main_monitor.width / urs.window.main_monitor.height
        # )

        urs.window.color = urs.color.rgb(
            BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
        )
        # urs.window.fullscreen = True
        # urs.window.position = urs.Vec2(50, 70)
        # urs.window.size = urs.Vec2(
        #     urs.window.main_monitor.width, urs.window.main_monitor.height
        # )

        self.event_queue: EventQueue = EventQueue(eternal=True)

        self.first_person_surface: FirstPersonSurface = None  # set by BlobUrsinaFactory

        self.fps: FPS = FPS()

        # self.font_overlay = urs.Entity(parent=urs.camera.ui, scale=1, x=-1, y=1)
        self.modes: Dict[int, int] = {
            BlobDisplay.FULLSCREEN: True,
            BlobDisplay.RESIZABLE: False,
        }

        self.text_entity_cache: Dict[str, urs.Text] = {}
        self.h = WindowHandler(urs.window.size, self)

        mykeys = tuple("abcdefghijklmnopqrstuvwxyz1234567890")
        morekeys = ("escape", "space")

        self.key_ints: Dict[str, int] = {}
        i = 0
        for key in mykeys:
            self.key_ints[key] = i
            i += 1
        for key in morekeys:
            self.key_ints[key] = i
            i += 1

        self.width = urs.window.size[0]
        self.height = urs.window.size[1]

        self.urs_keyboard_events: Dict[int, Callable[[], None]] = (
            self.load_keyboard_events()
        )

        # self.cam_pos = urs.Text(
        #     f"({self.x},{self.y},{self.z})",
        #     position=(0, 0.03, 0),
        #     parent=urs.camera.ui,
        #     origin=(0, 0),
        #     scale=0.75,
        # )
        # self.cam_pos_rot = urs.Text(
        #     f"({self.rotation_x},{self.rotation_y},{self.rotation_z})",
        #     position=(0, 0.06, 0),
        #     parent=urs.camera.ui,
        #     origin=(0, 0),
        #     scale=0.75,
        # )

        # self.cam_pos_rot.text = f"({round(self.rotation_x,2)},{round(self.rotation_y,2)},{round(self.rotation_z,2)})"
        # self.cam_pos.text = f"({round(self.position[0],2)},{round(self.position[1],2)},{round(self.position[2],2)})"

    def load_keyboard_events(self: Self) -> Dict[int, Callable[[], None]]:
        """
        Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict
        """
        keyboard_events: Dict[int, Callable[[], None]] = {}

        def pause_game() -> None:
            self.paused = not self.paused
            if self.paused:
                pass
            else:
                pass

        def toggle_stats() -> None:
            self.show_stats = not self.show_stats

            for _, item in self.text_entity_cache.items():
                item.enabled = self.show_stats
                if not self.show_stats:
                    item.enabled = False
                    urs.destroy(item)

            if not self.show_stats:
                self.text_entity_cache.clear()

        keyboard_events[self.get_key_code("space")] = pause_game
        keyboard_events[self.get_key_code("4")] = toggle_stats

        return keyboard_events

    def get_framework(self: Self) -> Any:
        """
        Returns the underlying framework implementation of the drawing area for display, mostly for use
        in an implementation of BlobSurface within the same framework for direct access
        """
        pass

    def get_windowed_width(self: Self) -> float:
        """
        Returns the default width of the non-fullscreen display object
        """
        return self.windowed_width

    def get_windowed_height(self: Self) -> float:
        """
        Returns the default height of the non-fullscreen display object
        """
        return self.windowed_height

    def get_width(self: Self) -> float:
        """
        Returns the current width of the display object
        """
        return self.width

    def get_height(self: Self) -> float:
        """
        Returns the current height of the display object
        """
        return self.height

    def get_key_code(self: Self, key: str) -> int:
        """
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict
        """
        return self.key_ints[key]

    def check_events(
        self: Self, keyboard_events: Dict[int, Callable[[], None]]
    ) -> None:
        """
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.
        """
        for _ in range(len(self.event_queue.input_queue)):
            key = self.event_queue.input_queue.popleft()
            if (
                self.key_ints.get(key) is not None
                and keyboard_events.get(self.key_ints[key]) is not None
            ):
                keyboard_events[self.key_ints[key]]()
                if self.urs_keyboard_events.get(self.key_ints[key]) is not None:
                    self.urs_keyboard_events[self.key_ints[key]]()

    def fps_clock_tick(self: Self, fps: int) -> None:
        """Control the FPS rate by sending the desired rate here every frame of while loop"""
        self.fps.clock.tick(fps)

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        """Will print the current achieved rate on the screen"""
        self.fps.render(pos[0], pos[1])

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        """Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)"""

        adjusted_height = urs.window.main_monitor.height - 70
        if adjusted_height < size[1]:
            size = (size[0], adjusted_height)

        urs.window.fullscreen = self.modes[mode]

        if not self.modes[mode]:
            urs.window.size = urs.Vec2(size[0], size[1])
            urs.window.position = urs.Vec2(
                ((urs.window.main_monitor.width - size[0]) / 2),
                ((urs.window.main_monitor.height - size[1]) / 2),
            )

    def is_fullscreen(self: Self) -> bool:
        """Whether of not the display is in fullscreen mode (False if in windowed mode)"""
        return urs.window.fullscreen

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        pass

    def temp_message(
        self: Self, text: str, pos: Tuple[float, float], msg_key: str
    ) -> None:

        text_entity = self.text_entity_cache.get(msg_key)
        if text_entity is None:
            self.text_entity_cache[msg_key] = TempMessage(text=text, pos=pos)
            text_entity = self.text_entity_cache.get(msg_key)
            text_entity.set_text(text, pos)

        if text_entity.get_text() != text:
            text_entity.set_text(text, pos)

        text_entity.reset_counter()

    def blit_text(
        self: Self, text: str, pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        # """
        # Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        # on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        # class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)
        # """

        if orientation == (BlobDisplay.TEXT_CENTER_x, BlobDisplay.TEXT_CENTER_y):
            self.temp_message(
                text, pos, f"{BlobDisplay.TEXT_CENTER_x}{BlobDisplay.TEXT_CENTER_y}"
            )
            return

        key = f"{orientation[0]}{orientation[1]}"

        text_entity_entity = self.text_entity_cache.get(key)
        if text_entity_entity is None:
            self.text_entity_cache[key] = StatText(
                text=text, pos=pos, orientation=orientation
            )

            text_entity_entity = self.text_entity_cache.get(key)
            text_entity_entity.set_text(text, pos, orientation)

        if text_entity_entity.get_text() != text:
            text_entity_entity.set_text(text, pos, orientation)

    def draw_universe(self: Self, universe: BlobUniverse) -> None:
        """Draw the universe area inside the display area (note that universe may be larger than display)"""

        if self.first_person_surface is not None:
            universe_entity = cast(urs.Entity, universe.get_framework())
            universe_entity.position = (
                self.first_person_surface.first_person_viewer.world_position
            )

    def update(self: Self) -> None:
        """Draw the prepared frame to the screen/window"""
        self.app.step()

    def quit(self: Self) -> None:
        """Exit the application"""
        urs.application.quit()
