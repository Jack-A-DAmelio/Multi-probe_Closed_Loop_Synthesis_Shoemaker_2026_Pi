"""
NAU7802 scale module for one load cell.

This file contains both:
1. The low-level NAU7802 hardware setup.
2. The high-level methods used by the runner.

The user supplies a configuration dictionary. The class gets the scale name,
wiring information, I2C address, channel, and sample count from that dictionary.

The power, ground, SDA, and SCL entries are stored for wiring reference.
board.I2C() automatically uses the Raspberry Pi default I2C pins:
GPIO2 for SDA and GPIO3 for SCL.
"""

from copy import deepcopy
from datetime import datetime
import time

import board
from cedargrove_nau7802 import NAU7802

from module_abstract import Module


class ScaleModule(Module):
    """Control one NAU7802 channel connected to one load cell."""

    DEFAULT_I2C_ADDRESS = 0x2A
    DEFAULT_SAMPLES = 2
    DEFAULT_ACTIVE_CHANNELS = 1
    DEFAULT_CHANNEL = 1

    DEFAULT_SDA_GPIO = 2
    DEFAULT_SCL_GPIO = 3

    def __init__(self, scale_config: dict):
        """Create and enable one scale from a configuration dictionary."""
        super().__init__()

        if not isinstance(scale_config, dict):
            raise TypeError("scale_config must be a dictionary.")

        if "name" not in scale_config:
            raise ValueError("scale_config must contain a 'name'.")

        name = scale_config["name"]

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "scale_config['name'] must be a nonempty string."
            )

        if "pins" not in scale_config:
            raise ValueError(
                "scale_config must contain a 'pins' dictionary."
            )

        pin_map = scale_config["pins"]

        if not isinstance(pin_map, dict):
            raise TypeError(
                "scale_config['pins'] must be a dictionary."
            )

        for pin_name in ("sda", "scl"):
            if pin_name not in pin_map:
                raise ValueError(
                    f"scale_config['pins'] must contain a "
                    f"'{pin_name}' entry."
                )

            pin_config = pin_map[pin_name]

            if not isinstance(pin_config, dict):
                raise TypeError(
                    f"scale_config['pins']['{pin_name}'] must be "
                    f"a dictionary."
                )

            if "gpio" not in pin_config:
                raise ValueError(
                    f"scale_config['pins']['{pin_name}'] must contain "
                    f"a 'gpio' number."
                )

            gpio_number = pin_config["gpio"]

            if isinstance(gpio_number, bool) or not isinstance(
                gpio_number,
                int,
            ):
                raise TypeError(
                    f"scale_config['pins']['{pin_name}']['gpio'] "
                    f"must be an integer GPIO number."
                )

        sda_gpio = pin_map["sda"]["gpio"]
        scl_gpio = pin_map["scl"]["gpio"]

        # board.I2C() does not read arbitrary GPIO numbers from the directory.
        # It uses the Raspberry Pi default hardware I2C pins. These checks stop
        # the directory from claiming different pins than the code actually uses.
        if sda_gpio != self.DEFAULT_SDA_GPIO:
            raise ValueError(
                "ScaleModule uses board.I2C(), so SDA must be GPIO2."
            )

        if scl_gpio != self.DEFAULT_SCL_GPIO:
            raise ValueError(
                "ScaleModule uses board.I2C(), so SCL must be GPIO3."
            )

        address = scale_config.get(
            "i2c_address",
            self.DEFAULT_I2C_ADDRESS,
        )

        if isinstance(address, bool) or not isinstance(address, int):
            raise TypeError("i2c_address must be an integer.")

        if not 0x08 <= address <= 0x77:
            raise ValueError(
                "i2c_address must be a valid 7-bit I2C address."
            )

        samples = scale_config.get(
            "samples",
            self.DEFAULT_SAMPLES,
        )

        if isinstance(samples, bool) or not isinstance(samples, int):
            raise TypeError("samples must be an integer.")

        if samples <= 0:
            raise ValueError("samples must be greater than zero.")

        active_channels = scale_config.get(
            "active_channels",
            self.DEFAULT_ACTIVE_CHANNELS,
        )

        if isinstance(active_channels, bool) or not isinstance(
            active_channels,
            int,
        ):
            raise TypeError("active_channels must be an integer.")

        if active_channels not in (1, 2):
            raise ValueError("active_channels must be either 1 or 2.")

        channel = scale_config.get(
            "channel",
            self.DEFAULT_CHANNEL,
        )

        if isinstance(channel, bool) or not isinstance(channel, int):
            raise TypeError("channel must be an integer.")

        if channel not in (1, 2):
            raise ValueError("channel must be either 1 or 2.")

        if channel > active_channels:
            raise ValueError(
                "channel cannot be greater than active_channels."
            )

        self._name = name.strip()
        self._config = deepcopy(scale_config)
        self._pins = deepcopy(pin_map)
        self._address = address
        self._samples = samples
        self._active_channels = active_channels
        self._channel = channel
        self._last_measurement = None
        self._enabled = False
        self._cleaned_up = False

        # board.I2C() selects the Raspberry Pi default I2C bus.
        # On a Raspberry Pi 4, that normally means GPIO2 for SDA
        # and GPIO3 for SCL.
        self._i2c = board.I2C()

        try:
            self._nau7802 = NAU7802(
                self._i2c,
                address=self._address,
                active_channels=self._active_channels,
            )

            self._nau7802.channel = self._channel
            self._enabled = bool(self._nau7802.enable(True))

            if not self._enabled:
                raise RuntimeError(
                    "NAU7802 digital and analog power could not be enabled."
                )

        except Exception:
            if getattr(self, "_enabled", False):
                self._nau7802.enable(False)
                self._enabled = False

            self._cleaned_up = True
            raise

    @property
    def name(self) -> str:
        """Return the scale name stored in the directory."""
        return self._name

    @property
    def pins(self) -> dict:
        """Return a copy of the scale wiring dictionary."""
        return deepcopy(self._pins)

    @property
    def address(self) -> int:
        """Return the configured I2C address."""
        return self._address

    @property
    def channel(self) -> int:
        """Return the selected NAU7802 channel."""
        return self._channel

    @property
    def samples(self) -> int:
        """Return the default sample count."""
        return self._samples

    @property
    def last_measurement(self):
        """Return the most recent measurement, or None."""
        if self._last_measurement is None:
            return None

        return dict(self._last_measurement)

    def _require_active(self) -> None:
        """Prevent hardware access after cleanup."""
        if self._cleaned_up or not self._enabled:
            raise RuntimeError(
                f"{self._name} is not active."
            )

    def zero_adc(self) -> dict:
        """
        Run the NAU7802 internal and offset calibration procedures.

        Remove all weight from the load cell before calling this method.
        This is ADC calibration, not mass calibration in grams.
        """
        self._require_active()
        self._nau7802.channel = self._channel

        internal_success = bool(
            self._nau7802.calibrate("INTERNAL")
        )
        offset_success = bool(
            self._nau7802.calibrate("OFFSET")
        )

        return {
            "internal": internal_success,
            "offset": offset_success,
        }

    def read_raw(self, samples: int = None) -> int:
        """Read and average raw NAU7802 measurements."""
        self._require_active()

        if samples is None:
            sample_count = self._samples
        else:
            sample_count = samples

        if isinstance(sample_count, bool) or not isinstance(
            sample_count,
            int,
        ):
            raise TypeError("samples must be an integer.")

        if sample_count <= 0:
            raise ValueError("samples must be greater than zero.")

        self._nau7802.channel = self._channel
        sample_sum = 0

        for _ in range(sample_count):
            while not self._nau7802.available():
                time.sleep(0.001)

            sample_sum += self._nau7802.read()

        return int(sample_sum / sample_count)

    def read(self, samples: int = None) -> dict:
        """
        Read the scale and return the channel, raw value, and timestamp.
        """

        raw_value = self.read_raw(samples=samples)

        return {
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "channel": self._channel,
            "raw": raw_value,
        }

    def cleanup(self) -> None:
        """Disable the NAU7802 digital and analog systems."""
        if self._cleaned_up:
            return

        if self._enabled:
            self._nau7802.enable(False)
            self._enabled = False

        self._cleaned_up = True
