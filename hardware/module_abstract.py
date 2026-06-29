"""
Abstract Module Base Class.

Author: Jack A. D'Amelio | Date: 2026-06-24 | Hardware Version: v0.1

Purpose:
--------
Defines a standard interface for all hardware probes in the system.

All probes must implement:
- name (str): human-readable identifier
- pins (dict): hardware pin mapping
- read() (function): returns current measurement

This ensures consistent behavior across all sensor implementations
and allows the controller to treat all probes uniformly.
"""

from abc import ABC, abstractmethod


# =========================================================
# ABSTRACT PROBE BASE CLASS
# =========================================================

class Module(ABC):
    """
    Base class for all hardware modules.

    This class enforces a common interface for:
    - identification (name)
    - hardware configuration (pins)
    - data acquisition (read)
    """

    def __init__(self):
        """
        Base initializer for shared probe setup.

        Currently empty, but reserved for future shared functionality
        such as calibration hooks or logging registration.
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: IDENTIFICATION
    # =========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns:
            str: Human-readable name of the probe
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: HARDWARE CONFIGURATION
    # =========================================================

    @property
    @abstractmethod
    def pins(self) -> dict:
        """
        Returns:
            dict: Dictionary describing hardware pin connections

        Example:
            {
                "sda": 2,
                "scl": 3
            }
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: DATA ACQUISITION
    # =========================================================

    @abstractmethod
    def read(self):
        """
        Reads a measurement from the probe.

        Returns:
            dict | float | int | structured measurement object

        Notes:
            - Each probe defines its own return format
            - Prefer returning a dictionary for consistency
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Cleans up resources used by the probe.

        Returns:
            None
        """
        pass

        Notes:
            - Each probe defines its own return format
            - Prefer returning a dictionary for consistency
        """
        pass