"""
Newton's Laws, a simulator of physics at the scale of space



by Jason Mott, copyright 2024
"""

from typing import Tuple, Self, Protocol

from .blob_surface import BlobSurface
from .blob_display import BlobDisplay
from .blob_universe import BlobUniverse
from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobPluginFactory(Protocol):

    def new_blob_surface(
        self: Self, radius: float, color: Tuple[int, int, int]
    ) -> BlobSurface:
        """Factory method for instantiating instances, as implementation is not known at runtime"""
        pass

    def get_blob_universe(self: Self) -> BlobUniverse:
        pass

    def get_blob_display(self: Self) -> BlobDisplay:
        pass
