"""
Newton's Laws, a simulator of physics at the scale of space

A mesh class to create the blob trails

by Jason Mott, copyright 2024
"""

import numbers
import array
from typing import Any, List, Self

from ursina import Color
from ursina.vec3 import Vec3

import panda3d.core as p3d

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobLine(p3d.NodePath):
    """
    A mesh class to create the blob trails

    Attributes
    ----------
    parent : p3d.NodePath = None
        The NodePath that will be the parent to this instance

    vertices : List[Vec3] = None
        An array of vertices that will build this mesh, each point being an Ursina vector, Vec3

    colors : Color = None
        An array of colors for each vertex of this mesh, each being an Ursina Color object. The number of colors must match
        the number of vertices if any are provided. This is optional and can be None (which is the default).

    thickness : float = 1
        Determines how thick the line will be

    render_points_in_3d : bool = True
        Denotes if this instance will be in a 3d space or not

    Methods
    -------

    _ravel(Self, data: List[Any]) -> List[Any]
        For internal use, flattens a multi-dimensional array into a 1 dimensional array, as
        needed for the underlying rendering libraries

    _set_array_data(array_handle: p3d.GeomVertexArrayData, data: List[Any], dtype_string: str = "f") -> None
        For internal use, writes the contents of data into array handle, assuming provided data type. See memoryview()
        docs for data types

    setup_data() -> p3d.GeomVertexData
        For internal use, initializes a GeomVertexData object in preparation for rendering ths mesh. See Panda3D docs
        for more information


    setup_prim() -> p3d.GeomLinestrips
        For internal use, initializes a GeomLinestrips object in preparation for rendering the mesh. See Panda3D docs
        for more information

    generate() -> None
        Draws or redraws this mesh based on provided vertices. This must be called again if vertices or colors are
        changed

    clear(regenerate: bool = True) -> None
        Clears the vertices and color lists

    """

    def __init__(
        self: Self,
        parent: p3d.NodePath = None,
        vertices: List[Vec3] = None,
        colors: Color = None,
        thickness: float = 1,
        render_points_in_3d: bool = True,
    ):
        super().__init__("mesh")
        if parent is not None:
            self.reparentTo(parent)
        self.vertices: List[Vec3] = vertices
        self.colors: Color = colors
        self.color_attribute_index: int = -1
        self.thickness: float = thickness
        self.render_points_in_3d: bool = render_points_in_3d
        self.static_mode: p3d.UsageHint = p3d.Geom.UHDynamic
        self._generated_vertices: List[Vec3] = None

        for var in (
            ("vertices", vertices),
            ("colors", colors),
        ):
            name, value = var
            if value is None:
                setattr(self, name, [])

        self.geomNode: p3d.GeomNode = None
        self.geom: p3d.Geom = None
        self.data: p3d.GeomVertexData = None
        self.prim: p3d.GeomLinestrips = None

        if self.vertices is not None and len(self.vertices) > 0:
            self.geomNode = p3d.GeomNode("mesh_geom")
            self.attachNewNode(self.geomNode)
            self.data = self.setup_data()
            self.prim = self.setup_prim()

    def _ravel(self: Self, data: List[Any]) -> List[Any]:
        """
        For internal use, flattens a multi-dimensional array into a 1 dimensional array, as
        needed for the underlying rendering libraries
        """
        if not isinstance(data[0], numbers.Real):
            d: List[Any] = []
            for v in data:
                d.extend(v)
            return d
        return data

    def _set_array_data(
        self: Self,
        array_handle: p3d.GeomVertexArrayData,
        data: List[Any],
        dtype_string: str = "f",
    ) -> None:
        """
        For internal use, writes the contents of data into array handle, assuming provided data type. See memoryview()
        docs for data types
        """
        a: memoryview = None
        try:
            a = memoryview(data).cast("B").cast(dtype_string)
        except Exception as e:
            a = array.array(dtype_string, data)

        vmem: memoryview = memoryview(array_handle).cast("B").cast(dtype_string)
        try:
            vmem[:] = a

        except Exception as e:
            raise Exception(
                f"Error in Mesh: {e} || Ensure Mesh is valid and the inputs have same length: vertices:{len(self.vertices)}, colors:{len(self.colors)}"
            )

    def setup_data(self: Self) -> p3d.GeomVertexData:
        """
        For internal use, initializes a GeomVertexData object in preparation for rendering ths mesh. See Panda3D docs
        for more information
        """

        format: p3d.GeomVertexFormat = p3d.GeomVertexFormat()
        format.addArray(p3d.GeomVertexFormat.getV3().arrays[0])
        if self.colors is not None and len(self.colors) > 0:
            format.addArray(
                p3d.GeomVertexArrayFormat(
                    "color", 4, p3d.Geom.NT_float32, p3d.Geom.C_color
                )
            )
            self.color_attribute_index = 1

        format = p3d.GeomVertexFormat.registerFormat(format)

        data: p3d.GeomVertexData = p3d.GeomVertexData(
            "vertex_data", format, self.static_mode
        )

        data.unclean_set_num_rows(len(self.vertices))
        self._set_array_data(data.modify_array(0), self._ravel(self.vertices), "f")
        if self.colors is not None and len(self.colors) > 0:
            self._set_array_data(
                data.modify_array(self.color_attribute_index),
                self._ravel(self.colors),
                "f",
            )

        return data

    def setup_prim(self: Self) -> p3d.GeomLinestrips:
        """
        For internal use, initializes a GeomLinestrips object in preparation for rendering the mesh. See Panda3D docs
        for more information
        """
        self.geom = p3d.Geom(self.data)

        prim: p3d.GeomLinestrips = p3d.GeomLinestrips(self.static_mode)
        prim.set_index_type(p3d.GeomEnums.NT_uint32)

        n: int = len(self.vertices)
        indexes: List[int] = [i for i in range(n)]

        prim_array: p3d.GeomVertexArrayData = prim.modify_vertices()
        prim_array.set_num_rows(n)
        self._set_array_data(prim_array, indexes, "I")

        prim.close_primitive()
        self.geom.addPrimitive(prim)

        self.geomNode.addGeom(self.geom)

        return prim

    def generate(self: Self) -> None:
        """
        Draws or redraws this mesh based on provided vertices. This must be called again if vertices or colors are
        changed
        """
        self._generated_vertices = None

        if len(self.vertices) == 0:
            return

        self.data.unclean_set_num_rows(len(self.vertices))

        self._set_array_data(self.data.modify_array(0), self._ravel(self.vertices), "f")

        if self.colors is not None and len(self.colors) > 0:
            self._set_array_data(
                self.data.modify_array(self.color_attribute_index),
                self._ravel(self.colors),
                "f",
            )

        prim_array: p3d.GeomVertexArrayData = self.prim.modify_vertices()
        n: int = len(self.vertices)
        indexes: List[int] = [i for i in range(n)]
        prim_array.unclean_set_num_rows(n)
        self._set_array_data(prim_array, indexes, "I")

        self.geom.setVertexData(self.data)
        self.geom.setPrimitive(0, self.prim)

        self.geomNode.setGeom(0, self.geom)

    def clear(self: Self, regenerate: bool = True) -> None:
        """Clears the vertices and color lists"""
        self.vertices = []
        self.colors = []
        if regenerate:
            self.generate()

    @property
    def generated_vertices(self: Self) -> List[Vec3]:
        """Returns a list of the vertices used in the last rendering"""
        if self._generated_vertices is None:
            self._generated_vertices = self.vertices
        return self._generated_vertices

    @property
    def render_points_in_3d(self: Self) -> bool:
        """Returns boolean indicating if this is a 3D mesh"""
        return self._render_points_in_3d

    @render_points_in_3d.setter
    def render_points_in_3d(self: Self, value: bool) -> None:
        """Sets boolean indicating if this is a 3D mesh"""
        self._render_points_in_3d = value
        self.set_render_mode_perspective(value)

    def __str__(self: Self) -> str:
        """Returns the set name of this instance"""
        if hasattr(self, "name"):
            return self.name

    @property
    def thickness(self) -> float:
        """Returns the thickness attribute"""
        return self.getRenderModeThickness()

    @thickness.setter
    def thickness(self, value) -> None:
        """Sets the thickness attribute"""
        self.setRenderModeThickness(value)
