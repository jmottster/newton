"""
Newton's Laws, a simulator of physics at the scale of space

Package init file

by Jason Mott, copyright 2024
"""

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.5"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


from newtons_blobs.globals import *

from .blob_pygame_factory import BlobPygameFactory
from .blob_universe_pygame import BlobUniversePygame
from .blob_display_pygame import BlobDisplayPygame
from .blob_surface_pygame import BlobSurfacePygame
