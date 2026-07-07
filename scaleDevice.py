"""
Scale device abstraction for the NAU7802 ADC.

Author: Gabriel Dennis
Date: 2026-07-07

Purpose:
--------
Provides a small wrapper around the cedargrove_nau7802 NAU7802 object.

This class handles low-level ADC behavior:

- creating the NAU7802 object
- enabling the ADC
- calibrating the ADC
- waiting for measurements
- reading raw ADC values
- averaging raw ADC values
- disabling the ADC

Important:
----------
This class does not convert raw ADC readings into grams or kilograms.

Mass conversion, taring, and scale calibration belong in the
higher-level ScaleModule class.
"""

from cedargrove_nau7802 import NAU7802


class ScaleDevice:
    """
    Low-level object for controlling one NAU7802 ADC.

    Parameters
    ----------
    i2c_bus
        Blinka/CircuitPython I2C bus object.

    address : int
        I2C address of the NAU7802.
        Default is 0x2A.

    samples : int
        Default number of ADC measurements to average.

    Returns
    -------
    ScaleDevice
        Object representing one NAU7802 ADC used for a scale.
    """

    def __init__(
        self,
        i2c_bus,
        address: int = 0x2A,
        samples: int = 2,
    ):
        """
        Create and enable one scale device.
        """

        # Make sure the requested sample count is valid.
        if samples <= 0:
            raise ValueError("samples must be greater than zero.")

        # Store the I2C address.
        self.address = address

        # Store the default number of measurements to average.
        self.samples = samples

        # Create the actual NAU7802 library object.
        #
        # The ScaleDevice class is our wrapper.
        # NAU7802 is the class provided by the external library.
        #
        # active_channels=1 means this scale uses one
        # active NAU7802 measurement channel.
        self._nau7802 = NAU7802(
            i2c_bus,
            address=address,
            active_channels=1,
        )

        # Use channel 1 for this scale.
        self._nau7802.channel = 1

        # Enable the NAU7802 digital and analog systems.
        self._enabled = self._nau7802.enable(True)

        # Stop immediately if the ADC could not be enabled.
        if not self._enabled:
            raise RuntimeError(
                "NAU7802 digital and analog power could not be enabled."
            )

    def calibrate_adc(self) -> dict:
        """
        Perform the NAU7802 internal and offset calibration.

        The scale should not have an applied calibration mass
        when this method is called.

        Returns
        -------
        dict
            Results of the internal and offset calibration procedures.
        """

        # Perform the NAU7802 internal calibration.
        internal_success = self._nau7802.calibrate("INTERNAL")

        # Perform the NAU7802 offset calibration.
        offset_success = self._nau7802.calibrate("OFFSET")

        # Return both results in one dictionary.
        return {
            "internal": internal_success,
            "offset": offset_success,
        }

    def read_raw(self, samples: int = None) -> int:
        """
        Read and average raw ADC measurements.

        Parameters
        ----------
        samples : int or None
            Number of measurements to average.

            If None, the ScaleDevice object's default
            sample count is used.

        Returns
        -------
        int
            Averaged raw ADC value.
        """

        # Use the object's default sample count when the caller
        # does not provide a different value.
        if samples is None:
            sample_count = self.samples

        else:
            sample_count = samples

        # Prevent zero or negative sample counts.
        if sample_count <= 0:
            raise ValueError("samples must be greater than zero.")

        # Start the sum at zero.
        sample_sum = 0

        # Repeat once for each requested measurement.
        for _ in range(sample_count):

            # Wait until the NAU7802 reports that a new
            # measurement is available.
            while not self._nau7802.available():
                pass

            # Read the raw ADC value and add it to the sum.
            sample_sum += self._nau7802.read()

        # Calculate and return the average raw ADC reading.
        return int(sample_sum / sample_count)

    def deinit(self):
        """
        Disable the NAU7802 digital and analog systems.

        Returns
        -------
        None
        """

        # Only disable the device if it is currently enabled.
        if self._enabled:
            self._nau7802.enable(False)

            # Remember that the device has been disabled.
            self._enabled = False