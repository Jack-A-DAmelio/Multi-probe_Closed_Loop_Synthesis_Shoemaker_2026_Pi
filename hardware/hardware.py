"""
Hardware layer (MINIMAL TEST VERSION)
Author: Undergraduate Research Project
Date: 2026-06-18
Internal Pi-Hardware Version: v0.2

Purpose:
--------
Simulates multi-sensor hardware readings using modular sensor functions.

Design philosophy:
------------------
Each sensor is isolated in its own function to mimic real hardware drivers.
This makes it easy to replace simulation functions with real hardware APIs later.

The main aggregation function returns a synchronized snapshot of all sensors.
"""

import time
import random


# =========================================================
# INDIVIDUAL SENSOR FUNCTIONS
# =========================================================

def read_temperature():
    """
    Simulated temperature sensor.

    Returns:
        float: temperature in degrees Celsius
    """

    # Small random noise simulates real sensor drift
    return 20.0 + random.uniform(-2.0, 2.0)


def read_pressure():
    """
    Simulated pressure sensor.

    Returns:
        float: pressure in arbitrary units
    """

    # Baseline pressure with realistic noise envelope
    return 1.0 + random.uniform(-0.1, 0.1)


def read_ph():
    """
    Simulated pH sensor.

    Returns:
        float: pH value (nominal biological range)
    """

    # Centered around neutral pH with small fluctuations
    return 7.0 + random.uniform(-0.5, 0.5)


# =========================================================
# AGGREGATION FUNCTION
# =========================================================

def read_all_sensors():
    """
    Reads all sensors and returns a synchronized snapshot.

    Returns:
        dict: sensor snapshot containing:
            - temperature (float)
            - pressure (float)
            - pH (float)
            - timestamp (float)
    """

    # Timestamp captured once to ensure temporal consistency
    # across all sensor readings in this snapshot
    timestamp = time.time()

    return {
        "temperature": read_temperature(),
        "pressure": read_pressure(),
        "pH": read_ph(),
        "timestamp": timestamp
    }