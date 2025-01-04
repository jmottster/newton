"""
Newton's Laws, a simulator of physics at the scale of space

Class to represent an object that holds and controls a drawing area intended for screen display

by Jason Mott, copyright 2024
"""

from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, Tuple, Self

from panda3d.core import loadPrcFileData  # type: ignore

from direct.filter.CommonFilters import CommonFilters  # type: ignore

from direct.showbase import DirectObject  # type: ignore
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from newtons_blobs import BlobUniverse
from newtons_blobs import BlobDisplay

from .blob_utils_ursina import *
from .blob_first_person_surface import FirstPersonSurface
from .fps import FPS


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class WindowHandler(DirectObject.DirectObject):
    """
    A class to catch window events from the Panda3D event handler. This is to maintain
    a consistent view by adjusting FOV according to the window width. (So the image
    doesn't scale with window size)

    Methods
    -------
    possible_resize(self: Self, arg: str) -> None
        Implementation of event call back (set up in __init__ via self.accept("window-event", self.possible_resize)
        See  direct.showbase.DirectObject from Panda3D API). This will adjust FOV if the window has changed size.

    """

    def __init__(self: Self, last_size: urs.Vec2, display: "BlobDisplayUrsina"):
        self.last_size: urs.Vec2 = last_size
        self.accept("window-event", self.possible_resize)
        self.display = display
        self.orig_fov: float = 90.0
        urs.camera.fov = self.orig_fov

    def possible_resize(self: Self, arg: Any) -> None:
        """
        Implementation of event call back (set up in __init__ via self.accept("window-event", self.possible_resize)
        See  direct.showbase.DirectObject from Panda3D API). This will adjust FOV if the window has changed size.
        """

        if (
            urs.window.size[0] != self.last_size[0]
            or urs.window.size[1] != self.last_size[1]
        ):
            pos_lock = urs.mouse.locked

            if pos_lock:
                self.display.first_person_surface.first_person_viewer.pos_lock()
            urs.camera.fov = urs.camera.fov * (urs.window.size[0] / self.last_size[0])

            if urs.window.fullscreen:
                self.display.width = urs.window.main_monitor.width
                self.display.height = urs.window.main_monitor.height
            else:
                self.display.width = urs.window.size[0]
                self.display.height = urs.window.size[1]

            self.last_size = urs.window.size

            for _, item in self.display.text_entity_cache.items():
                item.enabled = False
                urs.destroy(item)
            self.display.text_entity_cache.clear()
            if pos_lock:
                self.display.first_person_surface.first_person_viewer.pos_unlock()

        if not urs.window.fullscreen:
            urs.window.windowed_size = arg.getProperties().getSize()
            urs.window.windowed_position = arg.getProperties().getOrigin()
            urs.window.setOrigin(arg.getProperties().getOrigin())
            urs.window.setSize(arg.getProperties().getSize())
            try:
                urs.camera.set_shader_input(
                    "window_size", arg.getProperties().getSize()
                )
            except:
                pass  # not initialized yet


class BlobDisplayUrsina:
    """
    Class to represent an object that holds and controls a drawing
    area intended for screen display (the viewable area of the Universe object)

    Attributes
    ----------
    size_w: float
        The desired width of the display in pixels
    size_h: float
        The desired height of the display in pixels

    Methods
    -------

    load_key_ints() -> Dict[str, int]
        Loads up the Dict that holds integers that represent keys. (see get_key_code)

    load_keyboard_events() -> Dict[int, Callable[[], None]]
        Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict

    clear_stats() -> None
        Clears the cache that holds stat entities

    get_framework() -> Any
        Returns the underlying framework implementation of the drawing area for display, mostly for use
        in an implementation of BlobSurface within the same framework for direct access

    get_windowed_width() -> float
        Returns the default width of the non-fullscreen display object

    get_windowed_height() -> float
        Returns the default height of the non-fullscreen display object

    get_width() -> float
        Returns the current width of the display object

    get_height() -> float
        Returns the current height of the display object

    get_key_code(key: str) -> int
        Returns the key code of the provided character (keyboard character). For use in creating a dict that
        holds function references in a dict

    check_events(keyboard_events: Dict[int, Callable[[], None]]) -> None
        Send a dict that has codes from get_key_codes (i.e. keyboard key codes) as the keys (i.e. dict keys),
        and something to do upon that key being pressed.
        This is presumed to be used for each iteration of a frame before drawing.

    fps_clock_tick(fps: int) -> None
        Control the FPS rate by sending the desired rate here every frame of while loop

    fps_get_dt() -> float
        Returns the elapsed time for the previous frame in seconds

    fps_render(pos: Tuple[float, float]) -> None
        Will print the current achieved rate on the screen

    set_mode(size: Tuple[float, float], mode: int) -> None
        Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)

    is_fullscreen() -> bool:
        Whether or not the display is in fullscreen mode (False if in windowed mode)

    fill(color: Tuple[int, int, int]) -> None
        Fill the entire area wit a particular color to prepare for drawing another screen

    temp_message(text: str, pos: Tuple[float, float], msg_key: str) -> None
        Sends the given message to the center of the screen for 30 seconds

    blit_text(text: str, pos: Tuple[float, float], orientation: Tuple[int, int]) -> None
        Print the proved text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)

    draw_universe(universe: BlobUniverse) -> None
        Draw the universe area inside the display area (note that universe may be larger than display)

    update() -> None
        Draw the prepared frame to the screen/window

    quit() -> None
        Exit the application

    """

    FULLSCREEN: ClassVar[int] = 1
    RESIZABLE: ClassVar[int] = 2

    filters: CommonFilters = None

    def __init__(self: Self, size_w: float, size_h: float):

        urs.application.asset_folder = Path(__file__).parent
        urs.application.compressed_textures_folder = (
            urs.application.asset_folder.joinpath("textures").joinpath(
                "textures_compressed/"
            )
        )
        urs.application.compressed_models_folder = (
            urs.application.asset_folder.joinpath("models").joinpath(
                "models_compressed/"
            )
        )

        # Uncomment only if you're having trouble starting in fullscreen (virtual machine issue)
        # loadPrcFileData("", "fullscreen #t")
        # loadPrcFileData("", "framebuffer-multisample 1")
        # loadPrcFileData("", "multisamples 4")

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

        loadPrcFileData("", "coordinate-system z-up-right")

        urs.camera.ui = urs.Entity(
            eternal=True,
            name="ui",
            scale=(urs.camera.ui_size * 0.5, 0.5, urs.camera.ui_size * 0.5),
            add_to_scene_entities=False,
        )
        urs.camera.overlay = urs.Entity(
            parent=urs.camera.ui,
            model="quad",
            scale=99,
            color=urs.color.clear,
            eternal=True,
            y=-99,
            add_to_scene_entities=False,
        )

        urs.camera.set_up()
        urs.camera.fov = 90

        urs.window.color = urs.color.rgb32(
            BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]
        )

        BlobDisplayUrsina.filters = CommonFilters(
            urs.application.base.win, urs.application.base.cam
        )

        BlobDisplayUrsina.filters.setMSAA(4)

        BlobDisplayUrsina.filters.setHighDynamicRange()
        BlobDisplayUrsina.filters.setExposureAdjust(0.8)

        BlobDisplayUrsina.filters.setBloom(
            blend=(1, 1, 1, 1),
            mintrigger=3.3,
            maxtrigger=10,
            size="large",
            intensity=10,
            desat=0,
        )

        self.first_person_surface: FirstPersonSurface = None  # set by BlobUrsinaFactory

        self.windowed_width: float = size_w
        self.windowed_height: float = size_h

        self.width: float = urs.window.main_monitor.width
        self.height: float = urs.window.main_monitor.height

        if not urs.window.fullscreen:
            self.width = urs.window.size[0]
            self.height = urs.window.size[1]

        self.modes: Dict[int, int] = {
            BlobDisplay.FULLSCREEN: True,
            BlobDisplay.RESIZABLE: False,
        }

        self.h: WindowHandler = WindowHandler(urs.window.size, self)

        self.paused: bool = False
        self.show_stats: bool = True
        self.entity_follow: bool = False

        self.event_queue: EventQueue = EventQueue(eternal=True)

        self.fps: FPS = FPS()

        self.fps_display: FPSDisplay = None
        self.text_entity_cache: Dict[str, BlobText] = {}

        self.key_ints: Dict[str, int] = self.load_key_ints()

        self.urs_keyboard_events: Dict[int, Callable[[], None]] = (
            self.load_keyboard_events()
        )

    def load_key_ints(self: Self) -> Dict[str, int]:
        """Loads up the Dict that holds integers that represent keys. (see get_key_code)"""
        mykeys = tuple("abcdefghijklmnopqrstuvwxyz1234567890")
        morekeys = ("escape", "space", "up arrow", "down arrow", "right mouse down")

        key_ints: Dict[str, int] = {}
        i = 0
        for key in mykeys:
            key_ints[key] = i
            i += 1
        for key in morekeys:
            key_ints[key] = i
            i += 1

        return key_ints

    def load_keyboard_events(self: Self) -> Dict[int, Callable[[], None]]:
        """
        Creates and populates a dict that holds function references for keyboard events (also creates the functions),
        returns the dict
        """
        keyboard_events: Dict[int, Callable[[], None]] = {}

        def pause_game() -> None:
            self.paused = not self.paused
            if self.paused:
                FPS.paused = self.paused
            else:
                FPS.paused = self.paused

        def toggle_stats() -> None:
            self.show_stats = not self.show_stats

            if not self.show_stats:
                self.clear_stats()

        def toggle_entity_follow() -> None:
            if self.paused:
                self.entity_follow = not self.entity_follow
                if self.entity_follow and urs.mouse.hovered_entity is not None:
                    self.first_person_surface.first_person_viewer.start_following(
                        urs.mouse.hovered_entity
                    )
                else:
                    self.entity_follow = False
                    self.first_person_surface.first_person_viewer.stop_following()
            else:
                self.entity_follow = False
                self.first_person_surface.first_person_viewer.stop_following()

        keyboard_events[self.get_key_code("space")] = pause_game
        keyboard_events[self.get_key_code("2")] = toggle_stats
        keyboard_events[self.get_key_code("right mouse down")] = toggle_entity_follow

        return keyboard_events

    def clear_stats(self: Self) -> None:
        """Clears the cache that holds stat entities"""
        for _, item in self.text_entity_cache.items():
            item.enabled = False
            urs.destroy(item)
        self.text_entity_cache.clear()

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

        try:
            return self.key_ints[key]
        except:
            return -1

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
            if self.key_ints.get(key) is not None:
                if keyboard_events.get(self.key_ints[key]) is not None:
                    keyboard_events[self.key_ints[key]]()
                if self.urs_keyboard_events.get(self.key_ints[key]) is not None:
                    self.urs_keyboard_events[self.key_ints[key]]()

    def fps_clock_tick(self: Self, fps: int) -> None:
        """Control the FPS rate by sending the desired rate here every frame of while loop"""
        self.fps.clock.tick(fps)

    def fps_get_dt(self: Self) -> float:
        """Returns the elapsed time for the previous frame in seconds"""
        return self.fps.clock.dt

    def fps_render(self: Self, pos: Tuple[float, float]) -> None:
        """Will print the current achieved rate on the screen"""

        if self.fps_display is None:
            self.fps_display = FPSDisplay()
        self.fps_display.render(self.fps, pos[0], pos[1])

    def set_mode(self: Self, size: Tuple[float, float], mode: int) -> None:
        """Sets the screen size and window mode (BlobDisplay.FULLSCREEN or BlobDisplay.RESIZABLE)"""

        pos_lock = urs.mouse.locked

        if pos_lock:
            self.first_person_surface.first_person_viewer.pos_lock()
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
            self.windowed_width = size[0]
            self.windowed_height = size[1]

        if pos_lock:
            self.first_person_surface.first_person_viewer.pos_unlock()

        self.update()

    def is_fullscreen(self: Self) -> bool:
        """Whether or not the display is in fullscreen mode (False if in windowed mode)"""
        return urs.window.fullscreen

    def fill(self: Self, color: Tuple[int, int, int]) -> None:
        """Fill the entire area wit a particular color to prepare for drawing another screen"""
        pass

    def temp_message(
        self: Self, text: str, pos: Tuple[float, float], msg_key: str
    ) -> None:
        """Sends the given message to the center of the screen for 30 seconds"""

        text_entity = self.text_entity_cache.get(msg_key)
        if text_entity is None:
            self.text_entity_cache[msg_key] = TempMessage(text=text, pos=pos)
            text_entity = self.text_entity_cache.get(msg_key)
            text_entity.set_text(text, pos)

        if text_entity.get_text() != text:
            text_entity.set_text(text, pos)

        text_entity.reset_counter()

    def blit_text(
        self: Self, text: str, in_pos: Tuple[float, float], orientation: Tuple[int, int]
    ) -> None:
        """
        Print the provided text to the screen a the provided coordinates. orientation helps to give hints
        on how to offset the size of the text itself (so, for example, it doesn't go offscreen). Use the
        class vars for x/y orientation hints, e.g. (BlobDisplay.TEXT_LEFT, BlobDisplay.TEXT_BOTTOM)
        """

        pos: urs.Vec3 = urs.Vec3(in_pos[0], 0, in_pos[1])

        if orientation == (BlobDisplay.TEXT_CENTER_x, BlobDisplay.TEXT_CENTER_z):
            self.temp_message(
                text, pos, f"{BlobDisplay.TEXT_CENTER_x}{BlobDisplay.TEXT_CENTER_z}"
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
        pass

    def update(self: Self) -> None:
        """Draw the prepared frame to the screen/window"""
        self.app.step()

    def quit(self: Self) -> None:
        """Exit the application"""
        urs.application.quit()
