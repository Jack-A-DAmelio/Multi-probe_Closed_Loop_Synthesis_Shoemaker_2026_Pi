"""
GPIO pin abstraction for Blinka/CircuitPython digital I/O.



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

# board gives access to the Raspberry Pi pin names that Blinka understands,
# such as board.D18, board.D23, and board.D24.
import board

# digitalio gives access to DigitalInOut, Direction.OUTPUT, Direction.INPUT,
# and the .value property used to set or read digital HIGH/LOW signals.
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
        """
        Create one GPIOPin object.

        Parameters
        ----------
        gpio_number : int
            Raspberry Pi GPIO number, such as 18.

        direction : str
            Direction for the pin. Must be "out" or "in".

        Returns
        -------
        None

        Notes
        -----
        self means the specific GPIOPin object being created.
        gpio_number: int and direction: str are type hints.
        They describe what data type is expected, but they do not
        automatically convert the values.
        """

        # Check direction before claiming the pin so invalid setup fails early.
        # This prevents someone from typing something like "output", "send",
        # or "read" when the class only expects "out" or "in".
        if direction not in ["in", "out"]:
            raise ValueError("Direction must be either 'in' or 'out'.")

        # Store the GPIO number inside this specific object.
        # Example: if the user writes GPIOPin(18, "out"),
        # then self.gpio_number becomes 18.
        self.gpio_number = gpio_number

        # Store the direction inside this specific object.
        # Example: if the user writes GPIOPin(18, "out"),
        # then self.direction becomes "out".
        self.direction = direction

        # Convert a number like 18 into the matching Blinka board pin.
        #
        # f"D{gpio_number}" turns 18 into the string "D18".
        #
        # getattr(board, "D18") asks Python to look inside the board module
        # for the attribute called D18.
        #
        # This is the dynamic version of writing:
        # self.board_pin = board.D18
        try:
            self.board_pin = getattr(board, f"D{gpio_number}")

        # If board.D18, board.D23, etc. does not exist for the number given,
        # getattr() raises an AttributeError. This converts that into a clearer
        # error message for the user.
        except AttributeError:
            raise ValueError(f"GPIO{gpio_number} is not a valid board.D pin on this board.")

        # Claim the physical GPIO pin through Blinka.
        #
        # This is the line where the pin becomes controlled by this program.
        # Before this line, self.board_pin only refers to something like board.D18.
        # After this line, self._pin is the active DigitalInOut object.
        self._pin = digitalio.DigitalInOut(self.board_pin)

        # Configure the pin as an output if this object will send a signal.
        # Output means the Raspberry Pi can drive the pin HIGH or LOW.
        # This is the mode used for LEDs, relays, simple digital pump control,
        # and other devices that need a digital control signal.
        if direction == "out":
            self._pin.direction = digitalio.Direction.OUTPUT

            # Start output pins LOW for safety.
            # LOW means False, which is usually about 0 V.
            # This helps prevent an LED, pump, or other device from turning on
            # accidentally when the object is first created.
            self._pin.value = False

        # Configure the pin as an input if this object will read a signal.
        # Input means the Raspberry Pi watches the pin instead of driving it.
        # This would be used for buttons, switches, or digital sensors.
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

        # Only output pins are allowed to be written to.
        # If this GPIOPin was created with direction="in", writing to it would
        # not make sense because input pins are meant to read signals.
        if self.direction != "out":
            raise RuntimeError(f"GPIO{self.gpio_number} is not an output pin.")

        # Set the pin value.
        #
        # True means HIGH, usually about 3.3 V on a Raspberry Pi GPIO pin.
        # False means LOW, usually about 0 V.
        #
        # bool(value) makes sure values like 1 or 0 are converted into
        # True or False before being sent to the pin.
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

        # Return the current digital value of the pin.
        #
        # For an input pin, this reads the outside signal coming into the Pi.
        # For an output pin, this usually reflects the last value assigned.
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

        # Release the pin so another script, object, or future run can use it.
        # This is the Blinka/CircuitPython equivalent of cleaning up the pin.
        self._pin.deinit()


# The GPIOPin class creates a reusable pin object for Blinka/CircuitPython digital I/O.
# When the user creates something like GPIOPin(18, "out"),
# the class stores the GPIO number and direction inside the object.
# The getattr(board, f"D{gpio_number}") line converts the number 18 into board.D18,
# which is the form Blinka understands.
# Then digitalio.DigitalInOut(self.board_pin) claims that GPIO pin so the program can control it.
# If the direction is "out", the pin is configured as an output and starts LOW for safety.
# If the direction is "in", the pin is configured as an input so it can read a signal.
# The set() method only works for output pins and changes the pin HIGH or LOW.
# The read() method returns the current digital value.
# The deinit() method releases the pin when the program is done.