import RPi.GPIO as GPIO
from module_abstract import Module
from Pin_object import Pin



class LEDModule(Module):
    """
    LED hardware module implementing the standard Module interface.

    Controls red, green, and yellow LEDs via Pin abstraction.
    """

    def __init__(self, pin_map: dict):
        """
        pin_map format:
        {
            "red": Pin(...),
            "green": Pin(...),
            "yellow": Pin(...)
        }
        """

        super().__init__()

        GPIO.setmode(GPIO.BOARD)

        self._pins = pin_map
        self._state = {k: False for k in pin_map}

        # Initialize LEDs to OFF
        for pin in self._pins.values():
            pin.set(False)

    # REQUIRED INTERFACE -----------------------------------

    @property
    def name(self) -> str:
        return "LED Module"

    @property
    def pins(self) -> dict:
        return self._pins

    def read(self):
        """
        Returns logical LED state (last commanded values).
        """
        return dict(self._state)

    # MODULE BEHAVIOR --------------------------------------

    def set_led(self, color: str, value: bool):
        """
        Set a single LED state.
        """
        if color not in self._pins:
            raise ValueError(f"Unknown LED: {color}")

        self._pins[color].set(value)
        self._state[color] = value

    def set_all(self, value: bool):
        """
        Set all LEDs simultaneously.
        """
        for color in self._pins:
            self.set_led(color, value)