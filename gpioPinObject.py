"""
GPIO pin abstraction for Blinka/CircuitPython digital I/O.

Author: You | Date: 2026-07-01 | Hardware Version: v0.1

Purpose:
--------
Provides a small wrapper around Blinka's digitalio.DigitalInOut object.

This allows the rest of the code to refer to GPIO pins using simple
GPIO numbers like 18 instead of requiring board.D18 directly.

Important:
----------
The numbers used here are GPIO numbers, not physical board pin numbers.
For example, GPIO18 is physical pin 12 on the Raspberry Pi.
"""

import board
import digitalio


class GPIOPin:
    """
    GPIO pin object for digital input or digital output control.

    Parameters
    ----------
    gpio_number : int
        Raspberry Pi GPIO number, such as 18 for board.D18.

    direction : str
        Pin direction. Must be either:
        - "out" for output pins
        - "in" for input pins

    Returns
    -------
    GPIOPin
        A GPIOPin object that owns and controls one Blinka digital pin.
    """

    def __init__(self, gpio_number: int, direction: str):

        # Check direction before claiming the pin so invalid setup fails early
        if direction not in ["in", "out"]:
            raise ValueError("Direction must be either 'in' or 'out'.")

        self.gpio_number = gpio_number  # stores the user-facing GPIO number
        self.direction = direction      # stores whether this pin is input or output

        # Convert a number like 18 into the matching Blinka board pin name, board.D18
        try:
            self.board_pin = getattr(board, f"D{gpio_number}")

        except AttributeError:
            raise ValueError(f"GPIO{gpio_number} is not a valid board.D pin on this board.")

        # Claim the physical GPIO pin through Blinka
        self._pin = digitalio.DigitalInOut(self.board_pin)

        # Configure the pin as an output if this object will send a signal
        if direction == "out":
            self._pin.direction = digitalio.Direction.OUTPUT
            self._pin.value = False  # initialize output pins to LOW for safety

        # Configure the pin as an input if this object will read a signal
        elif direction == "in":
            self._pin.direction = digitalio.Direction.INPUT

    def set(self, value: bool):
        """
        Set an output pin HIGH or LOW.

        Parameters
        ----------
        value : bool
            True sets the pin HIGH.
            False sets the pin LOW.

        Returns
        -------
        None
        """

        # Prevent accidental writes to input pins
        if self.direction != "out":
            raise RuntimeError(f"GPIO{self.gpio_number} is not an output pin.")

        # Convert value to bool so values like 1 or 0 are handled safely
        self._pin.value = bool(value)

    def read(self) -> bool:
        """
        Read the current pin value.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            Current digital value of the pin.
        """

        return self._pin.value

    def deinit(self):
        """
        Release the pin from Blinka control.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self._pin.deinit()