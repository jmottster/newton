"""
Newton's Laws, a simulator of physics at the scale of space

A Protocol class used to define the interface for objects that BlobSaveLoad can, well, save and load

by Jason Mott, copyright 2025
"""

from typing import Any, Dict, Protocol, Self

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
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
        Sending a dict to this method will load the dict up with attributes that are desired to be saved

    set_prefs(data: dict) -> None
        Send a dict instances to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs())
    """

    def get_prefs(self: Self, data: Dict[str, Any]) -> None:
        """Sending a dict to this method will load the dict up with attributes that are desired to be saved"""
        pass

    def set_prefs(self: Self, data: Dict[str, Any]) -> None:
        """
        Send a dict instances to this method so its implementer can load up values from it (that it saved when
        populating dict in get_prefs())
        """
        pass
