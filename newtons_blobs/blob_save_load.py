"""
Newton's Laws, a simulator of physics at the scale of space

The class that saves and loads blob application state

by Jason Mott, copyright 2025
"""

import json
from typing import Any, Dict, List, Self
from .resources import home_path_plus, home_path_plus_exists
from .globals import *
from .savable_loadable_prefs import SavableLoadablePrefs

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
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
    savable_loadables: List[SavableLoadablePrefs]
        a list of objects that implement SavableLoadablePrefs

    Methods
    -------
    find_session_num() -> int
        Get the next available session number for incremental saving, if over 10, it remains at 10
        deletes 1 and moves all other existing save file down one session number

    rename_session(session_num: str, new_session_num: str) -> None
        Rename a session series of files (session_num-session_save_itr.json to new_session_num-session_save_itr.json)

    save(get_prefs: bool = True, file_name: str = "saved.json") -> None
        Saves the savable_loadables objects (by calling get_prefs() on each) to a json file for later retrieval

    load(universe: pygame.Surface, set_prefs: bool = True) -> bool
        Loads the saved json file (if exists) and sends to the set_prefs() of the savable_loadables objects

    load_value(key: str) -> Any
        Returns the value of the single key in the json_data file, has no effect on any savable_loadables objects

    save_value(key: str, value: Any) -> None
        Saves the key/value pair in the stored json_data file, has no effect on any savable_loadables objects

    """

    def __init__(self: Self, savable_loadables: List[SavableLoadablePrefs]):
        self.savable_loadables: List[SavableLoadablePrefs] = savable_loadables
        self.json_data: Dict[str, Any] = {}

    def find_session_num(self: Self) -> int:
        """
        Get the next available session number for incremental saving, if over 10, it remains at 10
        deletes 1 and moves all other existing save file down one session number
        """
        session_int: int = 1

        while home_path_plus_exists((".newton",), f"{session_int}-0.json"):
            session_int += 1

        if session_int == 11:
            session_int = 10
            i: int = 1
            y: int = 0

            while home_path_plus_exists((".newton",), f"{i}-{y}.json"):
                home_path_plus((".newton",), f"{i}-{y}.json").unlink()
                y += 1

            for n in range(2, 11):
                self.rename_session(str(n), str(i))
                i += 1

        return session_int

    def rename_session(self: Self, session_num: str, new_session_num: str) -> int:
        """Rename a session series of files (session_num-session_save_itr.json to new_session_num-session_save_itr.json)"""
        y = 0
        while home_path_plus_exists((".newton",), f"{session_num}-{y}.json"):
            home_path_plus((".newton",), f"{session_num}-{y}.json").rename(
                home_path_plus((".newton",), f"{new_session_num}-{y}.json", False)
            )
            y += 1
        return y - 1

    def save(self: Self, get_prefs: bool = True, file_name: str = "saved.json") -> None:
        """
        Saves the savable_loadables objects (by calling get_prefs() on each) to a json file for later retrieval
        """
        if get_prefs:
            for savable_loadable in self.savable_loadables:
                savable_loadable.get_prefs(self.json_data)

        with open(home_path_plus((".newton",), file_name), "w") as json_file:
            json.dump(self.json_data, json_file, indent=3)
        json_file.close()

    def load(self: Self, set_prefs: bool = True, file_name: str = "saved.json") -> bool:
        """
        Returns the value of the single key in the json_data file, has no effect on any savable_loadables objects
        """
        try:
            with open(home_path_plus((".newton",), file_name), "r") as json_file:
                self.json_data = json.load(json_file)
            json_file.close()
        except:
            print(f"No such file: {home_path_plus((".newton",),file_name)}")
            return False

        if set_prefs:
            for savable_loadable in self.savable_loadables:
                savable_loadable.set_prefs(self.json_data)
        return True

    def load_value(self: Self, key: str) -> Any:
        """
        Returns the value of the single key in the json_data file, has no effect on any savable_loadables objects
        """
        if self.load(False):
            return self.json_data[key]

        return None

    def save_value(self: Self, key: str, value: Any) -> None:
        """
        Saves the key/value pair in the stored json_data file, has no effect on any savable_loadables objects
        """
        if self.load(False):
            self.json_data[key] = value
            self.save(False)
