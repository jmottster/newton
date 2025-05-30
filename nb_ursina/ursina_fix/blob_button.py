"""
Newton's Laws, a simulator of physics at the scale of space

Class to create a UI button

by Jason Mott, copyright 2025
"""

from typing import Self, Tuple

from panda3d.core import Texture  # type: ignore
import ursina as urs  # type: ignore

from newtons_blobs.globals import *
from .blob_text import BlobText
from .blob_quad import createBlobQuad, BlobQuad

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobButton(urs.Entity):
    """
    A class

    Attributes
    ----------
    text: str
        The text to be displayed on the button

    text_origin: urs.Vec3
        The position of the text relative to its center
        Set using a tuple

    text_color: urs.Color
        The color of the text to be displayed

    icon: urs.Entity
        Entity the holds the texture the gives the button an icon
        Set using string path to texture

    icon_world_scale: urs.Vec3
        The scale of the icon entity
        Set using a tuple

    text_size: float
        The size of the text to be displayed

    origin: urs.Vec3
        The position of the button relative to its center
        Set using a tuple


    Methods
    -------
    input(key: str) -> None
        Called by Ursina when there is an input event

    on_mouse_enter() -> None
        Called by Ursina when the mouse cursor is over the button

    on_mouse_exit() -> None
        Called by Ursina when the mouse cursor leaves the button area

    """

    default_color: urs.Color = urs.color.black90
    default_model: BlobQuad = None

    def __init__(
        self: Self,
        text: str = "",
        parent: urs.Entity = urs.camera.ui,
        model: BlobQuad = None,
        radius: float = 0.1,
        text_origin: Tuple[float, float, float] = (0, 0, 0),
        text_size: float = 1,
        highlight_scale: float = 1,
        pressed_scale: float = 1,
        disabled: bool = False,
        **kwargs,
    ):

        super().__init__(parent=parent)

        self.color = BlobButton.default_color

        for key in (
            "scale",
            "scale_x",
            "scale_y",
            "scale_z",
            "world_scale",
            "world_scale_x",
            "world_scale_y",
            "world_scale_z",
            "color",
        ):
            if key in kwargs:  # set the scale before model for correct corners
                setattr(self, key, kwargs[key])
                del kwargs[key]

        self.model: BlobQuad = None

        self.aspect_ratio: float = self.scale_x / self.scale_z

        if model == None:
            if not BlobButton.default_model:
                if self.scale_x != 0 and self.scale_z != 0:
                    self.model = createBlobQuad(
                        aspect=(self.scale_x / self.scale_z),
                        scale=self.scale,
                        radius=radius,
                    )
            else:
                self.model = BlobButton.default_model

        else:
            self.model = model

        self._text_size: float = 0
        self._text_origin: urs.Vec3 = None
        self.icon_entity: urs.Entity = None
        self.highlight_color: urs.Color = self.color.tint(0.2)
        self.pressed_color: urs.Color = self.color.tint(-0.2)
        self.highlight_scale: float = highlight_scale  # multiplier
        self.pressed_scale: float = pressed_scale  # multiplier
        self.highlight_sound: urs.Audio = None
        self.pressed_sound: urs.Audio = None

        self.collider = "box"
        self.origin = (0, 0, 0)
        self.disabled = disabled

        self.text_entity: BlobText = None

        self.text_origin = text_origin

        if text:
            self.text_size = text_size
            self.text = text

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
    def text(self: Self) -> str:
        """The text to be displayed on the button"""
        if self.text_entity is not None:
            return self.text_entity.text
        return ""

    @text.setter
    def text(self: Self, value: str) -> None:
        """Sets the text to be displayed on the button"""
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        if self.text_entity is None:
            self.text_entity = BlobText(
                text=value,
                parent=self.model,
                scale=self.text_size,
                position=urs.Vec3(self.text_origin[0], -0.01, self.text_origin[2]),
                origin=self.text_origin,
                add_to_scene_entities=False,
            )
            self.text_entity.world_parent = self
            self.text_entity.scale_x /= self.aspect_ratio

        else:
            self.text_entity.text = value

    @property
    def text_origin(self: Self) -> urs.Vec3:
        """The position of the text relative to its center"""
        if self.text_entity is not None:
            return self.text_entity.origin

        return getattr(self, "_text_origin", urs.Vec3(0, 0, 0))

    @text_origin.setter
    def text_origin(self: Self, value: Tuple[float, float, float]) -> None:
        """Sets the position of the text relative to its center"""
        self._text_origin = urs.Vec3(value)
        if not self.text_entity:
            return

        self.text_entity.origin = self._text_origin
        self.text_entity.world_parent = self

    @property
    def text_color(self: Self) -> urs.Color:
        """The color of the text to be displayed"""
        if self.text_entity is not None:
            return self.text_entity.color

        return None

    @text_color.setter
    def text_color(self: Self, value: urs.Color) -> None:
        """Sets the color of the text to be displayed"""
        if self.text_entity is not None:
            self.text_entity.color = value

    @property
    def icon(self: Self) -> urs.Entity:
        """Entity that holds the texture the gives the button an icon"""
        return getattr(self, "icon_entity", None)

    @icon.setter
    def icon(self: Self, value: str) -> None:
        """Creates the Entity that holds the texture the gives the button an icon"""
        if value and not hasattr(self, "icon_entity"):
            self.icon_entity = urs.Entity(
                parent=self.model,
                name=f"button_icon_entity_{value}",
                model="quad",
                y=-0.1,
                add_to_scene_entities=False,
            )
        self.icon_entity.texture = value
        texture: Texture = self.icon_entity.texture
        aspect_ratio: float = texture.width / texture.height
        if aspect_ratio == 1:
            return

        if texture.width < texture.height:
            self.icon_entity.scale_x = self.icon_entity.scale_z * aspect_ratio
        else:
            self.icon_entity.scale_z = self.icon_entity.scale_x / aspect_ratio

    @property
    def icon_world_scale(self: Self) -> urs.Vec3:
        """The scale of the icon entity"""
        if self.icon is None:
            return None
        return self.icon_entity.world_scale

    @icon_world_scale.setter
    def icon_world_scale(self: Self, value: Tuple[float, float, float]) -> None:
        """Sets the scale of the icon entity"""
        if self.icon:
            self.icon_entity.world_scale = urs.Vec3(value)

    @property
    def text_size(self: Self) -> float:
        """The size of the text to be displayed"""
        return getattr(self, "_text_size", 1)

    @text_size.setter
    def text_size(self: Self, value: float) -> None:
        """Sets the size of the text to be displayed"""
        self._text_size = value
        if self.text_entity:
            self.text_entity.scale = urs.Vec3(value)
            self.text_entity.scale_x /= self.aspect_ratio

    @property
    def origin(self: Self) -> urs.Vec3:
        """The position of the button relative to its center"""
        return getattr(self, "_origin", urs.Vec3.zero)

    @origin.setter
    def origin(self: Self, value: Tuple[float, float, float]) -> None:
        """Sets the position of the button relative to its center"""
        if hasattr(self, "text_entity") and self.text_entity:
            self.text_entity.world_parent = self.model
            super().origin_setter(urs.Vec3(value))
            self.text_entity.world_parent = self
        else:
            super().origin_setter(urs.Vec3(value))

        if isinstance(
            self.collider, urs.BoxCollider
        ):  # update collider position by making a new one
            self.collider = "box"

    def on_destroy(self: Self) -> None:
        urs.destroy(self.text_entity)

    # def input(self: Self, key: str) -> None:
    #     """Called by Ursina when there is an input event"""
    #     if self.disabled or not self.model:
    #         return

    #     if key == "left mouse down":
    #         if self.hovered:
    #             self.model.setColorScale(self.pressed_color)
    #             self.model.setScale(urs.Vec3(self.pressed_scale, 1, self.pressed_scale))
    #             if self.pressed_sound:
    #                 if isinstance(self.pressed_sound, urs.Audio):
    #                     self.pressed_sound.play()
    #                 elif isinstance(self.pressed_sound, str):
    #                     urs.Audio(self.pressed_sound, auto_destroy=True)

    #     if key == "left mouse up":
    #         if self.hovered:
    #             self.model.setColorScale(self.highlight_color)
    #             self.model.setScale(
    #                 urs.Vec3(self.highlight_scale, 1, self.highlight_scale)
    #             )
    #         else:
    #             self.model.setColorScale(self.color)
    #             self.model.setScale(urs.Vec3(1, 1, 1))

    # def on_mouse_enter(self: Self) -> None:
    #     """Called by Ursina when the mouse cursor is over the button"""
    #     if not self.disabled and self.model:
    #         self.model.setColorScale(self.highlight_color)

    #         if self.highlight_scale != 1:
    #             self.model.setScale(
    #                 urs.Vec3(self.highlight_scale, 1, self.highlight_scale)
    #             )

    #         if self.highlight_sound:
    #             if isinstance(self.highlight_sound, urs.Audio):
    #                 self.highlight_sound.play()
    #             elif isinstance(self.highlight_sound, str):
    #                 urs.Audio(self.highlight_sound, auto_destroy=True)

    #     if hasattr(self, "tooltip") and self.tooltip:
    #         self.tooltip.enabled = True

    # def on_mouse_exit(self: Self) -> None:
    #     """Called by Ursina when the mouse cursor leaves the button area"""
    #     if not self.disabled and self.model:
    #         self.model.setColorScale(self.color)

    #         if not urs.mouse.left and self.highlight_scale != 1:
    #             self.model.setScale(urs.Vec3(1, 1, 1))

    #     if hasattr(self, "tooltip") and self.tooltip:
    #         self.tooltip.enabled = False
