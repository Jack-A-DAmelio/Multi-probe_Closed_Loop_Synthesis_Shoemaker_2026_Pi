"""
MAX31856 thermocouple module.

Purpose:
--------
Defines a MAX31856 temperature measurement module that follows
the shared Module interface.

This module receives simple configuration information from
external code and uses MAX31856Hardware internally.

The lower-level hardware details are handled by:
    max31856Hardware.py

This module is responsible for:
- module identification
- reporting hardware configuration
- returning measurements in a standard dictionary
- providing fault information
- cleanup
"""

from module_abstract import Module
from max31856Hardware import MAX31856Hardware


class MAX31856Module(Module):
    """
    MAX31856 thermocouple module implementing the Module interface.

    Parameters
    ----------
    cs_gpio : int
        GPIO number used for chip select.

        Example:
            5 means board.D5.

    thermocouple_type : str
        Thermocouple type.

        Default:
            "K"

    name : str
        Human-readable name for this module.

    Returns
    -------
    MAX31856Module
        Temperature measurement module.
    """

    def __init__(
        self,
        cs_gpio: int,
        thermocouple_type: str = "K",
        name: str = "MAX31856 Thermocouple Module"
    ):
        """
        Create one MAX31856 module.

        Parameters
        ----------
        cs_gpio : int
            Raspberry Pi GPIO number used for chip select.

        thermocouple_type : str
            Thermocouple type.

        name : str
            Human-readable module name.

        Returns
        -------
        None
        """

        # Run the parent Module initializer.
        super().__init__()

        # Store the readable module name.
        self._name = name

        # Create the lower-level MAX31856 hardware object.
        #
        # This is similar to how MultiLEDModule creates
        # GPIOPin objects internally.
        self._hardware = MAX31856Hardware(
            cs_gpio=cs_gpio,
            thermocouple_type=thermocouple_type
        )

    @property
    def name(self) -> str:
        """
        Return the human-readable module name.

        Returns
        -------
        str
            Module name.
        """

        return self._name

    @property
    def pins(self) -> dict:
        """
        Return the hardware communication configuration.

        Returns
        -------
        dict
            SPI bus and chip select information.
        """

        return {
            "spi": "board.SPI()",
            "cs": self._hardware.cs_gpio
        }

    def read(self) -> dict:
        """
        Read one temperature measurement.

        Returns
        -------
        dict
            Dictionary containing:
            - raw_code
            - temperature_c
        """

        # Ask the lower-level hardware object to perform
        # the actual physical measurement.
        return self._hardware.read_measurement()

    def read_raw(self) -> int:
        """
        Read only the signed raw temperature code.

        Returns
        -------
        int
            Signed 19-bit raw temperature code.
        """

        return self._hardware.read_raw_temperature_code()

    def read_faults(self) -> dict:
        """
        Read current MAX31856 fault states.

        Returns
        -------
        dict
            MAX31856 fault status dictionary.
        """

        return self._hardware.read_faults()

    def cleanup(self):
        """
        Release hardware resources owned by this module.

        Returns
        -------
        None
        """

        self._hardware.deinit()


# Summary:
#
# MAX31856Module provides the higher-level interface used by
# the rest of the crystal growth controller.
#
# It follows the Module abstract class by providing:
#
# name
#     Human-readable module identification.
#
# pins
#     Hardware communication configuration.
#
# read()
#     Returns the raw code and temperature in a dictionary.
#
# cleanup()
#     Releases the chip select pin.
#
# The actual SPI communication and register manipulation are kept
# inside MAX31856Hardware.