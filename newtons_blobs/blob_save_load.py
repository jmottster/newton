"""
Newton's Laws, a simulator of physics at the scale of space

The class that saves and loads blob application state

by Jason Mott, copyright 2024
"""

import json
from typing import Any, Dict, List, Self
from .resources import home_path_plus
from .globals import *
from .savable_loadable_prefs import SavableLoadablePrefs

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobSaveLoad:
    """
    A class that will save and load (to and from a json file) the states of the provided objects (which must implement
    SavableLoadablePrefs)

    Attributes
    ----------
    savable_loadables: List[SavableLoadablePrefs] a list of objects that implement SavableLoadablePrefs

    Methods
    -------
    save(get_prefs: bool = True) -> None
        Saves the savable_loadables objects (by calling get_prefs() on each) to a json file for later retrieval

    load(universe: pygame.Surface, set_prefs: bool = True) -> bool
        Loads the saved json file (if exists) and sends to the set_prefs() of the savable_loadables objects

    load_value(key: str) -> Any
        Returns the value of the single key in the json_data file, has no effect on blob_runner, blob_plotter

    save_value(key: str, value: Any) -> None
        Saves the key/value pair in the stored json_data file, has no effect on blob_runner, blob_plotter

    """

    def __init__(self: Self, savable_loadables: List[SavableLoadablePrefs]):
        self.savable_loadables: List[SavableLoadablePrefs] = savable_loadables
        self.json_data: Dict[str, Any] = {}

    def save(self: Self, get_prefs: bool = True) -> None:
        """Saves the savable_loadables objects (by calling get_prefs() on each) to a json file for later retrieval"""
        if get_prefs:
            for savable_loadable in self.savable_loadables:
                savable_loadable.get_prefs(self.json_data)

        with open(home_path_plus((".newton",), "saved.json"), "w") as json_file:
            json.dump(self.json_data, json_file, indent=3)

    def load(self: Self, set_prefs: bool = True) -> bool:
        """
        Loads the saved json file (if exists) and sends to the set_prefs() of the savable_loadables objects
        """
        try:
            with open(home_path_plus((".newton",), "saved.json"), "r") as json_file:
                self.json_data = json.load(json_file)
        except:
            print("No such file")
            return False

        if set_prefs:
            for savable_loadable in self.savable_loadables:
                savable_loadable.set_prefs(self.json_data)
        return True

    def load_value(self: Self, key: str) -> Any:
        """Returns the value of the single key in the json_data file, has no effect on blob_runner, blob_plotter"""
        if self.load(False):
            return self.json_data[key]

        return None

    def save_value(self: Self, key: str, value: Any) -> None:
        """Saves the key/value pair in the stored json_data file, has no effect on blob_runner, blob_plotter"""
        if self.load(False):
            self.json_data[key] = value
            self.save(False)
