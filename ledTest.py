import board
import digitalio
import time

led = digitalio.DigitalInOut(board.D18)
led.direction = digitalio.Direction.OUTPUT

try:
    while True:
        led.value = True
        time.sleep(1)

        led.value = False
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    led.value = False
    led.deinit()
