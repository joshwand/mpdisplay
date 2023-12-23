""" T-Embed ST7789 display with encoder"""

from lcd_bus import SPIBus
from st7789 import ST7789
from machine import Pin, I2C
from rotary_irq_esp import RotaryIRQ


display_bus = SPIBus(
    dc=13,
    host=1,
    mosi=11,
    miso=-1,
    sclk=12,
    cs=10,
    freq=60_000_000,
    wp=-1,
    hd=-1,
    quad_spi=False,
    tx_only=True,
    cmd_bits=8,
    param_bits=8,
    dc_low_on_data=False,
    sio_mode=False,
    lsb_first=False,
    cs_high_active=False,
    spi_mode=0,
)

display_drv = ST7796(
    display_bus,
    width=170,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=-1,  # PORTRAIT
    color_depth=16,
    bgr=False,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=15,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

encoder_drv = RotaryIRQ(1, 2, pull_up=True, half_step=True)
encoder_drv_read = encoder_drv.value
encoder_button = Pin(0, Pin.IN, Pin.PULL_UP)
encoder_button_read = lambda : not encoder_button.value()
