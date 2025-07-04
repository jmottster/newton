"""
Newton's Laws, a simulator of physics at the scale of space

Package init file

by Jason Mott, copyright 2025
"""

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


from .blob_text import BlobText
from .blob_prog_bar import BlobProgBar
from .blob_button import BlobButton
from .blob_quad import createBlobQuad
from .blob_circle import BlobCircle
from .blob_rotator import BlobRotator
from .blob_materials import SunMaterial, PlanetMaterial
from .blob_node_path_factory import BlobNodePathFactory
from .blob_line import BlobLine
