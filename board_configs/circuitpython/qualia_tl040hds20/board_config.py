""" Qualia S3 RGB-666 with TL040HDS20 4.0" 720x720 Square Display """

# Similar configs for RGBMatrix, usb_video, is31fl3741 an picodvi
import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay
import adafruit_focaltouch
from mpdisplay import FBDisplay, Devices


displayio.release_displays()

tft_pins = dict(board.TFT_PINS)

tft_timings = {
    "frequency": 16000000,
    "width": 720,
    "height": 720,
    "hsync_pulse_width": 2,
    "hsync_front_porch": 46,
    "hsync_back_porch": 44,
    "vsync_pulse_width": 2,
    "vsync_front_porch": 16,
    "vsync_back_porch": 18,
    "hsync_idle_low": False,
    "vsync_idle_low": False,
    "de_idle_high": False,
    "pclk_active_high": False,
    "pclk_idle_high": False,
}

init_sequence_tl040hds20 = bytes()

board.I2C().deinit()
i2c = busio.I2C(board.SCL, board.SDA)
tft_io_expander = dict(board.TFT_IO_EXPANDER)
#tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
dotclockframebuffer.ioexpander_send_init_sequence(i2c, init_sequence_tl040hds20, **tft_io_expander)

dcfb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)
display = FramebufferDisplay(dcfb, auto_refresh=True)
display.root_group = None

display_drv = FBDisplay(dcfb)

touch_drv = adafruit_focaltouch.Adafruit_FocalTouch(i2c, address=0x48)

def touch_read_func():
    touches = touch_drv.touches
    for touch in touches:
        return touch["x"], touch["y"]
    return None

touch_rotation_table=(0, 0, 0, 0)

touch_dev = display_drv.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
