"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class used to define the interface for objects that BlobSaveLoad can, well, save and load

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, Optional, Protocol, Self

import pygame

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class SavableLoadablePrefs(Protocol):
    """
    A Protocol class used to define the interface for objects the BlobSaveLoad can, well, save and load

    Attributes
    ----------

    Methods
    -------
    get_prefs(data: dict) -> None
        Sending a dict to this method will load the dict up with attributes that are desired to be saved.

    set_prefs(data: dict, universe: pygame.Surface = None) -> None
        Sending a dict and a pygame.Surface instances to this method, to it's implementer can load up values from it (that it saved when
        populating dict in get_prefs()). universe object represents the drawable surface that some objects may need to load themselves

    """

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Sending a dict to this method will load the dict up with attributes that are desired to be saved."""
        pass

    def set_prefs(
        self: Self, data: Dict[str, Any], universe: Optional[pygame.Surface] = None
    ) -> None:
        """
        Sending a dict and a pygame.Surface instances to this method, to it's implementer can load up values from it (that it saved when
        populating dict in get_prefs()). universe object represents the drawable surface that some objects may need to load themselves
        """
        pass
