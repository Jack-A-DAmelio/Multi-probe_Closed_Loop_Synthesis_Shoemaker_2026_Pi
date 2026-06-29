from gpiozero import LED
from time import sleep

# Initialize the LED on GPIO 18
led = LED(18)

while True:
    led.on()      # Turn the LED on
    sleep(1)      # Wait for 1 second
    led.off()     # Turn the LED off
    sleep(1)      # Wait for 1 second
