"""
mpdisplay_touch_test.py - Touch rotation test for mpdisplay
Tests the touch driver and finds the correct rotation masks for the touch screen.
Sets the rotation to each of 4 possible values and asks the user to touch the rectangle in each of the 4 corners.
Then it prints the touch_rotation_table that should be set in board_config.py.
"""

from board_config import display_drv
from mpdisplay import Events

if hasattr(display_drv, "set_device_data"):
    from mpdisplay import Device_types

    demo = False
else:
    demo = True
    print(
        "\nThis display driver does not need touch rotations\n",
        "   but you can still use this app for testing purposes.",
    )

FG_COLOR = -1  # white
BG_COLOR = 0  # black

text = "Touch here"
text_width = len(text) * 8

SWAP_XY = 0b001
REVERSE_X = 0b010
REVERSE_Y = 0b100


def set_rotation_table(table):
    for device in display_drv._devices:
        if device.type == Device_types.TOUCH:
            display_drv.set_device_data(device.id, table)


def loop():
    display_drv.fill_rect(0, 0, display_drv.width - 1, display_drv.height - 1, BG_COLOR)

    print("Touch the rectangle in each corner for 4 rotations.\n")

    touch_rotation_table = []

    for rotation in range(0, 360, 90):
        touched_zones = []
        display_drv.rotation = rotation

        width = display_drv.width
        height = display_drv.height
        half_width = width // 2
        half_height = height // 2

        for y in range(2):
            for x in range(2):
                display_drv.round_rect(
                    x * half_width + 10,
                    y * half_height + 10,
                    half_width - 20,
                    half_height - 20,
                    10,
                    FG_COLOR,
                    True,
                )
                display_drv.btext(
                    text,
                    x * half_width + ((half_width - text_width) // 2),
                    y * half_height + ((half_height - 8) // 2),
                    BG_COLOR,
                )
                touched_point = None
                while not touched_point:
                    event = display_drv.poll()
                    if (
                        event
                        and event.type == Events.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        touched_point = event.pos
                zone = (touched_point[1] // half_height) * 2 + (
                    touched_point[0] // half_width
                )
                touched_zones.append(zone)
                print(f"{touched_point=} in {zone=}")
                display_drv.fill_rect(
                    x * half_width,
                    y * half_height,
                    half_width - 1,
                    half_height - 1,
                    BG_COLOR,
                )

        if touched_zones == [0, 1, 2, 3]:
            mask = 0b0
        elif touched_zones == [1, 0, 3, 2]:
            mask = REVERSE_X
        elif touched_zones == [2, 3, 0, 1]:
            mask = REVERSE_Y
        elif touched_zones == [3, 2, 1, 0]:
            mask = REVERSE_X | REVERSE_Y
        elif touched_zones == [0, 2, 1, 3]:
            mask = SWAP_XY
        elif touched_zones == [2, 0, 3, 1]:
            mask = SWAP_XY | REVERSE_X
        elif touched_zones == [1, 3, 0, 2]:
            mask = SWAP_XY | REVERSE_Y
        elif touched_zones == [3, 1, 2, 0]:
            mask = SWAP_XY | REVERSE_X | REVERSE_Y
        else:
            print("Invalid touch sequence. Starting over...\n")
            return False

        touch_rotation_table.append(mask)
        print(f"{rotation=} {mask=} ({mask:#05b})\n")

    if not demo:
        set_rotation_table(touch_rotation_table)
        print("Set the `touch_rotation_table` in board_config.py to the following:")
    else:
        print("Demo complete.")
    print(f"    touch_rotation_table = {tuple(touch_rotation_table)}")
    return True


if not demo:
    set_rotation_table((0, 0, 0, 0))

completed = False
while not completed:
    completed = loop()
