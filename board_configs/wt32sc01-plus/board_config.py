""" WT32-SC01 Plus 320x480 ST7796 display """

from lcd_bus import I80Bus
from st7796 import ST7796
from machine import I2C, Pin  # See the note about reset below
from ft6x36 import FT6x36


# The WT32-SC01 Plus has the reset pins of the display IC and the touch IC both
# tied to pin 4.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is not common.  If they aren't tied 
# together on your board, define reset in ST7796 instead, like:
#    ST7796(reset=4)
reset=Pin(4, Pin.OUT, value=1)

display_bus = I80Bus(
    dc=0,
    wr=47,
    cs=6,
    data0=9,
    data1=46,
    data2=3,
    data3=8,
    data4=18,
    data5=17,
    data6=16,
    data7=15,
    freq=20000000,
    dc_idle_level=0,
    dc_cmd_level=0,
    dc_dummy_level=0,
    dc_data_level=1,
    cmd_bits=8,
    param_bits=8,
    cs_active_high=False,
    reverse_color_bits=False,
    swap_color_bytes=False,
    pclk_active_neg=False,
    pclk_idle_low=False,
)

display_drv = ST7796(
    display_bus,
    width=320,
    height=480,
    colstart=0,
    rowstart=0,
    rotation=-1,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=True,
    brightness=1.0,
    backlight_pin=45,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

i2c = I2C(0, sda=Pin(6), scl=Pin(5), freq=100000)
touch_drv = FT6x36(i2c)
touch_drv_read = touch_drv.get_positions
