"""
Newton's Laws, a simulator of physics at the scale of space

Class to create an Ursina text object

by Jason Mott, copyright 2024
"""

from typing import Any, Dict, List, Self, Tuple
from panda3d.core import TextNode, NodePath, TextFont  # type: ignore

import re

from panda3d.core import Vec3 as PanVec3  # type: ignore

import builtins

import ursina as urs  # type: ignore
from ursina import Entity as ursEntity

from newtons_blobs.globals import *
from .blob_quad import createBlobQuad

__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class BlobText(urs.Entity):
    """
    Class to create an Ursina text object

    note:
        <scale:n> tag doesn't work well in the middle of text.
        only good for titles for now.

    Attributes
    ----------
    text: str
        The text to be displayed

    my_forward: PanVec3
        the first person forward direction

    my_back: PanVec3
        the first person backwards direction

    my_right: PanVec3
        the first person right direction

    my_left: PanVec3
        the first person left direction

    my_up: PanVec3
        the first person up direction

    my_down: PanVec3
        the first person down direction

    font: TextFont
        The TextFont font to use when displaying text

    color: urs.Color
        The color of the text when displayed

    line_height: float
        The height of each line of text

    width: float
        The width of the longest line of text

    height: float
        The overall height of all text lines

    lines: List[str]
        A List of each line of text (each element in List is a line)

    resolution: float
        The pixels per unit of the font

    wordwrap: int
        The number of characters before a text wrap

    origin: urs.Vec3
        Where position 0 is at relative to the center of text

    background: urs.Entity
        The Entity that gives a background to text



    Methods
    -------
    create_text_section(text: str, tag: str = "", x: float = 0, z: float = 0) -> None
        Creates a section of text

    align() -> None
        Aligns the text

    create_background(padding: Any = size * 2, radius: float = size, color: urs.Color = urs.color.black66) -> None
        Creates a background Entity for text

    appear(speed: float = 0.025) -> urs.Sequence
        Creates a Sequence for animating the appearance of text


    Static Methods
    --------------
    get_width(string: str, font: str = None) -> float
        returns the width of given font

    """

    size: float = 0.025
    default_font: str = "OpenSans-Regular.ttf"
    default_resolution: float = 1080 * size * 2
    start_tag: str = "<"
    end_tag: str = ">"

    def __init__(
        self: Self,
        text: str = "",
        start_tag: str = start_tag,
        end_tag: str = end_tag,
        ignore: bool = True,
        **kwargs,
    ):
        super().__init__(ignore=ignore)

        self.raw_text: str = ""
        self.size: float = BlobText.size
        self.parent: urs.Entity = urs.camera.ui

        # self.setColorScaleOff()
        self.shader: str = None
        self.text_nodes: List[NodePath] = []
        self.images: List[ursEntity] = []
        self._origin: urs.Vec3 = urs.Vec3(-0.5, 0, 0.5)

        self._font: TextFont = None
        self._color: urs.Color = None
        self._line_height: float = 1
        self._wordwrap: int = 0
        self._background: urs.Entity = None
        self.use_tags: bool = False
        self.start_tag: str = start_tag
        self.end_tag: str = end_tag
        self.text_colors: Dict[str, urs.Color] = {"default": urs.color.text_color}

        for color_name in urs.color.color_names:
            self.text_colors[color_name] = urs.color.colors[color_name]

        self.tag: str = BlobText.start_tag + "default" + BlobText.end_tag
        self.current_color: urs.Color = self.text_colors["default"]
        self.scale_override: float = 1
        self.appear_sequence: urs.Sequence = None  # gets created when calling appear()

        self.font = BlobText.default_font
        self.resolution = BlobText.default_resolution

        if "origin" in kwargs:  # set the scale before model for correct corners
            setattr(self, "origin", kwargs["origin"])
        if "use_tags" in kwargs:
            setattr(self, "use_tags", kwargs["use_tags"])

        if text != "":
            self.text = text

        for key, value in kwargs.items():
            if key == "origin":
                continue
            setattr(self, key, value)

    @property
    def text(self: Self) -> str:
        """The text to be displayed"""

        if self.text_nodes:
            if len(self.text_nodes) > 1:
                t: str = ""
                z: float = 0
                z = self.text_nodes[0].getZ()

                for tn in self.text_nodes:
                    if z != tn.getZ():
                        t += "\n"
                        z = tn.getZ()

                    t += tn.node().text

                return t
            return self.text_nodes[0].node().text
        return ""

    @text.setter  # set this to update the text.
    def text(self: Self, text: str) -> None:
        """Sets the text to be displayed"""
        self.raw_text = text

        for img in self.images:
            urs.destroy(img)
        self.images = []

        for tn in self.text_nodes:
            tn.remove_node()
        self.text_nodes = []
        if not text:
            return

        if not self.use_tags:
            self.create_text_section(text)
            self.align()
            return

        text = self.start_tag + self.end_tag + str(text)
        sections: List[List[str]] = []
        positions: List[List[float]] = []
        section: str = ""
        tag: str = self.start_tag + "default" + self.end_tag
        temp_text_node: TextNode = TextNode("temp_text_node")
        temp_text_node.setFont(self.font)
        x: float = 0
        z: float = 0

        i: int = 0
        while i < len(text):
            char = text[i]
            if char == "\n":
                sections.append([section, tag])
                positions.append([x, z])
                section = ""
                z -= 1
                x = 0
                i += 1

            elif char == self.start_tag:  # find tag
                sections.append([section, tag])
                positions.append([x, z])
                x += temp_text_node.calcWidth(section)
                section = ""

                tag = ""
                done = False
                for j in range(len(text) - i):
                    tag += text[i + j]
                    if text[i + j] == self.end_tag and len(tag) > 0:
                        i += j + 1
                        done = True
                        break
                if not done:
                    i += 1
            else:
                section += char
                i += 1

        sections.append([section, tag])
        positions.append([x, z])

        for i, p in enumerate(positions):
            tag = sections[i][1]
            # move the text after image one space right
            if tag.startswith(self.start_tag + "image:"):
                for f in positions:
                    if f[1] == p[1] and f[0] > p[0]:
                        f[0] += 0.5

                p[0] += 0.5

            self.create_text_section(
                text=sections[i][0], tag=sections[i][1], x=p[0], z=p[1]
            )

        self.align()

    @property
    def my_forward(self: Self) -> PanVec3:
        """get the first person forward direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.forward()))

    @property
    def my_back(self: Self) -> PanVec3:
        """get the first person backwards direction"""
        return -self.my_forward

    @property
    def my_right(self: Self) -> PanVec3:
        """get the first person right direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.right()))

    @property
    def my_left(self: Self) -> PanVec3:
        """get the first person left direction"""
        return -self.my_right

    @property
    def my_up(self: Self) -> PanVec3:
        """get the first person up direction"""
        return PanVec3(*urs.scene.getRelativeVector(self, PanVec3.up()))

    @property
    def my_down(self: Self) -> PanVec3:
        """get the first person down direction"""
        return -self.my_up

    @property
    def font(self: Self) -> TextFont:
        """The TextFont font to use when displaying text"""
        return self._font

    @font.setter
    def font(self: Self, value: str) -> None:
        """Sets the font to use when displaying text"""
        font: TextFont = builtins.loader.loadFont(value)  # type: ignore
        if font is not None:
            self._font = font
            self._font.clear()  # remove assertion warning
            self._font.setPixelsPerUnit(self.resolution)
            self._font.setLineHeight(self.line_height)
            if self.text:
                self.text = self.raw_text  # update tex

    @property
    def color(self: Self) -> urs.Color:
        """The color of the text when displayed"""
        return getattr(self, "_color", urs.color.white)

    @color.setter
    def color(self: Self, value: urs.Color) -> None:
        """Sets the color of the text when displayed"""
        self._color = value
        self.current_color = value
        self.text_colors["default"] = value
        for tn in self.text_nodes:
            tn.node().setTextColor(value)
        for img in self.images:
            img.color = value

    @property
    def line_height(self: Self) -> float:
        """The height of each line of text"""
        return getattr(self, "_line_height", 1)

    @line_height.setter
    def line_height(self: Self, value: float) -> None:
        """Sets the height of each line of text"""
        self._line_height = value
        if self.use_tags and self.text:
            self.text = self.raw_text
        else:
            self._font.setLineHeight(value)

    @property
    def width(self: Self) -> float:
        """The width of the longest line of text"""
        if not hasattr(self, "text"):
            return 0

        temp_text_node = TextNode("temp")
        temp_text_node.setFont(self._font)

        longest_line_length: float = 0
        for line in self.text.split("\n"):
            longest_line_length = max(
                longest_line_length, temp_text_node.calcWidth(line)
            )

        return longest_line_length * self.size

    @property
    def height(self: Self) -> float:
        """The overall height of all text lines"""
        return len(self.lines) * self.line_height * self.size

    @property
    def lines(self: Self) -> List[str]:
        """A List of each line of text (each element in List is a line)"""
        return self.text.splitlines()

    @property
    def resolution(self: Self) -> float:
        """The pixels per unit of the font"""
        return self._font.getPixelsPerUnit()

    @resolution.setter
    def resolution(self: Self, value: float) -> None:
        """Sets the pixels per unit of the font"""
        self._font.setPixelsPerUnit(value)

    @property
    def wordwrap(self: Self) -> int:
        """The number of characters before a text wrap"""
        if hasattr(self, "_wordwrap"):
            return self._wordwrap
        else:
            return 0

    @wordwrap.setter
    def wordwrap(self: Self, value: int) -> None:
        """Sets the number of characters before a text wrap"""
        self._wordwrap = value
        if not value:
            return

        new_text: str = ""
        clean_string: str = ""
        for line in self.raw_text.split("\n"):
            x: int = 0
            for word in line.split(" "):
                clean_string = re.sub("<.*?>", "", word)
                x += len(clean_string) + 1
                # print('w:', word, 'len:', len(clean_string), 'clean str:', clean_string)

                if x >= value:
                    new_text += "\n"
                    x = 0

                new_text += word + " "

            new_text += "\n"

        self.text = new_text

    @property
    def origin(self: Self) -> urs.Vec3:
        """Where position 0 is at relative to the center of text"""
        return self._origin

    @origin.setter
    def origin(self: Self, value: urs.Vec3):
        """Sets where position 0 is at relative to the center of text"""
        self._origin = value
        if self.text:
            self.text = self.raw_text

    @property
    def background(self: Self) -> urs.Entity:
        """The Entity that gives a background to text"""
        return self._background

    @background.setter
    def background(self: Self, value: bool) -> None:
        """Set to True to create a background"""
        if value is True:
            self.create_background()
        elif self._background:

            urs.destroy(self._background)

    def create_text_section(
        self: Self, text: str, tag: str = "", x: float = 0, z: float = 0
    ) -> None:
        """Creates a section of text"""

        text_node: TextNode = TextNode("t")
        text_node_path: NodePath = self.attachNewNode(text_node)
        try:
            text_node.setFont(self._font)
        except:
            pass  # default font

        # if self.use_tags and tag != "<>":
        #     tag = tag[1:-1]

        #     if tag.startswith("hsb("):  # set color based on numbers
        #         tag = tag[4:-1]
        #         hsb_values: Tuple[float, ...] = tuple(
        #             float(e.strip()) for e in tag.split(",")
        #         )
        #         self.current_color = urs.color.hsv(*hsb_values)

        #     elif tag.startswith("rgb("):  # set color based on numbers
        #         tag = tag[4:-1]
        #         rgb_values: Tuple[float, ...] = tuple(
        #             float(e.strip()) for e in tag.split(",")
        #         )
        #         self.current_color = urs.color.rgba(*rgb_values)

        #     if tag.startswith("scale:"):
        #         scale: str = tag.split(":")[1]
        #         self.scale_override = float(scale)

        #     elif tag.startswith("image:"):
        #         texture_name: str = tag.split(":")[1]
        #         image: urs.Entity = urs.Entity(
        #             parent=text_node_path,
        #             name="inline_image",
        #             model="quad",
        #             texture=texture_name,
        #             color=self.current_color,
        #             origin=(0.0, 0, -0.25),
        #             add_to_scene_entities=False,
        #         )
        #         if not image.texture:
        #             urs.destroy(image)
        #         else:
        #             self.images.append(image)

        #     else:
        #         if tag in self.text_colors:
        #             self.current_color = self.text_colors[tag]

        text_node_path.setScale(self.scale_override * self.size)

        text_node.setText(text)
        text_node.setTextColor(self.current_color)
        text_node.setPreserveTrailingWhitespace(True)

        text_node_path.setPos(
            x * self.size * self.scale_override,
            0,
            (z * self.size * self.line_height) - 0.75 * self.size,
        )
        self.text_nodes.append(text_node_path)

    def align(self: Self) -> None:
        """Aligns the text"""
        value: urs.Vec3 = self.origin

        linewidths: List[float] = [
            self.text_nodes[0].node().calcWidth(line) for line in self.lines
        ]
        linenumber: int = 0
        half_height: float = 0
        for tn in self.text_nodes:
            linenumber = abs(int(tn.getZ() / self.size / self.line_height))
            linenumber = urs.clamp(linenumber, 0, len(linewidths) - 1)

            tn.setX(
                tn.getX()
                - (
                    linewidths[linenumber]
                    / 2
                    * self.size
                    * tn.getScale()[0]
                    / self.size
                )
            )

            tn.setX(
                tn.getX()
                - (linewidths[linenumber] / 2 * value[0] * 2 * self.size)
                * tn.getScale()[0]
                / self.size
            )
            half_height = len(linewidths) * self.line_height / 2
            tn.setZ(tn.getZ() + (half_height * self.size))
            tn.setZ(tn.getZ() - (half_height * value[2] * 2 * self.size))

    def create_background(
        self: Self,
        padding: Any = size * 2,
        radius: float = size,
        color: urs.Color = urs.color.black66,
    ) -> None:
        """Creates a background Entity for text"""

        if self._background is not None:
            urs.destroy(self._background)

        self._background = urs.Entity(
            parent=self,
            y=0.06,
            unlit=True,
            shader=None,
        )

        tup_padding: Tuple[float, float]

        if isinstance(padding, (int, float, complex)):
            tup_padding = (float(padding), float(padding))  # type: ignore
        else:
            tup_padding = padding

        w: float = 0
        h: float = 0

        w, h = self.width + tup_padding[0], self.height + tup_padding[1]
        self.background.x -= self.origin_x * self.width

        self.background.z -= self.origin_z * self.height

        self.background.model = createBlobQuad(radius=radius, scale=(w, 0, h))
        self.background.color = color

    def appear(self: Self, speed: float = 0.025) -> urs.Sequence:
        """Creates a Sequence for animating the appearance of text"""
        self.enabled = True

        if self.appear_sequence:
            self.appear_sequence.finish()

        self.appear_sequence = urs.Sequence()
        target_text: str = ""
        new_text: str = ""
        for tn in self.text_nodes:
            target_text = tn.node().getText()
            tn.node().setText("")
            new_text = ""

            for char in target_text:
                new_text += char
                self.appear_sequence.append(urs.Wait(speed))
                self.appear_sequence.append(urs.Func(tn.node().setText, new_text))

        self.appear_sequence.start()
        return self.appear_sequence

    @staticmethod
    def get_width(string: str, font: str = None) -> float:
        """returns the width of given font"""
        t: BlobText = BlobText(string)
        if font:
            t.font = font
        w: float = t.width

        urs.destroy(t)
        return w
