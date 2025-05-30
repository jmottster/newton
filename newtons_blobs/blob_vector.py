"""
Newton's Laws, a simulator of physics at the scale of space

Class file implementing a Vector

by Jason Mott, copyright 2025
"""

from typing import Any, Iterator, List, Self, Tuple

import math

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobVector:
    """
    Class file implementing a Vector

    Attributes
    ----------
    x : float
        Value for the x axis of this vector

    y : float
        Value for the y axis of this vector

    z : float
        Value for the z axis of this vector

    Static Methods
    -------
    zero() -> "BlobVector"
        Returns a BlobVector with all values as 0

    one() -> "BlobVector"
        Returns a BlobVector with all values as 1

    right() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction to the right according the z-up-right coordinate system

    left() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction to the left according the z-up-right coordinate system

    up() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction up according the z-up-right coordinate system

    down() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction down according the z-up-right coordinate system

    forward() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction forward according the z-up-right coordinate system

    back() -> "BlobVector"
        Returns a normalized BlobVector representing the
        direction backwards according the z-up-right coordinate system

    Methods
    -------
    diff(other: BlobVector) -> BlobVector
        Returns a BlobVector whose values are other - self

    distance(other: BlobVector) -> float
        Returns the distance of other from self

    mag() -> float
        Returns the magnitude (length) of this BlobVector

    normalize() -> BlobVector
        Returns a normalized version of this BlobVector

    dot(other: "BlobVector") -> float
        Returns the dot product of this vector and other

    cross(other: "BlobVector") -> "BlobVector"
        Returns the cross product of this vector and other

    angle(other: "BlobVector") -> float
        Returns the angle between this vector and other

    to_tuple() -> Tuple[float, ...]
        Returns a tuple of floats conversion of this vector

    to_int_tuple() -> Tuple[int, int, int]
        Returns a tuple of rounded ints conversion of this vector

    to_float_rounded(places: int = 2) -> Tuple[float, float, float]
        Returns a tuple of rounded floats to the designated places conversion of this vector

    """

    def __init__(self: Self, *args):

        self.values: List[float] = None
        if len(args) == 0:
            self.values = [0, 0, 0]
        else:
            self.values = list(args)

    @property
    def x(self: Self) -> float:
        """Returns the x value of this vector (at position 0)"""
        return self.values[0]

    @x.setter
    def x(self: Self, value: float) -> None:
        """Sets the x value of this vector (at position 0)"""
        self.values[0] = value

    @property
    def y(self: Self) -> float:
        """Returns the y value of this vector (at position 1)"""
        return self.values[1]

    @y.setter
    def y(self: Self, value: float) -> None:
        """Sets the y value of this vector (at position 1)"""
        self.values[1] = value

    @property
    def z(self: Self) -> float:
        """Returns the z value of this vector (at position 2)"""
        return self.values[2]

    @z.setter
    def z(self: Self, value: float) -> None:
        """Sets the z value of this vector (at position 2)"""
        self.values[2] = value

    @staticmethod
    def zero() -> "BlobVector":
        """Returns a BlobVector with all values as 0"""
        return BlobVector(0, 0, 0)

    @staticmethod
    def one() -> "BlobVector":
        """Returns a BlobVector with all values as 1"""
        return BlobVector(1, 1, 1)

    @staticmethod
    def right() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction to the right according the z-up-right coordinate system
        """
        return BlobVector(1, 0, 0)

    @staticmethod
    def left() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction to the left according the z-up-right coordinate system
        """
        return BlobVector(-1, 0, 0)

    @staticmethod
    def up() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction up according the z-up-right coordinate system
        """
        return BlobVector(0, 0, 1)

    @staticmethod
    def down() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction down according the z-up-right coordinate system
        """
        return BlobVector(0, 0, -1)

    @staticmethod
    def forward() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction forward according the z-up-right coordinate system
        """
        return BlobVector(0, 1, 0)

    @staticmethod
    def back() -> "BlobVector":
        """
        Returns a normalized BlobVector representing the
        direction backwards according the z-up-right coordinate system
        """
        return BlobVector(0, -1, 0)

    def diff(self: Self, other: "BlobVector") -> "BlobVector":
        """Returns a BlobVector whose values are other - self"""
        return BlobVector(
            *(
                other.values[0] - self.values[0],
                other.values[1] - self.values[1],
                other.values[2] - self.values[2],
            )
        )

    def distance(self: Self, other: "BlobVector") -> float:
        """Returns the distance of other from self"""
        return math.sqrt(
            (other.values[0] - self.values[0]) ** 2
            + (other.values[1] - self.values[1]) ** 2
            + (other.values[2] - self.values[2]) ** 2
        )

    def mag(self: Self) -> float:
        """Returns the magnitude (length) of this BlobVector"""
        return math.sqrt(
            self.values[0] ** 2 + self.values[1] ** 2 + self.values[2] ** 2
        )

    def normalize(self: Self) -> "BlobVector":
        """Returns a normalized version of this BlobVector"""
        mag: float = self.mag()
        return BlobVector(
            *(self.values[0] / mag, self.values[1] / mag, self.values[2] / mag)
        )

    def dot(self: Self, other: "BlobVector") -> float:
        """Returns the dot product of this vector and other"""
        return (
            other.values[0] * self.values[0]
            + other.values[1] * self.values[1]
            + other.values[2] * self.values[2]
        )

    def cross(self: Self, other: "BlobVector") -> "BlobVector":
        """Returns the cross product of this vector and other"""
        return BlobVector(
            *(
                self.values[1] * other.values[2] - self.values[2] * other.values[1],
                self.values[2] * other.values[0] - self.values[0] * other.values[2],
                self.values[0] * other.values[1] - self.values[1] * other.values[0],
            )
        )

    def angle(self: Self, other: "BlobVector") -> float:
        """Returns the angle between this vector and other"""
        return math.acos(self.dot(other) / (self.mag() * other.mag()))

    def to_tuple(self: Self) -> Tuple[float, ...]:
        """Returns a tuple of floats conversion of this vector"""
        return tuple(self.values)

    def to_int_tuple(self: Self) -> Tuple[int, int, int]:
        """Returns a tuple of rounded ints conversion of this vector"""
        return (round(self.values[0]), round(self.values[1]), round(self.values[2]))

    def to_float_rounded(self: Self, places: int = 2) -> Tuple[float, float, float]:
        """Returns a tuple of rounded floats to the designated places conversion of this vector"""
        return (
            round(self.values[0], places),
            round(self.values[1], places),
            round(self.values[2], places),
        )

    def __mul__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector multiplication of self and other"""
        try:
            return BlobVector(
                *(
                    self.values[0] * other.values[0],
                    self.values[1] * other.values[1],
                    self.values[2] * other.values[2],
                )
            )
        except Exception:
            return BlobVector(
                *(
                    self.values[0] * other,
                    self.values[1] * other,
                    self.values[2] * other,
                )
            )

    def __rmul__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 * self for instance"""
        return self.__mul__(other)

    def __truediv__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector division of self and other"""

        try:
            return BlobVector(
                *(
                    self.values[0] / other.values[0],
                    self.values[1] / other.values[1],
                    self.values[1] / other.values[1],
                )
            )
        except Exception:
            return BlobVector(
                *(
                    self.values[0] / other,
                    self.values[1] / other,
                    self.values[1] / other,
                )
            )

    def __add__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector addition of self and other"""

        try:
            return BlobVector(
                *(
                    self.values[0] + other.values[0],
                    self.values[1] + other.values[1],
                    self.values[2] + other.values[2],
                )
            )
        except Exception:
            return BlobVector(
                *(
                    self.values[0] + other,
                    self.values[1] + other,
                    self.values[2] + other,
                )
            )

    def __radd__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 + self for instance"""
        return self.__add__(other)

    def __sub__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector difference of self and other"""

        try:
            return BlobVector(
                *(
                    self.values[0] - other.values[0],
                    self.values[1] - other.values[1],
                    self.values[2] - other.values[2],
                )
            )
        except Exception:
            return BlobVector(
                *(
                    self.values[0] - other,
                    self.values[1] - other,
                    self.values[2] - other,
                )
            )

    def __rsub__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 - self for instance"""

        if isinstance(other, (int, float)):
            return BlobVector(
                *(
                    other - self.values[0],
                    other - self.values[1],
                    other - self.values[2],
                )
            )
        else:
            return NotImplemented

    def __abs__(self: Self) -> "BlobVector":
        """Returns the BlobVector with absolute values (non-negative)"""
        return BlobVector(
            *(abs(self.values[0]), abs(self.values[1]), abs(self.values[2]))
        )

    def __iter__(self: Self) -> Iterator:
        """Returns an Iterator of this instance"""
        return self.values.__iter__()

    def __len__(self: Self) -> int:
        """Returns the length of this vector"""
        return len(self.values)

    def __getitem__(self: Self, key: int) -> float:
        """Returns the value at index key in this vector"""
        return self.values[key]

    def __repr__(self: Self) -> str:
        """Returns a string version of this vector"""
        return str(self.values)
