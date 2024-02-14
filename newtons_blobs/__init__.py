"""
Newton's Laws, a simulator of physics at the scale of space

Package init file

by Jason Mott, copyright 2024
"""

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = "0.0.2"
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


from .globals import *
from .resources import resource_path, home_path_plus
from .blob_runner import BlobRunner
from .blob_plotter import BlobPlotter
from .massive_blob import MassiveBlob
from .blob_surface import BlobSurface
from .blob_save_load import BlobSaveLoad
