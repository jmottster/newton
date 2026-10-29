"""
Newton's Laws, a simulator of physics at the scale of space

Class file implementing a Vector

by Jason Mott, copyright 2025
"""

from typing import Any, Iterator, List, Self, Tuple

import math

from .globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2026"
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

    tilt(pitch: float, yaw: float) -> "BlobVector"
        Returns a normalized BlobVector tilted according to pitch (rotation about
        the y axis in radians) and yaw (rotation about the z axis in radians)

    Methods
    -------
    clear() -> None
        Resets all values to 0

    diff(other: BlobVector) -> BlobVector
        Returns a BlobVector whose values are other - self

    relative_to_self(other: "BlobVector") -> "BlobVector"
        Returns a BlobVector that represents other's position
        relative to this BlobVector, i.e. other - self

    relative_to(other: "BlobVector") -> "BlobVector"
        Returns a BlobVector that represents this BlobVector's position
        relative to other's position, i.e., self - other

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

    cross_a_b() -> Tuple["BlobVector", "BlobVector"]
        Returns two norm vectors which are perpendicular to this vector and to each other

    angle(other: "BlobVector") -> float
        Returns the angle between this vector and other

    to_tuple() -> Tuple[float, ...]
        Returns a tuple of floats conversion of this vector

    to_int_tuple() -> Tuple[int, int, int]
        Returns a tuple of rounded ints conversion of this vector

    to_float_rounded(places: int = 2) -> Tuple[float, float, float]
        Returns a tuple of rounded floats to the designated places conversion of this vector

    rotate_point(roll: float, yaw: float) -> "BlobVector"
        Rotates a single 3D point (x, y, z) given Roll, and Yaw in radians.
        Roll is rotation about the y axis and Yaw is rotation about the z axis).

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

    @staticmethod
    def tilt(pitch: float, yaw: float) -> "BlobVector":
        """
        Returns a vector tilted according to pitch (rotation about
        the y axis in radians) and yaw (rotation about the z axis in radians)
        """
        return BlobVector(
            math.sin(pitch) * math.cos(yaw),
            math.sin(pitch) * math.sin(yaw),
            math.cos(pitch),
        )

    def clear(self: Self) -> None:
        """Resets all values to 0"""
        self.x, self.y, self.z = 0.0, 0.0, 0.0

    def diff(self: Self, other: "BlobVector") -> "BlobVector":
        """Returns a BlobVector whose values are other - self"""
        return BlobVector(
            other.values[0] - self.values[0],
            other.values[1] - self.values[1],
            other.values[2] - self.values[2],
        )

    def relative_to_self(self: Self, other: "BlobVector") -> "BlobVector":
        """
        Returns a BlobVector that represents other's position
        relative to this BlobVector, i.e. other - self
        """
        return self.diff(other)

    def relative_to(self: Self, other: "BlobVector") -> "BlobVector":
        """
        Returns a BlobVector that represents this BlobVector's position
        relative to other's position, i.e., self - other
        """
        return BlobVector(
            self.values[0] - other.values[0],
            self.values[1] - other.values[1],
            self.values[2] - other.values[2],
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
            self.values[0] / mag, self.values[1] / mag, self.values[2] / mag
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
            self.values[1] * other.values[2] - self.values[2] * other.values[1],
            self.values[2] * other.values[0] - self.values[0] * other.values[2],
            self.values[0] * other.values[1] - self.values[1] * other.values[0],
        )

    def cross_a_b(self: Self) -> Tuple["BlobVector", "BlobVector"]:
        """Returns two norm vectors which are perpendicular to this vector and to each other"""
        cross_a: BlobVector
        cross_b: BlobVector
        if self.x < 0.9:
            cross_a = BlobVector(1, 0, 0).cross(self).normalize()
        else:
            cross_a = BlobVector(0, 1, 0).cross(self).normalize()

        cross_b = self.cross(cross_a).normalize()

        return (cross_a, cross_b)

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

    def rotate_point(self: Self, roll: float, yaw: float) -> "BlobVector":
        """
        Rotates a single 3D point (x, y, z) given Roll, and Yaw in radians.
        Roll is rotation about the y axis and Yaw is rotation about the z axis).
        """

        # Precompute sines and cosines
        s_r, c_r = math.sin(roll), math.cos(roll)
        s_y, c_y = math.sin(yaw), math.cos(yaw)

        return BlobVector(
            self.x * (c_y * c_r) - self.y * s_y + self.z * (c_y * s_r),
            self.x * (s_y * c_r) + self.y * c_y + self.z * (s_y * s_r),
            self.x * (-s_r) + self.z * c_r,
        )

    def __mul__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector multiplication of self and other"""
        try:
            return BlobVector(
                self.values[0] * other.values[0],
                self.values[1] * other.values[1],
                self.values[2] * other.values[2],
            )
        except Exception:
            return BlobVector(
                self.values[0] * other,
                self.values[1] * other,
                self.values[2] * other,
            )

    def __rmul__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 * self for instance"""
        return self.__mul__(other)

    def __truediv__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector division of self and other"""

        try:
            return BlobVector(
                self.values[0] / other.values[0],
                self.values[1] / other.values[1],
                self.values[2] / other.values[1],
            )
        except Exception:
            return BlobVector(
                self.values[0] / other,
                self.values[1] / other,
                self.values[2] / other,
            )

    def __add__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector addition of self and other"""

        try:
            return BlobVector(
                self.values[0] + other.values[0],
                self.values[1] + other.values[1],
                self.values[2] + other.values[2],
            )
        except Exception:
            return BlobVector(
                self.values[0] + other,
                self.values[1] + other,
                self.values[2] + other,
            )

    def __radd__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 + self for instance"""
        return self.__add__(other)

    def __sub__(self: Self, other: Any) -> "BlobVector":
        """Returns the BlobVector difference of self and other"""

        try:
            return BlobVector(
                self.values[0] - other.values[0],
                self.values[1] - other.values[1],
                self.values[2] - other.values[2],
            )
        except Exception:
            return BlobVector(
                self.values[0] - other,
                self.values[1] - other,
                self.values[2] - other,
            )

    def __rsub__(self: Self, other: Any) -> "BlobVector":
        """Called if 4 - self for instance"""

        if isinstance(other, (int, float)):
            return BlobVector(
                other - self.values[0],
                other - self.values[1],
                other - self.values[2],
            )
        else:
            return NotImplemented

    def __abs__(self: Self) -> "BlobVector":
        """Returns the BlobVector with absolute values (non-negative)"""
        return BlobVector(abs(self.values[0]), abs(self.values[1]), abs(self.values[2]))

    def __iter__(self: Self) -> Iterator:
        """Returns an Iterator of this instance"""
        return self.values.__iter__()

    def __len__(self: Self) -> int:
        """Returns the length of this vector"""
        return len(self.values)

    def __getitem__(self: Self, key: int) -> float:
        """Returns the value at index key in this vector"""
        return self.values[key]

    def __setitem__(self: Self, key: int, value: float) -> None:
        """Sets the value at index key in this vector"""
        self.values[key] = value

    def __repr__(self: Self) -> str:
        """Returns a string version of this vector"""
        return str(self.values)
