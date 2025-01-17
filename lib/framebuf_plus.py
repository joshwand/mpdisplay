# SPDX-FileCopyrightText: <text> 2018 Kattni Rembor, Melissa LeBlanc-Williams
# and Tony DiCola, for Adafruit Industries.
# Copyright 2024 Brad Barnett
# Original file created by Damien P. George
# SPDX-License-Identifier: MIT

"""
A subclass of FrameBuffer that adds some useful methods for drawing shapes and text.
Each method returns a bounding box (x, y, w, h) of the drawn shape to indicate
the area of the display that was modified.  This can be used to update only the
modified area of the display.
"""

# Inherits from frambuf.Framebuffer, which may be compiled into MicroPython
# or may be from framebuf.py.  This module should return an Area object, but
# the MicroPython framebuf module returns None, so the methods inherited from
# framebuf.FrameBuffer are overridden to return an Area object.
# The methods inherited from ExtendedShapes are not overridden, as they already
# return an Area object.
from framebuf import FrameBuffer as _FrameBuffer
from framebuf import (
    MVLSB,
    MONO_VLSB,
    MONO_HLSB,
    MONO_HMSB,
    RGB565,
    GS2_HMSB,
    GS4_HMSB,
    GS8,
)
from primitives import ExtendedShapes, Area
import math


class FrameBuffer(_FrameBuffer, ExtendedShapes):
    def __init__(self, buffer, width, height, format, *args, **kwargs):
        super().__init__(buffer, width, height, format, *args, **kwargs)
        self.width = width
        self.height = height
        
        if format == MONO_VLSB:
            self._color_depth = 1
        elif format == MONO_HLSB:
            self._color_depth = 1
        elif format == MONO_HMSB:
            self._color_depth = 1
        elif format == RGB565:
            self._color_depth = 16
        elif format == GS2_HMSB:
            self._color_depth = 2
        elif format == GS4_HMSB:
            self._color_depth = 4
        elif format == GS8:
            self._color_depth = 8
        else:
            raise ValueError("invalid format")
    @property
    def color_depth(self):
        return self._color_depth

    def fill_rect(self, x, y, w, h, c):
        """
        Fill a rectangle at the given location, size and color.

        Args:
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width in pixels
            height (int): Height in pixels
            c (int): 565 encoded color
        """
        super().fill_rect(x, y, w, h, c)
        return Area(x, y, w, h)

    def fill(self, c):
        """
        Fill the entire display with the given color.

        Args:
            c (int): 565 encoded color
        """
        super().fill(c)
        return Area(0, 0, self.width, self.height)

    def pixel(self, x, y, c):
        """
        Draw a single pixel at the given location and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            c (int): 565 encoded color
        """
        super().pixel(x, y, c)
        return Area(x, y, 1, 1)

    def hline(self, x, y, w, c):
        """
        Draw a horizontal line at the given location, width and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            w (int): Width in pixels
            c (int): 565 encoded color
        """
        super().hline(x, y, w, c)
        return Area(x, y, w, 1)

    def vline(self, x, y, h, c):
        """
        Draw a vertical line at the given location, height and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            h (int): Height in pixels
            c (int): 565 encoded color
        """
        super().vline(x, y, h, c)
        return Area(x, y, 1, h)

    def line(self, x1, y1, x2, y2, c):
        """
        Draw a line between the given start and end points and color.

        Args:
            x1 (int): Start x coordinate
            y1 (int): Start y coordinate
            x2 (int): End x coordinate
            y2 (int): End y coordinate
            c (int): 565 encoded color
        """
        super().line(x1, y1, x2, y2, c)
        return Area(min(x1, x2), min(y1, y2), abs(x2 - x1) + 1, abs(y2 - y1) + 1)

    def rect(self, x, y, w, h, c, f=False):
        """
        Draw a rectangle at the given location, size and color.

        Args:
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width in pixels
            height (int): Height in pixels
            c (int): 565 encoded color
            f (bool): Fill the rectangle (default: False)
        """
        super().rect(x, y, w, h, c, f)
        return Area(x, y, w, h)

    def ellipse(self, x, y, rx, ry, c, f=False, m=0b1111):
        """
        Draw an ellipse at the given location, radii and color.

        Args:
            x (int): Center x coordinate
            y (int): Center y coordinate
            rx (int): X radius
            ry (int): Y radius
            c (int): 565 encoded color
            f (bool): Fill the ellipse (default: False)
            m (int): Bitmask to determine which quadrants to draw (default: 0b1111)
        """
        super().ellipse(x, y, rx, ry, c, f, m)
        return Area(x - rx, y - ry, 2 * rx, 2 * ry)

    def poly(self, x, y, coords, c, f=False):
        """
        Draw a polygon at the given location, coordinates and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            coords (array): Array of x, y coordinate tuples
            c (int): 565 encoded color
            f (bool): Fill the polygon (default: False)
        """
        super().poly(x, y, coords, c, f)
        # Convert the coords to a list of x, y tuples if it is not already
        if isinstance(coords, list):
            vertices = coords
        elif isinstance(coords, tuple):
            vertices = list(coords)
        else:
            # Check that the coords array has an even number of elements
            if len(coords) % 2 != 0:
                raise ValueError("coords must have an even number of elements")
            vertices = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
        # Find the min and max x and y values
        min_x = min([v[0] for v in vertices])
        min_y = min([v[1] for v in vertices])
        max_x = max([v[0] for v in vertices])
        max_y = max([v[1] for v in vertices])
        return Area(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def text(self, first_arg, *args, **kwargs):
        if isinstance(first_arg, (str, bytes)):
            return self.atext(first_arg, *args, **kwargs)
        else:
            return self.ttext(first_arg, *args, **kwargs)

