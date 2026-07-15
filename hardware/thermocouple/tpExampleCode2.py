"""
Example runner for one MAX31856 temperature probe.
"""

import time

from tempProbeDirectory2 import TEMP_PROBE_DIRECTORY
from tempProbeModule2 import TempProbeModule


temp_probe = None

try:
    probe_config = TEMP_PROBE_DIRECTORY

    temp_probe = TempProbeModule(
        probe_config=probe_config,
    )

    read_interval = probe_config.get(
        "read_interval_seconds",
        0.5,
    )

    print(f"Started: {temp_probe.name}")
    print(
        f"Thermocouple type: "
        f"{temp_probe.thermocouple_type}"
    )

    print("Wiring directory:")

    for connection_name, connection in temp_probe.pins.items():
        print(f"  {connection_name}: {connection}")

    print("Press Ctrl+C to stop.")

    while True:
        measurement = temp_probe.read()
        faults = temp_probe.read_faults()

        active_faults = [
            fault_name
            for fault_name, is_active in faults.items()
            if is_active
        ]

        print()
        print("Raw code:", measurement["raw_code"])
        print(
            "Temperature:",
            measurement["temperature_c"],
            "C",
        )

        if active_faults:
            print(
                "Active faults:",
                ", ".join(active_faults),
            )
        else:
            print("Active faults: none")

        time.sleep(read_interval)

except (KeyError, TypeError, ValueError) as error:
    print(f"Configuration error: {error}")

except KeyboardInterrupt:
    print("\nMeasurement stopped by user.")

finally:
    if temp_probe is not None:
        temp_probe.cleanup()
        print("Temperature probe cleanup complete.")
