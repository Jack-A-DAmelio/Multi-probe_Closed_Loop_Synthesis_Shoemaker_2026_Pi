import time
from module_abstract import Module
from Pin_object import Pin


class OneLEDModule(Module):
    """
    LED hardware module implementing the standard Module interface.

    Controls one LEDs using Blinka and CircuitPython digitalio.
    """

    def __init__(self, pin_map: dict,name):
        """
        pin_map format:
        {
            "led1": 18,

        }

        The numbers are GPIO numbers, not physical pin numbers.
        LEDModule assumes every pin it receives should be an output.
        """

        super().__init__()

        self._pins = {}
        self._state = {}

        #for led_name, gpio_number in pin_map.items():
            pin = Pin(gpio_number, direction="out")#all pins are initialized as off 
            self._state[led_name] = False #therfore we initialize the state to off
            self._pins[led_name] = pin #adds pin to directory of pins for this module
            

    @property
    def name(self) -> str:
        return "LED Module"

    @property
    def pins(self) -> dict:
        return self._pins

    def read(self):#Necessary for abstract class but non functional in this usage
        """
        Returns the last commanded LED states.
        """
        return dict(self._state)

    def set_led(self, led_name: str, value: bool):
        """
        Set one LED on or off.
        """
        if led_name not in self._pins:
            raise ValueError(f"Unknown LED: {led_name}")
        else:
            self._pins[led_name].set(value)
            self._state[led_name] = bool(value)

        return 



    def blink_led(self, led_name: str, interval: int):
        """
        Blink one LED once.
        """
        self.set_led(led_name, True)
        time.sleep(interval)

        self.set_led(led_name, False)
        time.sleep(interval)
        return 0

    def cleanup(self):
        """
        Turn off and release only the pins this module claimed.
        """
        for led_name, pin in self._pins.items():
            pin.set(False)
            pin.deinit()
            self._state[led_name] = False
        return 0