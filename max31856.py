"""
Low-level MAX31856 hardware abstraction.

Purpose:
--------
Provides direct hardware communication with one MAX31856
thermocouple amplifier using Blinka and CircuitPython.

This class handles:
- creation of the default SPI bus
- creation of the chip select pin
- creation of the Adafruit MAX31856 driver object
- thermocouple type selection
- starting a one-shot measurement
- waiting for measurement completion
- reading the raw temperature registers
- converting the registers into a signed 19-bit raw code
- converting the raw code into temperature
- releasing the chip select pin during cleanup

This file is responsible for hardware-specific MAX31856 behavior.

Higher-level module behavior belongs in max31856Module.py.
"""

import board
import digitalio
import time
import adafruit_max31856


# =========================================================
# THERMOCOUPLE TYPE LOOKUP TABLE
# =========================================================

# The user can provide a readable string such as "K" or "T".
#
# The dictionary converts that string into the constant expected
# by the Adafruit MAX31856 library.
THERMOCOUPLE_TYPES = {
    "B": adafruit_max31856.ThermocoupleType.B,
    "E": adafruit_max31856.ThermocoupleType.E,
    "J": adafruit_max31856.ThermocoupleType.J,
    "K": adafruit_max31856.ThermocoupleType.K,
    "N": adafruit_max31856.ThermocoupleType.N,
    "R": adafruit_max31856.ThermocoupleType.R,
    "S": adafruit_max31856.ThermocoupleType.S,
    "T": adafruit_max31856.ThermocoupleType.T,
}


class MAX31856Hardware:
    """
    Low-level hardware interface for one MAX31856.

    Parameters
    ----------
    cs_gpio : int
        Raspberry Pi GPIO number used for chip select.

        Example:
            5 means board.D5.

    thermocouple_type : str
        Thermocouple type.

        Supported values:
            "B"
            "E"
            "J"
            "K"
            "N"
            "R"
            "S"
            "T"

        Default:
            "K"

    Returns
    -------
    MAX31856Hardware
        Object that owns the MAX31856 hardware connection.
    """

    # The MAX31856 thermocouple temperature registers begin
    # at register address 0x0C.
    TEMPERATURE_REGISTER_START = 0x0C

    # Each raw MAX31856 temperature count represents
    # 0.0078125 degrees Celsius.
    TEMPERATURE_RESOLUTION = 0.0078125

    def __init__(
        self,
        cs_gpio: int,
        thermocouple_type: str = "K"
    ):
        """
        Create the MAX31856 hardware connection.

        Parameters
        ----------
        cs_gpio : int
            GPIO number used for chip select.

        thermocouple_type : str
            Thermocouple type.

        Returns
        -------
        None
        """

        # Make sure thermocouple_type is a string before
        # trying to call .upper() on it.
        if not isinstance(thermocouple_type, str):
            raise TypeError(
                "thermocouple_type must be a string such as 'K' or 'T'."
            )

        # Convert lowercase input into uppercase.
        #
        # Example:
        # "k" becomes "K"
        thermocouple_type = thermocouple_type.upper()

        # Check that the requested thermocouple type exists.
        if thermocouple_type not in THERMOCOUPLE_TYPES:
            raise ValueError(
                f"Unsupported thermocouple type: {thermocouple_type}"
            )

        # Store the GPIO number used for chip select.
        self.cs_gpio = cs_gpio

        # Store the readable thermocouple type.
        self.thermocouple_type = thermocouple_type

        # Track whether cleanup has already happened.
        #
        # This prevents repeated cleanup calls from trying
        # to deinitialize the CS pin multiple times.
        self._is_deinitialized = False

        # Convert an integer such as 5 into board.D5.
        #
        # f"D{cs_gpio}" creates the string "D5".
        #
        # getattr(board, "D5") retrieves board.D5.
        try:
            self._cs_board_pin = getattr(
                board,
                f"D{cs_gpio}"
            )

        except AttributeError as error:
            raise ValueError(
                f"GPIO{cs_gpio} is not a valid board.D pin on this board."
            ) from error

        # Create the default SPI bus.
        #
        # The MAX31856 will communicate through:
        # SCLK
        # MOSI
        # MISO
        self._spi = board.SPI()

        # Claim the GPIO pin that will be used for chip select.
        self._cs = digitalio.DigitalInOut(
            self._cs_board_pin
        )

        # Configure chip select as an output.
        self._cs.direction = digitalio.Direction.OUTPUT

        # Chip select is active LOW.
        #
        # HIGH means the MAX31856 is not currently selected.
        # The Adafruit driver will control the pin during
        # SPI transactions.
        self._cs.value = True

        # Convert the readable thermocouple type into the
        # constant required by the Adafruit driver.
        driver_thermocouple_type = (
            THERMOCOUPLE_TYPES[self.thermocouple_type]
        )

        # Create the Adafruit MAX31856 sensor object.
        #
        # This object receives:
        # 1. the SPI bus
        # 2. the chip select DigitalInOut object
        # 3. the thermocouple type
        try:
            self._sensor = adafruit_max31856.MAX31856(
                self._spi,
                self._cs,
                thermocouple_type=driver_thermocouple_type
            )

        # If driver creation fails, release the CS pin
        # before passing the original error upward.
        except Exception:
            self._cs.deinit()
            raise

    def read_raw_temperature_code(self) -> int:
        """
        Perform one measurement and return the signed raw code.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Signed 19-bit MAX31856 temperature code.
        """

        # Tell the MAX31856 to begin one measurement.
        self._sensor.initiate_one_shot_measurement()

        # Wait until the MAX31856 reports that the
        # one-shot measurement has completed.
        while self._sensor.oneshot_pending:
            time.sleep(0.01)

        # Read three consecutive temperature registers.
        #
        # Register 0x0C:
        #     high temperature byte
        #
        # Register 0x0D:
        #     middle temperature byte
        #
        # Register 0x0E:
        #     low temperature byte
        raw_bytes = self._sensor._read_sequential_registers(
            self.TEMPERATURE_REGISTER_START,
            3
        )

        # Separate the three bytes.
        high_byte = raw_bytes[0]
        mid_byte = raw_bytes[1]
        low_byte = raw_bytes[2]

        # Combine the three register values into one
        # 19-bit temperature code.
        raw_code = (
            (high_byte << 11)
            | (mid_byte << 3)
            | (low_byte >> 5)
        )

        # Convert the 19-bit two's complement value
        # into a normal signed Python integer.
        #
        # 0x40000 is the sign bit.
        #
        # 0x80000 represents the full 19-bit numerical range.
        if raw_code & 0x40000:
            raw_code -= 0x80000

        return raw_code

    def read_measurement(self) -> dict:
        """
        Read one complete MAX31856 measurement.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary containing:
            - raw_code
            - temperature_c
        """

        # Perform one measurement and retrieve its raw code.
        raw_code = self.read_raw_temperature_code()

        # Convert the raw code into degrees Celsius.
        temperature_c = (
            raw_code * self.TEMPERATURE_RESOLUTION
        )

        # Return both values from the same physical measurement.
        #
        # This is important because we do not want to perform
        # one conversion for the raw code and a different conversion
        # for the temperature.
        return {
            "raw_code": raw_code,
            "temperature_c": temperature_c
        }

    def read_faults(self) -> dict:
        """
        Read the current MAX31856 fault states.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            MAX31856 fault status dictionary.
        """

        return dict(self._sensor.fault)

    def deinit(self):
        """
        Release the chip select pin.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Only release the CS pin once.
        if not self._is_deinitialized:

            # Release the DigitalInOut object.
            self._cs.deinit()

            # Record that cleanup has happened.
            self._is_deinitialized = True


# Summary:
#
# MAX31856Hardware handles direct interaction with the physical
# MAX31856 thermocouple amplifier.
#
# It creates the default SPI bus and CS pin.
#
# It creates the Adafruit MAX31856 driver object.
#
# read_raw_temperature_code() performs one physical conversion,
# reads the three temperature registers, combines the bytes into
# a signed 19-bit raw code, and returns that integer.
#
# read_measurement() performs one measurement and returns both
# the raw code and the converted temperature from that same measurement.
#
# read_faults() returns the MAX31856 fault dictionary.
#
# deinit() releases the CS pin.