"""
Abstract Module Base Class.

Author: Jack A. D'Amelio | Date: 2026-07-1 | Hardware Version: v0.1

Purpose:
--------
Defines the common interface that every hardware module in the
control system must implement.

Using an abstract base class ensures that all modules expose the
same set of properties and methods. This allows the controller to
interact with different hardware (LEDs, sensors, motors, etc.)
without needing to know their implementation details.

All modules must implement:
- name (str): human-readable identifier
- pins (dict): hardware pin mapping
- read() (function): returns the current measurement or state
- cleanup() (function): releases hardware resources before shutdown
"""

from abc import ABC, abstractmethod


# =========================================================
# ABSTRACT MODULE BASE CLASS
# =========================================================

class Module(ABC):
    """
    Base class for all hardware modules.

    Every hardware module should inherit from this class.
    Python prevents subclasses from being instantiated until
    all abstract methods have been implemented, ensuring a
    consistent interface throughout the project.
    """

    def __init__(self):
        """
        Base initializer for shared module setup.

        Parameters:
            None

        Returns:
            None

        Currently empty, but reserved for future shared
        functionality such as:
        - logging registration
        - hardware initialization
        - calibration setup
        - configuration validation
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: IDENTIFICATION
    # =========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the human-readable name of the module.

        Returns:
            str: Module name displayed to users and used
                throughout the control software.
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: HARDWARE CONFIGURATION
    # =========================================================

    @property
    @abstractmethod
    def pins(self) -> dict:
        """
        Returns the hardware pin assignments used by the module.

        Returns:
            dict: Dictionary describing hardware pin connections.

        Example:
            {
                "sda": 2,
                "scl": 3
            }

        The exact keys depend on the hardware implementation.
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: DATA ACQUISITION
    # =========================================================

    @abstractmethod
    def read(self):
        """
        Reads the current state or measurement from the module.

        Returns:
            dict | float | int | object:
                Module-specific measurement data.

        Notes:
            - Each module defines its own return format.
            - Returning a dictionary is recommended because it
              makes combining data from multiple modules easier.
        """
        pass

    # =========================================================
    # REQUIRED INTERFACE: RESOURCE CLEANUP
    # =========================================================

    @abstractmethod
    def cleanup(self):
        """
        Releases any hardware resources used by the module.

        This method is called before shutting down the program or
        unloading a module. It provides an opportunity to safely
        reset GPIO pins, close communication interfaces, or stop
        background processes.

        Returns:
            None
        """
        pass