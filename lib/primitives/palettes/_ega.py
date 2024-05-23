"""
The EGA 64 color palette.
"""

_colors = (
    b"\x00\x00\x00"  # 0
    b"\x00\x00\xAA"  # 1
    b"\x00\xAA\x00"  # 2
    b"\x00\xAA\xAA"  # 3
    b"\xAA\x00\x00"  # 4
    b"\xAA\x00\xAA"  # 5
    b"\xAA\xAA\x00"  # 6
    b"\xAA\xAA\xAA"  # 7
    b"\x00\x00\x55"  # 8
    b"\x00\x00\xFF"  # 9
    b"\x00\xAA\x55"  # 10
    b"\x00\xAA\xFF"  # 11
    b"\xAA\x00\x55"  # 12
    b"\xAA\x00\xFF"  # 13
    b"\xAA\xAA\x55"  # 14
    b"\xAA\xAA\xFF"  # 15
    b"\x00\x55\x00"  # 16
    b"\x00\x55\xAA"  # 17
    b"\x00\xFF\x00"  # 18
    b"\x00\xFF\xAA"  # 19
    b"\xAA\x55\x00"  # 20
    b"\xAA\x55\xAA"  # 21
    b"\xAA\xFF\x00"  # 22
    b"\xAA\xFF\xAA"  # 23
    b"\x00\x55\x55"  # 24
    b"\x00\x55\xFF"  # 25
    b"\x00\xFF\x55"  # 26
    b"\x00\xFF\xFF"  # 27
    b"\xAA\x55\x55"  # 28
    b"\xAA\x55\xFF"  # 29
    b"\xAA\xFF\x55"  # 30
    b"\xAA\xFF\xFF"  # 31
    b"\x55\x00\x00"  # 32
    b"\x55\x00\xAA"  # 33
    b"\x55\xAA\x00"  # 34
    b"\x55\xAA\xAA"  # 35
    b"\xFF\x00\x00"  # 36
    b"\xFF\x00\xAA"  # 37
    b"\xFF\xAA\x00"  # 38
    b"\xFF\xAA\xAA"  # 39
    b"\x55\x00\x55"  # 40
    b"\x55\x00\xFF"  # 41
    b"\x55\xAA\x55"  # 42
    b"\x55\xAA\xFF"  # 43
    b"\xFF\x00\x55"  # 44
    b"\xFF\x00\xFF"  # 45
    b"\xFF\xAA\x55"  # 46
    b"\xFF\xAA\xFF"  # 47
    b"\x55\x55\x00"  # 48
    b"\x55\x55\xAA"  # 49
    b"\x55\xFF\x00"  # 50
    b"\x55\xFF\xAA"  # 51
    b"\xFF\x55\x00"  # 52
    b"\xFF\x55\xAA"  # 53
    b"\xFF\xFF\x00"  # 54
    b"\xFF\xFF\xAA"  # 55
    b"\x55\x55\x55"  # 56
    b"\x55\x55\xFF"  # 57
    b"\x55\xFF\x55"  # 58
    b"\x55\xFF\xFF"  # 59
    b"\xFF\x55\x55"  # 60
    b"\xFF\x55\xFF"  # 61
    b"\xFF\xFF\x55"  # 62
    b"\xFF\xFF\xFF"  # 63
)

COLORS = memoryview(_colors)

NAMES = {
    0: "Black",
    1: "Blue",
    2: "Green",
    3: "Cyan",
    4: "Red",
    5: "Magenta",
    20: "Brown",
    7: "Light Grey",
    56: "Dark Grey",
    57: "Light Blue",
    58: "Light Green",
    59: "Light Cyan",
    60: "Light Red",
    61: "Light Magenta",
    62: "Yellow",
    63: "White",
    # : "Grey",
    52: "Orange",
    34: "Lime",
    26: "Spring Green",
    25: "Azure",
    41: "Indigo",
    44: "Rose",
    24: "Teal",
    40: "Purple",
    45: "Pink",
    55: "Light Yellow",
    32: "Dark Red",
    8: "Dark Blue",
    11: "Sky Blue",
    38: "Amber",
    43: "Blue Grey",
    48: "Olive",
    39: "Salmon",
}
