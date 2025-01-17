# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
SDL2Display class for MicroPython on Linux and CPython on available platforms.
"""

from . import _BaseDisplay, Events, Devices, Area
from sdl2_lib import (
    SDL_Init, SDL_Quit, SDL_GetError, SDL_CreateWindow, SDL_CreateRenderer, SDL_PollEvent,
    SDL_DestroyWindow, SDL_DestroyRenderer, SDL_DestroyTexture, SDL_SetRenderDrawColor, SDL_Point,
    SDL_RenderClear, SDL_RenderPresent, SDL_RenderSetLogicalSize, SDL_SetWindowSize, SDL_RenderCopyEx,
    SDL_SetRenderTarget, SDL_SetTextureBlendMode, SDL_RenderFillRect, SDL_RenderCopy,
    SDL_UpdateTexture, SDL_CreateTexture, SDL_GetKeyName, SDL_Rect, SDL_Event, SDL_QUIT,
    SDL_PIXELFORMAT_ARGB8888, SDL_PIXELFORMAT_RGB888, SDL_PIXELFORMAT_RGB565, SDL_TEXTUREACCESS_TARGET,
    SDL_BLENDMODE_NONE, SDL_RENDERER_ACCELERATED, SDL_RENDERER_PRESENTVSYNC, SDL_WINDOWPOS_CENTERED,
    SDL_WINDOW_SHOWN, SDL_INIT_EVERYTHING, SDL_BUTTON_LMASK, SDL_BUTTON_MMASK, SDL_BUTTON_RMASK,
    SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL, SDL_KEYDOWN, SDL_KEYUP,
)
from sys import implementation
if implementation.name == 'cpython':
    import ctypes
    is_cpython = True
else:
    is_cpython = False


def retcheck(retvalue):
    # Check the return value of an SDL function and raise an exception if it's not 0
    if retvalue:
        raise RuntimeError(SDL_GetError())


class SDL2Display(_BaseDisplay):
    '''
    A class to emulate an LCD using SDL2.
    Provides scrolling and rotation functions similar to an LCD.  The .texture
    object functions as the LCD's internal memory.
    '''
    def __init__(
        self,
        width=320,
        height=240,
        rotation=0,
        color_depth=16,
        title="SDL2 Display",
        scale=1.0,
        window_flags=SDL_WINDOW_SHOWN,
        render_flags=SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC,
        x=SDL_WINDOWPOS_CENTERED,
        y=SDL_WINDOWPOS_CENTERED,
    ):
        """
        Initializes the display instance with the given parameters.

        :param width: The width of the display (default is 320).
        :type width: int
        :param height: The height of the display (default is 240).
        :type height: int
        :param rotation: The rotation of the display (default is 0).
        :type rotation: int
        :param color_depth: The color depth of the display (default is 16).
        :type color_depth: int
        :param title: The title of the display window (default is "MicroPython").
        :type title: str
        :param scale: The scale factor for the display (default is 1).
        :type scale: int
        :param window_flags: The flags for creating the display window (default is SDL_WINDOW_SHOWN).
        :type window_flags: int
        :param render_flags: The flags for creating the renderer (default is SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC).
        :type render_flags: int
        :param x: The x-coordinate of the display window's position (default is SDL_WINDOWPOS_CENTERED).
        :type x: int
        :param y: The y-coordinate of the display window's position (default is SDL_WINDOWPOS_CENTERED).
        :type y: int
        """
        super().__init__()
        self._width = width
        self._height = height
        self._rotation = rotation
        self.color_depth = color_depth
        self._title = title
        self._window_flags = window_flags
        self._scale = scale
        self._buffer = None

        # Determine the pixel format
        if color_depth == 32:
            self._px_format = SDL_PIXELFORMAT_ARGB8888
        elif color_depth == 24:
            self._px_format = SDL_PIXELFORMAT_RGB888
        elif color_depth == 16:
            self._px_format = SDL_PIXELFORMAT_RGB565
        else:
            raise ValueError("Unsupported color_depth")

        retcheck(SDL_Init(SDL_INIT_EVERYTHING))
        self._window = SDL_CreateWindow(self._title.encode(), x, y, int(self.width*self._scale), int(self.height*self._scale), self._window_flags)
        if not self._window:
            raise RuntimeError(f"{SDL_GetError()}")
        self._renderer = SDL_CreateRenderer(self._window, -1, render_flags)
        if not self._renderer:
            raise RuntimeError(f"{SDL_GetError()}")
        
        self._buffer = SDL_CreateTexture(self._renderer, self._px_format, SDL_TEXTUREACCESS_TARGET, self.width, self.height)
        if not self._buffer:
            raise RuntimeError(f"{SDL_GetError()}")
        retcheck(SDL_SetTextureBlendMode(self._buffer, SDL_BLENDMODE_NONE))

        self.init()

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        retcheck(SDL_SetWindowSize(self._window, int(self.width*self._scale), int(self.height*self._scale)))
        retcheck(SDL_RenderSetLogicalSize(self._renderer, self.width, self.height))
        
        super().vscrdef(0, self.height, 0)  # Set the vertical scroll definition without calling _show
        self.vscsad(False)  # Scroll offset; set to False to disable scrolling

    def blit_rect(self, buffer, x, y, w, h):
        """
        Blits a buffer to the display.
        
        :param x: The x-coordinate of the display.
        :type x: int
        :param y: The y-coordinate of the display.
        :type y: int
        :param w: The width of the display.
        :type w: int
        :param h: The height of the display.
        :type h: int
        :param buffer: The buffer to blit_rect to the display.
        :type buffer: bytearray
        """
        pitch = int(w * self.color_depth // 8)
        if len(buffer) != pitch * h:
            raise ValueError("Buffer size does not match dimensions")
        blitRect = SDL_Rect(x, y, w, h)
        if is_cpython:
            if type(buffer) is memoryview:
                buffer_array = (ctypes.c_ubyte * len(buffer.obj)).from_buffer(buffer.obj)
            elif type(buffer) is bytearray:
                buffer_array = (ctypes.c_ubyte * len(buffer)).from_buffer(buffer)
            else:
                raise ValueError(f"Buffer is of type {type(buffer)} instead of memoryview or bytearray")
            buffer_ptr = ctypes.c_void_p(ctypes.addressof(buffer_array))
            retcheck(SDL_UpdateTexture(self._buffer, blitRect, buffer_ptr, pitch))
        else:
            retcheck(SDL_UpdateTexture(self._buffer, blitRect, buffer, pitch))
        self._show(blitRect)
        return Area(x, y, w, h)

    def fill_rect(self, x, y, w, h, color):
        """
        Fill a rectangle with a color.

        Renders to the texture instead of directly to the window
        to facilitate scrolling and scaling.

        :param x: The x-coordinate of the rectangle.
        :type x: int
        :param y: The y-coordinate of the rectangle.
        :type y: int
        :param w: The width of the rectangle.
        :type w: int
        :param h: The height of the rectangle.
        :type h: int
        :param color: The color of the rectangle.
        :type color: int
        """
        fillRect = SDL_Rect(x, y, w, h)
        r, g, b = self.color_rgb(color)

        retcheck(SDL_SetRenderTarget(self._renderer, self._buffer))  # Set the render target to the texture
        retcheck(SDL_SetRenderDrawColor(self._renderer, r, g, b, 255))  # Set the color to fill the rectangle
        retcheck(SDL_RenderFillRect(self._renderer, fillRect))  # Fill the rectangle on the texture
        retcheck(SDL_SetRenderTarget(self._renderer, None))  # Reset the render target back to the window
        self._show(fillRect)
        return Area(x, y, w, h)

    def deinit(self):
        """
        Deinitializes the sdl2lcd instance.
        """
        retcheck(SDL_DestroyTexture(self._buffer))
        retcheck(SDL_DestroyRenderer(self._renderer))
        retcheck(SDL_DestroyWindow(self._window))
        retcheck(SDL_Quit())

    ############### API Method Overrides ################

    def vscrdef(self, tfa, vsa, bfa):
        """
        Set the vertical scroll definition.

        :param tfa: The top fixed area.
        :type tfa: int
        :param vsa: The vertical scroll area.
        :type vsa: int
        :param bfa: The bottom fixed area.
        :type bfa: int
        """
        super().vscrdef(tfa, vsa, bfa)
        self._show()

    def vscsad(self, vssa=None):
        """
        Set the vertical scroll start address.
        
        :param vssa: The vertical scroll start address.
        :type vssa: int
        """
        if vssa is not None:
            super().vscsad(vssa)
            self._show()
        else:
            return super().vscsad()

    @property
    def rotation(self):
        """
        The rotation of the display.

        :return: The rotation of the display.
        :rtype: int
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """
        Sets the rotation of the display.

        Makes sure the rotation is not a multiple of 360, creates a new texture to use as the buffer and
        copies the old one, applying rotation with SDL_RenderCopyEx.  Destroys the old buffer.

        :param value: The rotation of the display.
        :type value: int
        """

        value = self._rotation_helper(value)

        if value == self._rotation:
            return

        if (angle := (value % 360) - (self._rotation % 360)) != 0:
            if implementation.name == 'cpython':
                # print("Before.")
                tempBuffer = SDL_CreateTexture(self._renderer, self._px_format, SDL_TEXTUREACCESS_TARGET, self.height, self.width)
                # print("After.")
                if not tempBuffer:
                    raise RuntimeError(f"{SDL_GetError()}")

                retcheck(SDL_SetTextureBlendMode(tempBuffer, SDL_BLENDMODE_NONE))
                retcheck(SDL_SetRenderTarget(self._renderer, tempBuffer))
                if abs(angle) != 180:
                    dstrect = SDL_Rect(
                        (self.height - self.width) // 2,
                        (self.width - self.height) // 2,
                        self.width,
                        self.height
                    )
                else:
                    dstrect = None
                retcheck(SDL_RenderCopyEx(self._renderer, self._buffer, None, dstrect, angle, None, 0))
                retcheck(SDL_SetRenderTarget(self._renderer, None))
                retcheck(SDL_DestroyTexture(self._buffer))
                self._buffer = tempBuffer
            else:
                retcheck(SDL_DestroyTexture(self._buffer))
                self._buffer = SDL_CreateTexture(self._renderer, self._px_format, SDL_TEXTUREACCESS_TARGET, self.height, self.width)
                if not self._buffer:
                    raise RuntimeError(f"{SDL_GetError()}")
                retcheck(SDL_SetTextureBlendMode(self._buffer, SDL_BLENDMODE_NONE))

        self._rotation = value
        
        for device in self.devices:
            if device.type == Devices.TOUCH:
                device.rotation = value

        self.init()

    ############### Class Specific Methods ##############

    def _show(self, renderRect=None):
        """
        Show the display.  Automatically called after blitting or filling the display.

        :param renderRect: The rectangle to render (default is None).
        :type renderRect: SDL_Rect
        """
        if (y_start := self.vscsad()) == False:
            retcheck(SDL_RenderCopy(self._renderer, self._buffer, renderRect, renderRect))
        else:
            # Ignore renderRect and render the entire texture to the window in four steps
            if self._tfa > 0:
                tfaRect = SDL_Rect(0, 0, self.width, self._tfa)
                retcheck(SDL_RenderCopy(self._renderer, self._buffer, tfaRect, tfaRect))

            vsaTopHeight = self._vsa + self._tfa - y_start
            vsaTopSrcRect = SDL_Rect(0, y_start, self.width, vsaTopHeight)
            vsaTopDestRect = SDL_Rect(0, self._tfa, self.width, vsaTopHeight)
            retcheck(SDL_RenderCopy(self._renderer, self._buffer, vsaTopSrcRect, vsaTopDestRect))

            vsaBtmHeight = self._vsa - vsaTopHeight
            vsaBtmSrcRect = SDL_Rect(0, self._tfa, self.width, vsaBtmHeight)
            vsaBtmDestRect = SDL_Rect(0, self._tfa + vsaTopHeight, self.width, vsaBtmHeight)
            retcheck(SDL_RenderCopy(self._renderer, self._buffer, vsaBtmSrcRect, vsaBtmDestRect))

            if self._bfa > 0:
                bfaRect = SDL_Rect(0, self._tfa + self._vsa, self.width, self._bfa)
                retcheck(SDL_RenderCopy(self._renderer, self._buffer, bfaRect, bfaRect))

        retcheck(SDL_RenderPresent(self._renderer))


class SDL2EventQueue():
    """
    A class to poll events in SDL2.
    """
    def __init__(self):
        """
        Initializes the SDL2Events instance.
        """
        self._event = SDL_Event()

    def read(self):
        """
        Polls for an event and returns the event type and data.

        :return: The event type and data.
        :rtype: tuple
        """
        if SDL_PollEvent(self._event):
            if is_cpython:
                if self._event.type in Events.filter:
                    return self._convert(SDL_Event(self._event))
            else:
                if int.from_bytes(self._event[:4], 'little') in Events.filter:
                    return self._convert(SDL_Event(self._event))
        return None

    @staticmethod
    def _convert(e):
        if e.type == SDL_MOUSEMOTION:
            l = 1 if e.motion.state & SDL_BUTTON_LMASK else 0
            m = 1 if e.motion.state & SDL_BUTTON_MMASK else 0
            r = 1 if e.motion.state & SDL_BUTTON_RMASK else 0
            evt = Events.Motion(e.type, (e.motion.x, e.motion.y), (e.motion.xrel, e.motion.yrel), (l, m, r), e.motion.which != 0, e.motion.windowID)
        elif e.type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP):
            evt = Events.Button(e.type, (e.button.x, e.button.y), e.button.button, e.button.which != 0, e.button.windowID)
        elif e.type == SDL_MOUSEWHEEL:
            evt = Events.Wheel(e.type, e.wheel.direction != 0, e.wheel.x, e.wheel.y, e.wheel.preciseX, e.wheel.preciseY, e.wheel.which != 0, e.wheel.windowID)
        elif e.type in (SDL_KEYDOWN, SDL_KEYUP):
            name = SDL_GetKeyName(e.key.keysym.sym)
            evt = Events.Key(e.type, name, e.key.keysym.sym, e.key.keysym.mod, e.key.keysym.scancode, e.key.windowID)
        elif e.type == SDL_QUIT:
            evt = Events.Quit(e.type)
        else:
            evt = Events.Unknown(e.type)
        return evt
