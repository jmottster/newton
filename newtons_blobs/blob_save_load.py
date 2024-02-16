"""
Newton's Laws, a simulator of physics at the scale of space

The class that saves and loads blob application state

by Jason Mott, copyright 2024
"""

import json
from .resources import home_path_plus
from .globals import *

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
    get_prefs() and set_prefs())

    Attributes
    ----------
    blob_runner: an instance of a class that runs the blob application and implements get_prefs(data) and set_prefs(data)

    blob_plotter: an instance of a class that manages the blob application and implements get_prefs(data) and set_prefs(data, universe)

    Methods
    -------
    save()
        Saves the objects to a json file for later retrieval

    load(universe)
        Loads the saved json file (if exists) and sends to the set_prefs() of the objects. The blob_plotter object needs to implement
        set_prefs(universe), which provides the drawing canvas needed for display of blobs

    load_value(key)
        Returns the value of the single key in the json_data file, has no effect on blob_runner, blob_plotter

    save_value(key,value)
        Saves the key/value pair in the stored json_data file, has no effect on blob_runner, blob_plotter

    """

    def __init__(self, blob_runner, blob_plotter):
        self.blob_runner = blob_runner
        self.blob_plotter = blob_plotter
        self.json_data = {}

    def save(self, get_prefs=True):
        """Saves the objects to a json file for later retrieval"""
        if get_prefs:
            self.blob_runner.get_prefs(self.json_data)
            self.blob_plotter.get_prefs(self.json_data)
        with open(home_path_plus((".newton",), "saved.json"), "w") as json_file:
            json.dump(self.json_data, json_file, indent=3)

    def load(self, universe, set_prefs=True):
        """
        Loads the saved json file (if exists) and sends to the set_prefs() of the objects. The blob_plotter object needs to implement
        set_prefs(universe), which provides the drawing canvas needed for display of blobs
        """
        try:
            with open(home_path_plus((".newton",), "saved.json"), "r") as json_file:
                self.json_data = json.load(json_file)
        except:
            print("No such file")
            return False

        if set_prefs:
            self.blob_runner.set_prefs(self.json_data)
            self.blob_plotter.set_prefs(self.json_data, universe)
        return True

    def load_value(self, key):
        """Returns the value of the single key in the json_data file, has no effect on blob_runner, blob_plotter"""
        if self.load(None, False):
            return self.json_data[key]

        return None

    def save_value(self, key, value):
        """Saves the key/value pair in the stored json_data file, has no effect on blob_runner, blob_plotter"""
        if self.load(None, False):
            self.json_data[key] = value
            self.save(False)
