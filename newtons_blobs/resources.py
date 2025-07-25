"""
Newton's Laws, a simulator of physics at the scale of space

File for resource related vars or functions

by Jason Mott, copyright 2025
"""

import sys
from pathlib import Path
from typing import Tuple
from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


def relative_resource_path_str(relative_path: str, leading_char: str = ".") -> str:
    """Get string version of absolute path to resource, works for local drive and for PyInstaller by automatically detecting context"""
    my_str = str(resource_path(Path(relative_path))).replace(
        str(Path().absolute()), leading_char
    )
    return my_str


def resource_path_str(relative_path: str) -> str:
    """Get string version of absolute path to resource, works for local drive and for PyInstaller by automatically detecting context"""
    return str(resource_path(Path(relative_path)))


def resource_path(relative_path: Path) -> Path:
    """Get absolute path to resource, works for local drive and for PyInstaller by automatically detecting context"""
    mypath = Path()

    try:
        base_path = Path(__file__).parent
        if not mypath.joinpath(base_path, relative_path).exists():
            base_path = Path(__file__).parent.parent

    except Exception:
        base_path = mypath.absolute()

    return mypath.joinpath(base_path, relative_path)


def home_path_plus(
    path_tuple: Tuple[str], file: str, create_if_not_exists: bool = True
) -> Path:
    """Get or create a file in the user home directory (no need to send home dir, it'll be the base no matter what)"""
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


def home_path_plus_exists(path_tuple: Tuple[str], file: str) -> bool:
    """find out if a file exists in the user home directory (no need to send home dir, it'll be the base no matter what)"""
    mypath = Path()
    full_path = mypath.home()
    for item in path_tuple:
        full_path = mypath.joinpath(full_path, item)
        if not full_path.exists():
            return False
    full_path = mypath.joinpath(full_path, file)
    if not full_path.exists():
        return False

    return True
