"""
Newton's Laws, a simulator of physics at the scale of space

File for resource related vars or functions

by Jason Mott, copyright 2024
"""

import sys
from pathlib import Path
from typing import Tuple
from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for local drive and for PyInstaller by automatically detecting context"""
    mypath = Path()

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = mypath.absolute()

    return mypath.joinpath(base_path, relative_path)


def home_path_plus(
    path_tuple: Tuple[str], file: str, create_if_not_exists: bool = True
) -> Path:
    mypath = Path()
    full_path = mypath.home()
    for item in path_tuple:
        full_path = mypath.joinpath(full_path, item)
        if create_if_not_exists and not full_path.exists():
            full_path.mkdir()
    full_path = mypath.joinpath(full_path, file)
    if create_if_not_exists and not full_path.exists():
        full_path.touch()

    return full_path
