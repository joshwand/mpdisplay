# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
An example implementation of an I80 bus driver written in MicroPython.
This driver is VERY slow and is only intended as an example to be rewritten in C
or have the _write method rewritten to use DMA transfers.
"""
import machine
import struct
from lib.lcd_bus import _BaseBus, Optional
from gpio_registers import GPIO_SET_CLR_REGISTERS
from uctypes import addressof
from array import array


class I80Bus(_BaseBus):
    """
    Represents an I80 bus interface for controlling GPIO pins.
    Currently only supports 8-bit data bus width and requires pin numbers instead of pin names.
    ESP32, RP2, SAMD and NRF use pin numbers and should work with this driver.
    MIMXRT and STM use pin names and will not work with this driver until pin names are supported.

    Args:
        dc (int): The pin number for the DC pin.
        cs (int): The pin number for the CS pin.
        wr (int): The pin number for the WR pin.
        d0 - d7 (int): The pin numbers for the data pins.
        cs_active_high (bool): True if CS is active high, False if CS is active low.
        dc_data_level (int): The level for the DC pin when sending data (1 or 0).
        pclk_active_neg (bool): True if PCLK is active low, False if PCLK is active high.
        swap_color_bytes (bool): True if the color bytes should be swapped, False otherwise.
    """

    name = "MicroPython I80Bus driver"

    def __init__(
        self,
        dc,
        cs,
        wr,
        data0,
        data1,
        data2,
        data3,
        data4,
        data5,
        data6,
        data7,
        cs_active_high=False,
        dc_data_level=1,
        pclk_active_neg=False,
        swap_color_bytes=False,
    ) -> None:
        super().__init__()

        # Save the swap enabled setting for the base class
        self.swap_enabled = swap_color_bytes

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the control pins and to determine the number of pins per port for
        # _setup_data_pins() and _write()
        self.gpio = GPIO_SET_CLR_REGISTERS()

        # Configure data pins as outputs, populate lookup tables and pin_masks
        self._setup_data_pins([data0, data1, data2, data3, data4, data5, data6, data7])

        # Define the _write method
        self._use_set_clr_regs = True if self.gpio.pins_per_port == 32 else False
        self._last = (
            None  # Integer used in _write method to determine if the value has changed
        )
        self._tx_value = 0  # Integer used to hold the value to be sent

        # Set the control pins as outputs
        machine.Pin(dc, machine.Pin.OUT, value=not dc_data_level)
        machine.Pin(cs, machine.Pin.OUT, value=not cs_active_high)
        machine.Pin(wr, machine.Pin.OUT, value=pclk_active_neg)

        # Get the masks for the control pins
        self._mask_cs_active, self._mask_cs_inactive = self.gpio.get_set_clr_masks(
            cs, cs_active_high
        )
        self._mask_dc_data, self._mask_dc_cmd = self.gpio.get_set_clr_masks(
            dc, dc_data_level
        )
        self._mask_wr_inactive, self._mask_wr_active = self.gpio.get_set_clr_masks(
            wr, pclk_active_neg
        )

        # Get the register addresses for the control pins
        self._cs_active_reg, self._cs_inactive_reg = self.gpio.get_set_clr_regs(
            cs, cs_active_high
        )
        self._dc_data_reg, self._dc_cmd_reg = self.gpio.get_set_clr_regs(
            dc, dc_data_level
        )
        self._wr_inactive_reg, self._wr_active_reg = self.gpio.get_set_clr_regs(
            wr, pclk_active_neg
        )

    def _setup_data_pins(self, pins: list[int]) -> None:
        """
        Sets output mode and creates lookup_tables and pin_masks for a list pins.
        Must be called after self.gpio is initialized.
        """
        bus_width = len(pins)
        if bus_width != 8:
            raise ValueError("bus_width must be 8")

        lut_len = 2**bus_width  # 256 for 8-bit bus width

        # Set the data pins as outputs
        for pin in pins:
            machine.Pin(pin, machine.Pin.OUT)

        self._pin_masks = []  # list of 32-bit pin masks, 1 per lookup table
        self._lookup_tables = []  # list of memoryview lookup tables
        if self.gpio.pins_per_port == 32:
            self._set_regs = []  # list of 32-bit set registers, 1 per lookup table
            self._clr_regs = []  # list of 32-bit clear registers, 1 per lookup table
        else:
            self._set_reset_regs = (
                []
            )  # list of 32-bit set/reset registers, 1 per lookup table

        # Create the pin_masks and initialize the lookup_tables
        # LUT values are 32-bit, so iterate through each set of 32 pins regardless of pins_per_port
        for start_pin in range(0, max(pins), 32):
            lut_pins = [p for p in pins if p >= start_pin and p < start_pin + 32]
            pin_mask = sum([1 << (p - start_pin) for p in lut_pins]) if lut_pins else 0
            self._pin_masks.append(pin_mask)
            # print(f"lut pins = {lut_pins}; pin_mask = 0b{pin_mask:032b}")
            # append a memoryview to the lookup_tables list
            self._lookup_tables.append(
                memoryview(bytearray(lut_len * 4)) if pin_mask else None
            )
            if self.gpio.pins_per_port == 32:
                self._set_regs.append(self.gpio.set_reg(start_pin))
                self._clr_regs.append(self.gpio.clr_reg(start_pin))
            else:
                self._set_reset_regs.append(
                    [
                        self.gpio.set_reset_reg(start_pin),
                        self.gpio.set_reset_reg(start_pin + 16),
                    ]
                )

        # Populate the lookup tables
        # Iterate through all possible 8-bit values (0 to 255), assumes 8-bit bus width
        for index in range(lut_len):
            # Iterate through each pin
            for bit_number, pin in enumerate(pins):
                # If the bit is set in the index
                if index & (1 << bit_number):
                    # Set the bit in the lookup table
                    # Assuming pin and index are defined
                    byte_index = index * 4
                    value = int.from_bytes(
                        self._lookup_tables[pin // 32][byte_index : byte_index + 4],
                        "little",
                    )
                    value |= 1 << (pin % 32)
                    self._lookup_tables[pin // 32][
                        byte_index : byte_index + 4
                    ] = value.to_bytes(4, "little")

        self.num_luts = len(self._lookup_tables)

        # for i, lut in enumerate(self._lookup_tables):
        #     print(f"Lookup table {i}:")
        #     for j in range(0, lut_len):
        #         print(f"{j:03d}: 0b{int.from_bytes(lut[j*4:j*4+4], 'little'):032b}")

        # save all settings in an array for use in viper
        pin_data = array("I", [0] * self.num_luts * 4)
        for i in range(self.num_luts):
            pin_data[i * 4 + 0] = self._pin_masks[i]
            pin_data[i * 4 + 1] = (
                self._set_regs[i]
                if self.gpio.pins_per_port == 32
                else self._set_reset_regs[i][0]
            )
            pin_data[i * 4 + 2] = (
                self._clr_regs[i]
                if self.gpio.pins_per_port == 32
                else self._set_reset_regs[i][1]
            )
            pin_data[i * 4 + 3] = addressof(self._lookup_tables[i])
        self.pin_data = memoryview(pin_data)

    @micropython.native
    def tx_param(
        self, cmd: Optional[int] = None, data: Optional[memoryview] = None
    ) -> None:
        """Write to the display: command and/or data."""
        machine.mem32[self._cs_active_reg] = self._mask_cs_active  # CS Active

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
            machine.mem32[self._dc_cmd_reg] = self._mask_dc_cmd  # DC Command
            self._write(self.buf1, 1)
        if data is not None:
            machine.mem32[self._dc_data_reg] = self._mask_dc_data  # DC Data
            self._write(data, len(data))

        machine.mem32[self._cs_inactive_reg] = self._mask_cs_inactive  # CS Inactive

    @micropython.native
    def _write_slow(self, data: memoryview, length: int) -> None:
        """
        Writes data to the I80 bus interface.

        Args:
            data (memoryview): The data to be written.
        """
        for i in range(length):
            machine.mem32[self._wr_inactive_reg] = self._mask_wr_inactive  # WR Inactive
            val = data[i]  # 8-bit value (bus_width = 8)
            # No need to set the data pins again if the value hasn't changed
            if (val != self._last):
                # Iterate through each lookup table
                for n, lut in enumerate(self._lookup_tables):
                    # If the pin_mask is not 0
                    if self._pin_masks[n]:
                        # Lookup the value in the table
                        self._tx_value = int.from_bytes(lut[val * 4 : val * 4 + 4], "little")
                        if self._use_set_clr_regs:  # 32-bit ports
                            # Set the appropriate bits for all 32 pins
                            machine.mem32[self._set_regs[n]] = self._tx_value
                            # Clear the appropriate bits for all 32 pins
                            machine.mem32[self._clr_regs[n]] = (
                                self._tx_value ^ self._pin_masks[n]
                            )
                        else:  # 16-bit ports
                            # Set and clear the bits for the first 16 pins
                            machine.mem32[self._set_reset_regs[n][0]] = (
                                self._tx_value & 0xFFFF
                            ) | ((self._tx_value ^ self._pin_masks[n]) << 16)
                            # Set and clear the bits for the second 16 pins
                            machine.mem32[self._set_reset_regs[n][1]] = (
                                self._tx_value >> 16
                            ) | ((self._tx_value ^ self._pin_masks[n]) & 0xFFFF0000)
                self._last = val
            machine.mem32[self._wr_active_reg] = self._mask_wr_active  # WR Active

    @micropython.viper
    def _write(self, data: ptr8, length: int):
        _wr_inactive_reg = ptr32(self._wr_inactive_reg)
        _mask_wr_inactive = int(self._mask_wr_inactive)
        _wr_active_reg = ptr32(self._wr_active_reg)
        _mask_wr_active = int(self._mask_wr_active)
        _use_set_clr_regs = bool(self._use_set_clr_regs)

        pin_data = ptr32(self.pin_data)
        num_luts = int(self.num_luts)
        last: int = -1

        for i in range(length):
            _wr_inactive_reg[0] = _mask_wr_inactive  # WR Inactive
            val = data[i]
            if val != last:
                for n in range(num_luts):
                    pin_mask = pin_data[n * 4 + 0]
                    if pin_mask != 0:
                        set_reg = ptr32(pin_data[n * 4 + 1])
                        clr_reg = ptr32(pin_data[n * 4 + 2])
                        lut = ptr32(pin_data[n * 4 + 3])
                        tx_value: int = lut[val]
                        if True:
                            set_reg[0] = tx_value
                            clr_reg[0] = tx_value ^ pin_mask
                        else:
                            set_reg[0] = (tx_value & 0xFFFF) | ((tx_value ^ pin_mask) << 16)
                            clr_reg[0] = (tx_value >> 16) | ((tx_value ^ pin_mask) & 0xFFFF0000)
                last = val
            _wr_active_reg[0] = _mask_wr_active  # WR Active


# Example usage
# display_bus = I80Bus(
#     dc=0,
#     wr=47,
#     cs=6,
#     data0=9,
#     data1=46,
#     data2=3,
#     data3=8,
#     data4=18,
#     data5=17,
#     data6=16,
#     data7=15,
#     # freq=20000000,
#     # cmd_bits=8,
#     # param_bits=8,
#     # reverse_color_bits=False,
#     swap_color_bytes=True,
#     cs_active_high=False,
#     pclk_active_neg=False,
#     # pclk_idle_low=False,
#     # dc_idle_level=0,
#     # dc_cmd_level=0,
#     # dc_dummy_level=0,
#     dc_data_level=1,
# )
#
# display_bus.tx_param(0x36, memoryview(b'\x00\x01\x02\x03'))
