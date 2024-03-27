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

from .blob_ursina_factory import BlobUrsinaFactory
from .blob_universe_ursina import BlobUniverseUrsina
from .blob_display_ursina import BlobDisplayUrsina
from .blob_surface_ursina import BlobSurfaceUrsina
