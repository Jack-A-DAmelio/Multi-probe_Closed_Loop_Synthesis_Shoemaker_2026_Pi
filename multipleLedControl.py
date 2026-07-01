"""
Multiple LED module using Blinka/CircuitPython digital I/O.


Purpose:
--------
Defines an LED module that follows the shared Module interface.

This module receives simple GPIO numbers from external code, creates
GPIOPin objects internally, and controls multiple LEDs through Blinka
digital output pins.
"""

# time is used so LEDs can stay on or off for a set number of seconds
# during blink_led(), blink_all(), and blink_sequence().
import time

# Module is the shared abstract class that all hardware modules are expected
# to follow. This keeps the LED module consistent with other future modules.
from module_abstract import Module

# GPIOPin is our custom pin abstraction.
# It lets this file use simple GPIO numbers like 18 instead of directly using board.D18.
from gpioPinObject import GPIOPin


class MultiLEDModule(Module):
    """
    LED hardware module implementing the standard Module interface.

    Parameters
    ----------
    pin_map : dict
        Dictionary mapping readable LED names to GPIO numbers.

        Example:
            {
                "status_led": 18,
                "warning_led": 23,
                "ready_led": 24
            }

    name : str
        Human-readable name for this module.

    Returns
    -------
    MultiLEDModule
        A module object that can turn LEDs on, turn LEDs off, blink one LED,
        blink all LEDs, blink LEDs in a sequence, report the last commanded
        state, and release GPIO pins during cleanup.
    """

    def __init__(self, pin_map: dict, name: str = "Multi LED Module"):
        """
        Create one multi LED module object.

        Parameters
        ----------
        pin_map : dict
            Dictionary where each key is a readable LED label and each value
            is a Raspberry Pi GPIO number.

            Example:
                {
                    "status_led": 18,
                    "warning_led": 23,
                    "ready_led": 24
                }

        name : str
            Human-readable name for this module.

        Returns
        -------
        None

        Notes
        -----
        self means the specific MultiLEDModule object being created.
        pin_map: dict and name: str are type hints. They describe what data
        types are expected, but they do not automatically convert values.
        """

        # Run setup from the parent Module class.
        # This matters because MultiLEDModule is built from Module.
        super().__init__()

        # Check that the user actually supplied at least one LED.
        # An empty pin_map would create a module that has nothing to control.
        if not pin_map:
            raise ValueError("pin_map must contain at least one LED name and GPIO number.")

        # Store the module name inside this object.
        # This allows the name property to return the module's readable name later.
        self._name = name

        # Create an empty dictionary that will store GPIOPin objects.
        # Example after setup:
        # self._pins["status_led"] = GPIOPin(18, "out")
        # self._pins["warning_led"] = GPIOPin(23, "out")
        self._pins = {}

        # Create an empty dictionary that will store the last commanded LED states.
        # This is not reading voltage from the hardware directly.
        # It stores what the code last told each LED to do.
        self._state = {}

        # Go through each LED listed in pin_map.
        #
        # Example:
        # If pin_map is {"status_led": 18, "warning_led": 23}, then:
        # first loop:
        #     led_name becomes "status_led"
        #     gpio_number becomes 18
        # second loop:
        #     led_name becomes "warning_led"
        #     gpio_number becomes 23
        for led_name, gpio_number in pin_map.items():

            # Create a GPIOPin object for this LED.
            #
            # Since this is an LED module, every pin passed into this module
            # is assumed to be an output pin.
            #
            # This line eventually causes GPIOPin to convert 18 into board.D18,
            # 23 into board.D23, and so on.
            pin = GPIOPin(gpio_number, direction="out")

            # Store the GPIOPin object using the readable LED name.
            #
            # This lets later methods use "status_led" or "warning_led"
            # instead of needing to know the GPIO number again.
            self._pins[led_name] = pin

            # Store the starting logical state of this LED.
            #
            # GPIOPin initializes output pins to False, meaning LOW or off.
            # So the internal state should also start as False.
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

        # Return the name stored during __init__().
        # Example: "Multi LED Module"
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

        # Return the dictionary of GPIOPin objects controlled by this module.
        #
        # Example:
        # {
        #     "status_led": GPIOPin object,
        #     "warning_led": GPIOPin object
        # }
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

        # Return a copy of self._state.
        #
        # dict(self._state) prevents outside code from directly changing
        # the module's internal state dictionary.
        #
        # Important:
        # This returns the last commanded state, not a fresh electrical
        # measurement from the physical pin.
        return dict(self._state)

    def set_led(self, led_name: str, value: bool):
        """
        Set one LED on or off.

        Parameters
        ----------
        led_name : str
            Name of the LED in self._pins, such as "status_led".

        value : bool
            True turns the LED on.
            False turns the LED off.

        Returns
        -------
        None
        """

        # Check that the requested LED name exists in this module.
        #
        # Example:
        # If the module was created with {"status_led": 18}, then
        # "status_led" is valid. If the user tries "led5", this raises an error.
        if led_name not in self._pins:
            raise ValueError(f"Unknown LED: {led_name}")

        # Use the GPIOPin object's set() method to change the physical pin.
        #
        # True means HIGH.
        # False means LOW.
        self._pins[led_name].set(value)

        # Store the last commanded value in the module state dictionary.
        #
        # bool(value) keeps the stored state as True or False even if someone
        # passes 1 or 0.
        self._state[led_name] = bool(value)

    def set_all(self, value: bool):
        """
        Set all LEDs on or off.

        Parameters
        ----------
        value : bool
            True turns all LEDs on.
            False turns all LEDs off.

        Returns
        -------
        None
        """

        # Go through every LED name stored in this module.
        #
        # This reuses set_led() so the same checking and state updating happens
        # for every LED.
        for led_name in self._pins:
            self.set_led(led_name, value)

    def blink_led(self, led_name: str, interval: float):
        """
        Blink one LED once.

        Parameters
        ----------
        led_name : str
            Name of the LED in self._pins, such as "status_led".

        interval : float
            Number of seconds to stay on and then stay off.

        Returns
        -------
        None
        """

        # Turn the selected LED on.
        self.set_led(led_name, True)

        # Keep the selected LED on for the requested number of seconds.
        time.sleep(interval)

        # Turn the selected LED off.
        self.set_led(led_name, False)

        # Keep the selected LED off for the requested number of seconds.
        time.sleep(interval)

    def blink_all(self, interval: float):
        """
        Blink all LEDs at the same time once.

        Parameters
        ----------
        interval : float
            Number of seconds all LEDs stay on and then stay off.

        Returns
        -------
        None
        """

        # Turn every LED on at the same time.
        self.set_all(True)

        # Keep all LEDs on for the requested number of seconds.
        time.sleep(interval)

        # Turn every LED off at the same time.
        self.set_all(False)

        # Keep all LEDs off for the requested number of seconds.
        time.sleep(interval)

    def blink_sequence(self, interval: float):
        """
        Blink each LED one at a time.

        Parameters
        ----------
        interval : float
            Number of seconds each LED stays on and then off before moving
            to the next LED.

        Returns
        -------
        None
        """

        # Go through the LEDs in the order they were added to pin_map.
        #
        # Example:
        # If pin_map was {"status_led": 18, "warning_led": 23},
        # status_led blinks first, then warning_led blinks second.
        for led_name in self._pins:
            self.blink_led(led_name, interval)

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

        # Go through only the pins created by this module.
        #
        # This is important because cleanup should not affect unrelated GPIO pins
        # that another module or script may be using.
        for led_name, pin in self._pins.items():

            # Turn the LED off before releasing the pin.
            # This leaves the hardware in a safer final state.
            pin.set(False)

            # Release the GPIO pin from Blinka control.
            #
            # This is the cleanup step that allows another script or later run
            # to use the same pin again.
            pin.deinit()

            # Update the stored state so read() agrees with the cleanup action.
            self._state[led_name] = False


# Summary:
# The MultiLEDModule class creates a reusable LED module object.
# When the user creates something like MultiLEDModule({"status_led": 18, "warning_led": 23}),
# the class loops through the dictionary and creates one GPIOPin object for each GPIO number.
# The GPIOPin object handles the lower-level Blinka setup.
# This module keeps track of each LED by its readable name.
# The set_led() method turns one named LED on or off.
# The set_all() method turns all LEDs on or off together.
# The blink_led() method blinks one named LED.
# The blink_all() method blinks all LEDs at the same time.
# The blink_sequence() method blinks each LED one at a time.
# The read() method returns the last commanded state of every LED.
# The cleanup() method turns off and releases only the pins this module created.