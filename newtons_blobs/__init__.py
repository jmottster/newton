"""
Newton's Laws, a simulator of physics at the scale of space

Package init file

by Jason Mott, copyright 2025
"""

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


from .blob_global_vars import BlobGlobalVars
from .resources import (
    resource_path,
    home_path_plus,
    resource_path_str,
    relative_resource_path_str,
)
from .blob_runner import BlobRunner
from .blob_plotter import BlobPlotter
from .massive_blob import MassiveBlob
from .blob_surface import BlobSurface
from .blob_save_load import BlobSaveLoad
from .blob_physics import BlobPhysics
from .blob_universe import BlobUniverse
from .blob_display import BlobDisplay
from .blob_plugin_factory import BlobPluginFactory
from .savable_loadable_prefs import SavableLoadablePrefs
from .blob_random import blob_random
from .blob_vector import BlobVector
