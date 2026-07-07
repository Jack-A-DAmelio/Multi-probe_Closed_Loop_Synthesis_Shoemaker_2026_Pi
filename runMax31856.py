"""
Runner for one MAX31856 thermocouple module.

Purpose:
--------
Creates the MAX31856 module, repeatedly reads temperature data,
prints the raw code and converted temperature, and cleans up the
hardware when the program exits.
"""

import time

from max31856Module import MAX31856Module


# =========================================================
# CREATE MODULE
# =========================================================

# Create one MAX31856 module.
#
# cs_gpio=5 means the MAX31856 CS pin is connected to GPIO5.
#
# thermocouple_type="K" explicitly configures the driver
# for a K-type thermocouple.
thermocouple = MAX31856Module(
    cs_gpio=5,
    thermocouple_type="K",
    name="Crystal Growth Temperature Probe"
)


# =========================================================
# MAIN PROGRAM
# =========================================================

try:

    while True:

        # Perform one physical temperature measurement.
        measurement = thermocouple.read()

        # Retrieve values from the returned dictionary.
        raw_code = measurement["raw_code"]
        temperature_c = measurement["temperature_c"]

        # Display the results.
        print("Raw code:", raw_code)
        print("Temperature:", temperature_c, "C")
        print()

        # Wait before taking the next measurement.
        time.sleep(0.5)


# =========================================================
# KEYBOARD INTERRUPT
# =========================================================

except KeyboardInterrupt:

    print("\nMeasurement stopped by user.")


# =========================================================
# CLEANUP
# =========================================================

finally:

    # Release hardware resources owned by the module.
    thermocouple.cleanup()

    print("MAX31856 cleanup complete.")