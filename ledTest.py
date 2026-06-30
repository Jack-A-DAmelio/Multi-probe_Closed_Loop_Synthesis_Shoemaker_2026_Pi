import board
import digitalio
import time

led = digitalio.DigitalInOut(board.D18)
led.direction = digitalio.Direction.OUTPUT

#get user input
blinkInterval = int(input("enter blinker interval"))
print (f"The led Blinks every,{blinkInterval}! seconds")
try:
    while True:
        led.value = True
        time.sleep(blinkInterval)

        led.value = False
        time.sleep(blinkInterval)

except KeyboardInterrupt:
    pass

finally:
    led.value = False
    led.deinit()
