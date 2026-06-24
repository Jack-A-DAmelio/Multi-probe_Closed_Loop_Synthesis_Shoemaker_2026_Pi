"""
Hardware Pin Abstraction.

Author: Jack A. D'Amelio | Date: 2026-06-24 | Hardware Version: v0.1

Purpose:
--------
Represents a single physical hardware pin used by probes.

Each pin stores:
- address (hardware identifier)
- human-readable name
- usage description
- basic read/write operations (if supported by backend driver)
"""

# =========================================================
# PIN CLASS
# =========================================================

class Pin:
    """
    Represents a single hardware pin.

    This class is not abstract because:
    - pins are concrete hardware objects
    - behavior is consistent across all usage contexts
    """

    def __init__(self, address: int, name: str, description: str):
        """
        Parameters:
            address (int):
                Hardware address / GPIO / I2C / ADC channel identifier

            name (str):
                Human-readable name for debugging and logs

            description (str):
                Explanation of what this pin is used for
        """

        self.address = address
        self.name = name
        self.description = description

        # Optional cached state (useful for debugging or buffering)
        self._last_value = None

    # =========================================================
    # READ OPERATION
    # =========================================================

    def read(self):
        """
        Reads the current value from the hardware pin.

        Returns:
            float | int | bool | None:
                Raw value from hardware interface
        """

        try:
            # -----------------------------------------------------
            # Placeholder hardware access
            # Replace with real driver call later
            # -----------------------------------------------------

            value = self._hardware_read()

            self._last_value = value
            return value

        except Exception as e:
            print(f"[PIN READ ERROR] {self.name} ({self.address}): {e}")
            return None

    # =========================================================
    # WRITE OPERATION
    # =========================================================

    def set(self, value):
        """
        Writes a value to the pin (if supported).

        Parameters:
            value (int | float | bool):
                Value to write to hardware

        Returns:
            bool:
                True if successful, False otherwise
        """

        try:
            self._hardware_write(value)
            self._last_value = value
            return True

        except Exception as e:
            print(f"[PIN WRITE ERROR] {self.name} ({self.address}): {e}")
            return False

    # =========================================================
    # INTERNAL HARDWARE INTERFACE (PLACEHOLDER)
    # =========================================================

    def _hardware_read(self):
        """
        Internal hardware read stub.

        Replace this with:
        - GPIO read (Raspberry Pi)
        - ADC read (MCP3008, ADS1115, etc.)
        - I2C/SPI read

        Returns:
            raw hardware value
        """
        raise NotImplementedError("Hardware read not implemented")

    def _hardware_write(self, value):
        """
        Internal hardware write stub.

        Replace with actual driver implementation.
        """
        raise NotImplementedError("Hardware write not implemented")