"""
Newton's Laws, a simulator of physics at the scale of space

A static wrapper class for generating random numbers. This makes it easy to globally
change the implementation

by Jason Mott, copyright 2025
"""

import secrets
import numpy as np

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class blob_random:
    """
    A static wrapper class for generating random numbers. This makes it easy to globally
    change the implementation

    Methods
    -------
    random() -> float
        Returns a random float in the half-open interval 0.0 - 1.0

    randint(a: int, b: int) -> int
        Returns a random integer from a low (inclusive) to b high (inclusive)

    """

    np_random = np.random.default_rng(secrets.randbits(1024))

    @staticmethod
    def random() -> float:
        """Returns a random float in the half-open interval 0.0 - 1.0"""

        blob_random.np_random = np.random.default_rng(secrets.randbits(1024))

        # blob_random.np_random = np.random.default_rng(
        #     round(blob_random.np_random.random() * 20000000000000)
        # )
        return blob_random.np_random.random()

    @staticmethod
    def randint(a: int, b: int) -> int:
        """Returns a random integer from a low (inclusive) to b high (inclusive)"""

        blob_random.np_random = np.random.default_rng(secrets.randbits(1024))

        # blob_random.np_random = np.random.default_rng(
        #     round(blob_random.np_random.random() * 20000000000000)
        # )
        b += 1
        return blob_random.np_random.integers(a, b)
