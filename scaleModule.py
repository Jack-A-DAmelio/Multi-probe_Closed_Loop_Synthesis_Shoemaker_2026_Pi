"""
Scale module using one NAU7802 ADC and one load cell.

Author: Gabriel Dennis
Date: 2026-07-07

Purpose:
--------
Provides the higher-level scale behavior for the crystal growth
control system.

This class:

- follows the Module abstract interface
- reads raw NAU7802 measurements
- stores a software tare point
- calibrates using a known mass
- converts measurements to grams
- converts measurements to kilograms
- cleans up the scale device when finished

The low-level NAU7802 communication is handled by ScaleDevice.
"""

from module_abstract import Module
from scaleDevice import ScaleDevice


class ScaleModule(Module):
    """
    Scale module using one NAU7802 ADC and one load cell.

    Parameters
    ----------
    i2c_bus
        Shared Blinka/CircuitPython I2C bus.

    name : str
        Human-readable name of the scale.

    address : int
        NAU7802 I2C address.

    samples : int
        Number of raw measurements averaged for each reading.

    Returns
    -------
    ScaleModule
        Scale object capable of returning raw and converted measurements.
    """

    def __init__(
        self,
        i2c_bus,
        name: str = "NAU7802 Scale",
        address: int = 0x2A,
        samples: int = 2,
    ):
        """
        Create one scale module.
        """

        # Run the Module parent initializer.
        super().__init__()

        # Store the human-readable name of this scale.
        self._name = name

        # Store the Raspberry Pi GPIO numbers used by the I2C bus.
        #
        # GPIO2 is SDA.
        # GPIO3 is SCL.
        self._pins = {
            "sda": 2,
            "scl": 3,
        }

        # Create the low-level ScaleDevice object.
        #
        # ScaleModule does not directly create or control
        # the NAU7802 library object.
        #
        # ScaleDevice handles that responsibility.
        self._device = ScaleDevice(
            i2c_bus=i2c_bus,
            address=address,
            samples=samples,
        )

        # Raw ADC value representing the software zero point.
        #
        # None means the scale has not been tared yet.
        self._tare_raw = None

        # Number of raw ADC counts corresponding to one gram.
        #
        # None means the scale has not been calibrated
        # using a known mass yet.
        self._counts_per_gram = None

    @property
    def name(self) -> str:
        """
        Return the human-readable scale name.

        Returns
        -------
        str
            Name of the scale.
        """

        return self._name

    @property
    def pins(self) -> dict:
        """
        Return the scale's hardware communication pins.

        Returns
        -------
        dict
            Dictionary containing SDA and SCL GPIO numbers.
        """

        return self._pins

    @property
    def calibration_factor(self):
        """
        Return the current calibration factor.

        Returns
        -------
        float or None
            Raw ADC counts per gram.
        """

        return self._counts_per_gram

    @property
    def tare_raw(self):
        """
        Return the current raw tare value.

        Returns
        -------
        int or None
            Raw ADC value stored as zero mass.
        """

        return self._tare_raw

    def zero_adc(self) -> dict:
        """
        Perform the NAU7802's internal ADC calibration.

        This is different from taring the scale.

        Returns
        -------
        dict
            Internal and offset calibration results.
        """

        return self._device.calibrate_adc()

    def read_raw(self, samples: int = None) -> int:
        """
        Read the raw ADC measurement.

        Parameters
        ----------
        samples : int or None
            Number of measurements to average.

        Returns
        -------
        int
            Averaged raw ADC value.
        """

        return self._device.read_raw(samples=samples)

    def tare(self, samples: int = None) -> int:
        """
        Set the current scale load as zero mass.

        Parameters
        ----------
        samples : int or None
            Number of measurements to average when establishing
            the zero point.

        Returns
        -------
        int
            Raw ADC value stored as the tare point.
        """

        # Read the current scale output.
        self._tare_raw = self._device.read_raw(
            samples=samples
        )

        # Return the stored tare value.
        return self._tare_raw

    def calibrate(
        self,
        known_mass_grams: float,
        samples: int = None,
    ) -> float:
        """
        Calibrate the scale using a known mass.

        The scale must be tared before this method is called.

        Parameters
        ----------
        known_mass_grams : float
            Known calibration mass in grams.

        samples : int or None
            Number of raw measurements to average.

        Returns
        -------
        float
            Calibration factor in raw ADC counts per gram.
        """

        # A zero or negative calibration mass is invalid.
        if known_mass_grams <= 0:
            raise ValueError(
                "Known calibration mass must be greater than zero."
            )

        # The scale needs a zero reference before we can determine
        # how much the raw ADC reading changed.
        if self._tare_raw is None:
            raise RuntimeError(
                "The scale must be tared before calibration."
            )

        # Measure the raw ADC output while the known mass
        # is sitting on the scale.
        loaded_raw = self._device.read_raw(
            samples=samples
        )

        # Find the change in raw ADC counts caused by
        # the known calibration mass.
        raw_difference = loaded_raw - self._tare_raw

        # Prevent division by zero when the reading did not change.
        if raw_difference == 0:
            raise RuntimeError(
                "Calibration failed because the raw reading did not change."
            )

        # Calculate the calibration factor:
        #
        # raw ADC counts per gram
        self._counts_per_gram = (
            raw_difference / known_mass_grams
        )

        # Return the calibration factor.
        return self._counts_per_gram

    def read(self) -> dict:
        """
        Read the current scale measurement.

        Returns
        -------
        dict
            Dictionary containing:

            raw
                Raw averaged ADC reading.

            grams
                Converted mass in grams.
                None if calibration has not been completed.

            kilograms
                Converted mass in kilograms.
                None if calibration has not been completed.
        """

        # Get the current raw ADC reading.
        raw_value = self._device.read_raw()

        # Raw readings are still useful before calibration.
        #
        # Therefore, return the raw reading even when grams and
        # kilograms cannot yet be calculated.
        if (
            self._tare_raw is None
            or self._counts_per_gram is None
        ):
            return {
                "raw": raw_value,
                "grams": None,
                "kilograms": None,
            }

        # Subtract the zero point and divide by
        # raw ADC counts per gram.
        grams = (
            raw_value - self._tare_raw
        ) / self._counts_per_gram

        # Convert grams to kilograms.
        kilograms = grams / 1000.0

        # Return all useful forms of the measurement.
        return {
            "raw": raw_value,
            "grams": grams,
            "kilograms": kilograms,
        }

    def cleanup(self):
        """
        Clean up resources used by the scale.

        Returns
        -------
        None
        """

        # Tell ScaleDevice to disable the NAU7802.
        self._device.deinit()