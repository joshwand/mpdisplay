from board_config import display_drv

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="wheel", swapped=needs_swap, length=256, saturation=1.0)
# palette = display_drv.get_palette(name="wheel", color_depth=16, length=256)

line_height = 2

i = 0
def main():
    global i
    for color in palette:
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(0, i % display_drv.height, display_drv.width, line_height, color)
        i += line_height

def loop():
    while True:
        main()

loop()