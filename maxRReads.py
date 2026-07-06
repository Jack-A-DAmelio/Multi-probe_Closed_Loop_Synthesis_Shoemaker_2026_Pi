# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import digitalio
import time
import adafruit_max31856


# Create sensor object, communicating over the board's default SPI bus
spi = board.SPI()


# Allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT


# Create a thermocouple object
thermocouple = adafruit_max31856.MAX31856(spi, cs)


def read_raw_temperature_code(sensor):

    # Start a new measurement
    sensor.initiate_one_shot_measurement()

    # Wait until measurement is finished
    while sensor.oneshot_pending:
        time.sleep(0.01)

    # Read temperature registers
    raw_bytes = sensor._read_sequential_registers(0x0C, 3)

    high_byte = raw_bytes[0]
    mid_byte = raw_bytes[1]
    low_byte = raw_bytes[2]

    # Combine the three bytes into a 19-bit value
    raw_code = (
        (high_byte << 11)
        | (mid_byte << 3)
        | (low_byte >> 5)
    )

    # Convert from 19-bit two's complement
    if raw_code & 0x40000:
        raw_code -= 0x80000

    return raw_code


try:

    while True:

        raw = read_raw_temperature_code(thermocouple)

        print("Raw code:", raw)
        print("Temperature:", raw * 0.0078125)

        time.sleep(0.5)


except KeyboardInterrupt:
    pass


finally:
    cs.deinit()