"""Example runner for one configured NAU7802 scale."""

import time

from scaleDirectory2 import SCALE_DIRECTORY
from scaleModule2 import ScaleModule


SCALE_KEY = "crystal_growth_scale"


def main() -> None:
    """Create, calibrate, read, and clean up one scale."""
    scale_config = SCALE_DIRECTORY[SCALE_KEY]
    scale = ScaleModule(scale_config)

    try:
        print("*** Scale setup")
        print(f"Name: {scale.name}")
        print(f"I2C address: 0x{scale.address:02X}")
        print(f"NAU7802 channel: {scale.channel}")
        print(f"Samples per reading: {scale.samples}")
        print(f"Wiring directory: {scale.pins}")
        print()

        input(
            "Remove all weight from the load cell, then press Enter "
            "to calibrate the ADC."
        )

        calibration = scale.zero_adc()

        print(
            "Internal calibration:",
            calibration["internal"],
        )
        print(
            "Offset calibration:",
            calibration["offset"],
        )

        if not all(calibration.values()):
            raise RuntimeError(
                "One or more NAU7802 calibration procedures failed."
            )

        print("READY")
        print("Press Ctrl+C to stop.")

        while True:
            measurement = scale.read()

            print(
                f"channel {measurement['channel']} "
                f"raw value: {measurement['raw']}"
            )

            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")

    finally:
        scale.cleanup()
        print("Scale cleaned up.")


if __name__ == "__main__":
    main()
