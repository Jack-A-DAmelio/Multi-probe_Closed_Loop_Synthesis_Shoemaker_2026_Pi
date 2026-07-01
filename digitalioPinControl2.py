"""
One LED module using Blinka/CircuitPython digital I/O.



Purpose:
--------
Defines an LED module that follows the shared Module interface.

This module receives simple GPIO numbers from external code, creates
GPIOPin objects internally, and controls one or more LEDs through
Blinka digital output pins.
"""

import time
from module_abstract import Module
from gpioPinObject import GPIOPin


class OneLEDModule(Module):
    """
    LED hardware module implementing the standard Module interface.

    Parameters
    ----------
    pin_map : dict
        Dictionary mapping readable LED names to GPIO numbers.

        Example:
            {
                "led1": 18
            }

    name : str
        Human-readable name for this module.

    Returns
    -------
    OneLEDModule
        A module object that can turn LEDs on, turn LEDs off, blink LEDs,
        report the last commanded state, and release GPIO pins during cleanup.
    """

    def __init__(self, pin_map: dict, name: str = "One LED Module"):

        super().__init__()

        self._name = name   # stores the module name used by the name property
        self._pins = {}     # stores GPIOPin objects using readable names
        self._state = {}    # stores the last commanded state of each LED

        # Create one GPIOPin object for each LED listed in pin_map
        for led_name, gpio_number in pin_map.items():

            # LEDs send voltage out from the GPIO pin, so each LED pin is an output
            pin = GPIOPin(gpio_number, direction="out")

            # Store the pin object so later methods can control it by name
            self._pins[led_name] = pin

            # The GPIOPin object initializes output pins to LOW, so state starts as False
            self._state[led_name] = False

    @property
    def name(self) -> str:
        """
        Return the human-readable module name.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Module name.
        """

        return self._name

    @property
    def pins(self) -> dict:
        """
        Return the pins owned by this module.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary of LED names mapped to GPIOPin objects.
        """

        return self._pins

    def read(self) -> dict:
        """
        Return the last commanded LED states.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Dictionary of LED names mapped to their last commanded bool state.
        """

        # Return a copy so outside code cannot directly modify self._state
        return dict(self._state)

    def set_led(self, led_name: str, value: bool):
        """
        Set one LED on or off.

        Parameters
        ----------
        led_name : str
            Name of the LED in self._pins, such as "led1".

        value : bool
            True turns the LED on.
            False turns the LED off.

        Returns
        -------
        None
        """

        # Check that the requested LED exists before trying to control it
        if led_name not in self._pins:
            raise ValueError(f"Unknown LED: {led_name}")

        # Send the requested output value to the GPIO pin
        self._pins[led_name].set(value)

        # Store the last commanded value for read()
        self._state[led_name] = bool(value)

    def blink_led(self, led_name: str, interval: int):
        """
        Blink one LED once.

        Parameters
        ----------
        led_name : str
            Name of the LED in self._pins, such as "led1".

        interval : int
            Number of seconds to stay on and then stay off.

        Returns
        -------
        None
        """

        # Turn the LED on and keep it on for the requested interval
        self.set_led(led_name, True)
        time.sleep(interval)

        # Turn the LED off and keep it off for the requested interval
        self.set_led(led_name, False)
        time.sleep(interval)

    def cleanup(self):
        """
        Turn off and release all GPIO pins owned by this module.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Only clean up pins this module created, leaving all other GPIO pins free
        for led_name, pin in self._pins.items():

            # Turn the LED off before releasing the pin
            pin.set(False)

            # Release the pin so another script can use it later
            pin.deinit()

            # Update internal state after cleanup
            self._state[led_name] = False