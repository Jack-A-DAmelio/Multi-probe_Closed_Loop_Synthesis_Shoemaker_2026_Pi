from digitalioPinControl2 import MultiLEDModule


blink_interval = float(input("After how many seconds do you want to blink? "))

led_module = MultiLEDModule({
    "status_led": 18,
    "warning_led": 23,
    "ready_led": 24
})

try:
    while True:
        led_module.blink_sequence(blink_interval)

except KeyboardInterrupt:
    pass

finally:
    led_module.cleanup()