from digitalioPinControl2 import OneLEDModule


blink_interval = int(input("After how many seconds do you want to blink? "))

led_module = OneLEDModule({
    "led1": 18
})

try:
    while True:
        led_module.blink_led("led1", blink_interval)

except KeyboardInterrupt:
    pass

finally:
    led_module.cleanup()