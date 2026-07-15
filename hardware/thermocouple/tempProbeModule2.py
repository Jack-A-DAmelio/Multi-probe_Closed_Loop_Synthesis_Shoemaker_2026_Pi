"""
MAX31856 temperature probe module, including type K.

This file contains both:
1. The low-level MAX31856 hardware setup.
2. The high-level methods used by the runner.

The user supplies a configuration dictionary. The class gets the probe
name and wiring information from that dictionary, then converts the
configured CS GPIO number into the board.D pin object required by Blinka.

The power, ground, SCK, MISO, and MOSI entries are stored for wiring
reference. board.SPI() automatically uses the Raspberry Pi default SPI
pins. Only the CS GPIO number must be converted manually.
"""

import time

import adafruit_max31856
import board
import digitalio


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


class TempProbeModule:
    """Control one MAX31856 thermocouple amplifier."""

    TEMPERATURE_REGISTER = 0x0C
    TEMPERATURE_RESOLUTION_C = 0.0078125

    def __init__(self, probe_config: dict):
        if not isinstance(probe_config, dict):
            raise TypeError("probe_config must be a dictionary.")

        if "name" not in probe_config:
            raise ValueError("probe_config must contain a 'name'.")

        name = probe_config["name"]

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "probe_config['name'] must be a nonempty string."
            )

        if "pins" not in probe_config:
            raise ValueError(
                "probe_config must contain a 'pins' dictionary."
            )

        pin_map = probe_config["pins"]

        if not isinstance(pin_map, dict):
            raise TypeError(
                "probe_config['pins'] must be a dictionary."
            )

        if "cs" not in pin_map:
            raise ValueError(
                "probe_config['pins'] must contain a 'cs' entry."
            )

        cs_config = pin_map["cs"]

        if not isinstance(cs_config, dict):
            raise TypeError(
                "probe_config['pins']['cs'] must be a dictionary."
            )

        if "gpio" not in cs_config:
            raise ValueError(
                "probe_config['pins']['cs'] must contain a 'gpio' number."
            )

        cs_gpio_number = cs_config["gpio"]

        if isinstance(cs_gpio_number, bool) or not isinstance(
            cs_gpio_number,
            int,
        ):
            raise TypeError(
                "probe_config['pins']['cs']['gpio'] must be an "
                "integer GPIO number."
            )

        thermocouple_type = probe_config.get(
            "thermocouple_type",
            "K",
        )

        if not isinstance(thermocouple_type, str):
            raise TypeError("thermocouple_type must be a string.")

        normalized_type = thermocouple_type.strip().upper()

        if normalized_type not in THERMOCOUPLE_TYPES:
            supported_types = ", ".join(THERMOCOUPLE_TYPES)

            raise ValueError(
                f"Unsupported thermocouple type "
                f"'{thermocouple_type}'. "
                f"Choose one of: {supported_types}."
            )

        self._name = name.strip()
        self._config = dict(probe_config)
        self._pins = {
            pin_name: (
                dict(pin_details)
                if isinstance(pin_details, dict)
                else pin_details
            )
            for pin_name, pin_details in pin_map.items()
        }
        self._thermocouple_type = normalized_type
        self._last_measurement = None
        self._measurement_started = False
        self._cleaned_up = False

        try:
            cs_board_pin = getattr(
                board,
                f"D{cs_gpio_number}",
            )

        except AttributeError as error:
            raise ValueError(
                f"GPIO{cs_gpio_number} does not have a matching "
                f"board.D{cs_gpio_number} pin on this board."
            ) from error

        # board.SPI() uses the Raspberry Pi default SCK, MOSI, and MISO pins.
        self._spi = board.SPI()

        # CS is the one configurable digital pin used directly by this class.
        self._cs = digitalio.DigitalInOut(cs_board_pin)
        self._cs.direction = digitalio.Direction.OUTPUT
        self._cs.value = True

        try:
            self._sensor = adafruit_max31856.MAX31856(
                self._spi,
                self._cs,
                thermocouple_type=(
                    THERMOCOUPLE_TYPES[normalized_type]
                ),
            )

        except Exception:
            self._cs.deinit()
            self._cleaned_up = True
            raise

    @property
    def name(self) -> str:
        """Return the probe name stored in the directory."""
        return self._name

    @property
    def pins(self) -> dict:
        """Return a copy of the probe wiring dictionary."""
        return {
            pin_name: (
                dict(pin_details)
                if isinstance(pin_details, dict)
                else pin_details
            )
            for pin_name, pin_details in self._pins.items()
        }

    @property
    def thermocouple_type(self) -> str:
        """Return the configured thermocouple type."""
        return self._thermocouple_type

    @property
    def last_measurement(self):
        """Return the most recent measurement, or None."""
        if self._last_measurement is None:
            return None

        return dict(self._last_measurement)

    def _require_active(self) -> None:
        """Prevent hardware access after cleanup."""
        if self._cleaned_up:
            raise RuntimeError(
                f"{self._name} has already been cleaned up."
            )

    def initiate_one_shot_measurement(self) -> None:
        """Start a new MAX31856 measurement and return immediately."""
        self._require_active()
        self._sensor.initiate_one_shot_measurement()
        self._measurement_started = True

    def one_shot_pending(self) -> bool:
        """Return True while a one-shot measurement is running."""
        self._require_active()
        return bool(self._sensor.oneshot_pending)

    def wait_for_measurement(self) -> None:
        """Wait until a previously started measurement completes."""
        self._require_active()

        if not self._measurement_started:
            raise RuntimeError(
                "No one-shot measurement has been started."
            )

        while self._sensor.oneshot_pending:
            time.sleep(0.01)

    def read_completed_raw_temperature_code(self) -> int:
        """Read the signed 19-bit raw code from a completed measurement."""
        self._require_active()

        if not self._measurement_started:
            raise RuntimeError(
                "No completed one-shot measurement is available."
            )

        if self._sensor.oneshot_pending:
            raise RuntimeError(
                "The one-shot measurement is still running."
            )

        raw_bytes = self._sensor._read_sequential_registers(
            self.TEMPERATURE_REGISTER,
            3,
        )

        high_byte = raw_bytes[0]
        middle_byte = raw_bytes[1]
        low_byte = raw_bytes[2]

        raw_code = (
            (high_byte << 11)
            | (middle_byte << 3)
            | (low_byte >> 5)
        )

        if raw_code & 0x40000:
            raw_code -= 0x80000

        self._measurement_started = False
        return raw_code

    def read_raw_temperature_code(self) -> int:
        """Start one measurement, wait, and return its raw code."""
        self.initiate_one_shot_measurement()
        self.wait_for_measurement()
        return self.read_completed_raw_temperature_code()

    @classmethod
    def raw_code_to_celsius(cls, raw_code: int) -> float:
        """Convert one signed raw code into degrees Celsius."""
        if isinstance(raw_code, bool) or not isinstance(raw_code, int):
            raise TypeError("raw_code must be an integer.")

        return raw_code * cls.TEMPERATURE_RESOLUTION_C

    def read(self) -> dict:
        """Take one measurement and return raw and Celsius readings."""
        raw_code = self.read_raw_temperature_code()

        measurement = {
            "raw_code": raw_code,
            "temperature_c": self.raw_code_to_celsius(raw_code),
        }

        self._last_measurement = dict(measurement)
        return dict(measurement)

    def read_temperature_celsius(self) -> float:
        """Take one measurement and return only degrees Celsius."""
        measurement = self.read()
        return measurement["temperature_c"]

    def read_reference_temperature_celsius(self) -> float:
        """Return the MAX31856 cold-junction temperature."""
        self._require_active()
        return float(self._sensor.reference_temperature)

    def read_faults(self) -> dict:
        """Return a dictionary of MAX31856 fault states."""
        self._require_active()
        return dict(self._sensor.fault)

    def cleanup(self) -> None:
        """Release the chip-select pin owned by this object."""
        if self._cleaned_up:
            return

        self._cs.deinit()
        self._measurement_started = False
        self._cleaned_up = True
