"""
Newton's Laws, a simulator of physics at the scale of space

Wrapper classes for Panda3D light classes

by Jason Mott, copyright 2024
"""

from typing import Self

from panda3d.core import NodePath  # type: ignore
from panda3d.core import Light as PandaLight  # type: ignore
from panda3d.core import PointLight as PandaPointLight  # type: ignore
from panda3d.core import AmbientLight as PandaAmbientLight  # type: ignore

import ursina as urs  # type: ignore

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobLight(urs.Entity):
    """
    A abstract base class for light wrappers to extend. One would never use this directly

    Attributes
    ----------
    **kwargs
        Specific to this class:
        light_name: str, entity_set_light: urs.Entity
    color: urs.Color the color the light will emit

    Methods
    -------
    init_light() -> PandaLight
        The method that sub classes must implement; it creates the specific kind of light
        and returns it as just a PandaLight. See Panda3D documentation

    destroy() -> None
        Call to turn off and properly clean up the light instance

    """

    def __init__(self: Self, **kwargs):
        super().__init__()
        self.rotation_x = 90
        self._color: urs.Color = urs.color.white
        self._light: PandaLight = self.init_light()
        self._light_node: NodePath = self.attachNewNode(self._light)

        if self.entity_set_light is not None:
            self.entity_set_light.setLight(self._light_node)
        else:
            render.setLight(self._light_node)  # type: ignore

        for key, value in kwargs.items():
            setattr(self, key, value)

    def init_light(self: Self) -> PandaLight:
        """
        The method that sub classes must implement; it creates the specific kind of light
        and returns it as just a PandaLight. See Panda3D documentation
        """
        pass

    def destroy(self: Self) -> None:
        """
        Call to turn off and properly clean up the light instance
        """
        if self.entity_set_light is not None:
            self.entity_set_light.clearLight(self._light_node)
        else:
            render.clearLight(self._light_node)  # type: ignore

    @property
    def color(self: Self) -> urs.Color:
        """get the color the light will emit"""
        return getattr(self, "_color", urs.color.white)

    @color.setter
    def color(self: Self, value: urs.Color):
        """set the color the light will emit"""
        self._color = value
        self._light.setColor(value)


class BlobPointLight(BlobLight):
    """
    A point light, which emits light in all directions from its set position

    Attributes
    ----------
    **kwargs
        Specific to this class:
        light_name: str, entity_set_light: urs.Entity

    Methods
    -------
    init_light() -> PandaLight
        Returns an instance of PandaPointLight(). See Panda3D documentation
    """

    def __init__(self: Self, **kwargs):

        self.light_name: str = kwargs.get("light_name")
        self.entity_set_light: urs.Entity = kwargs.get("entity_set_light")
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def init_light(self: Self) -> PandaLight:
        """Returns an instance of PandaPointLight(). See Panda3D documentation"""
        return PandaPointLight(f"point_light_{self.light_name}")


class BlobAmbientLight(BlobLight):
    """
    An ambient light, which emits light everywhere from no particular direction

    Attributes
    ----------
    **kwargs
        Specific to this class:
        light_name: str, entity_set_light: urs.Entity

    Methods
    -------
    init_light() -> PandaLight
        Returns an instance of PandaAmbientLight(). See Panda3D documentation
    """

    def __init__(self: Self, **kwargs):

        self.light_name: str = kwargs.get("light_name")
        self.entity_set_light: urs.Entity = kwargs.get("entity_set_light")
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def init_light(self: Self) -> PandaLight:
        """Returns an instance of PandaAmbientLight(). See Panda3D documentation"""
        return PandaAmbientLight(f"ambient_light_{self.light_name}")
