"""
Simple test example to demonstrate the use of framebuf.FrameBuffer.
"""

from board_config import display_drv
from framebuf import FrameBuffer, RGB565
from array import array  # for defining a polygon

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

WIDTH = display_drv.width
HEIGHT = display_drv.height
FONT_WIDTH = 8

# Create a frame buffer
BPP = display_drv.color_depth // 8  # Bytes per pixel
ba = bytearray(WIDTH * HEIGHT * BPP)
fb = FrameBuffer(ba, WIDTH, HEIGHT, RGB565)

# Define color palette
pal = display_drv.get_palette(swapped=needs_swap)

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def main(
    scroll=False, animate=False, text1="framebuf", text2="simpletest", poly=triangle
):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        fb.fill(pal.BLACK)
        fb.poly(0, y, poly, pal.YELLOW, True)
        fb.fill_rect(WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, pal.GREY)
        fb.line(0, 0, WIDTH - 1, HEIGHT - 1, pal.GREEN)
        fb.rect(0, 0, 15, 15, pal.RED, True)
        fb.rect(WIDTH - 15, HEIGHT - 15, 15, 15, pal.BLUE, True)
        fb.hline(WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, pal.MAGENTA)
        fb.vline(WIDTH // 2, HEIGHT // 4, HEIGHT // 2, pal.CYAN)
        fb.pixel(WIDTH // 2, HEIGHT * 1 // 8, pal.WHITE)
        fb.ellipse(
            WIDTH // 2, HEIGHT // 2, WIDTH // 4, HEIGHT // 8, pal.BLACK, True, 0b1111
        )
        fb.text(text1, (WIDTH - FONT_WIDTH * len(text1)) // 2, HEIGHT // 2 - 8, pal.WHITE)
        fb.text(text2, (WIDTH - FONT_WIDTH * len(text2)) // 2, HEIGHT // 2, pal.WHITE)
        display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)

    fb.hline(0, 0, WIDTH, pal.BLACK)
    fb.vline(0, 0, HEIGHT, pal.BLACK)

    scroll_range = range(min(WIDTH, HEIGHT)) if scroll else [0]
    for _ in scroll_range:
        fb.scroll(1, 1)
        display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)


launch = lambda: main(animate=True)

wipe = lambda: main(scroll=True)

main()
