"""
Runner file for testing OneLEDModule.


Purpose:
--------
Creates one LED module on GPIO18 and repeatedly blinks it using a
user-supplied blink interval.

This file is meant to be run directly on the Raspberry Pi.
"""

from digitalioPinControl2 import OneLEDModule


# Ask the user how long the LED should stay on and off during each blink cycle
blink_interval = int(input("After how many seconds do you want to blink? "))

# Create the LED module using GPIO18, which is physical pin 12 on the Raspberry Pi
led_module = OneLEDModule({
    "led1": 18
})

try:
    # Keep blinking until the user stops the program with Ctrl+C
    while True:
        led_module.blink_led("led1", blink_interval)

except KeyboardInterrupt:
    # Allow Ctrl+C to stop the program without printing a Python error traceback
    pass

finally:
    # Always release the GPIO pin, even if the program is interrupted
    led_module.cleanup()