"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2024
"""

from blob_runner import BlobRunner
from globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


if __name__ == "__main__":
    blober = BlobRunner()
    blober.run()
