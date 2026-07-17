# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import digitalio
import time
import adafruit_max31856


# Create SPI bus
spi = board.SPI()


# Create chip-select pin
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT


# Create MAX31856 in voltage mode with gain = 8
thermocouple = adafruit_max31856.MAX31856(
    spi,
    cs,
    thermocouple_type=adafruit_max31856.ThermocoupleType.G8
)


def read_raw_voltage(sensor):

    # Start one ADC conversion
    sensor.initiate_one_shot_measurement()

    # Wait for conversion to finish
    while sensor.oneshot_pending:
        time.sleep(0.01)

    # Read the three thermocouple conversion registers
    raw_bytes = sensor._read_sequential_registers(0x0C, 3)

    high_byte = raw_bytes[0]
    mid_byte = raw_bytes[1]
    low_byte = raw_bytes[2]

    # Combine the three bytes into signed 19-bit ADC code
    raw_code = (
        (high_byte << 11)
        | (mid_byte << 3)
        | (low_byte >> 5)
    )

    # Convert from 19-bit two's complement
    if raw_code & 0x40000:
        raw_code -= 0x80000

    # Gain used by G8 voltage mode
    gain = 8

    # Convert ADC code into thermocouple input voltage
    voltage_volts = raw_code / (
        gain * 1.6 * (2 ** 17)
    )

    voltage_microvolts = voltage_volts * 1_000_000

    return raw_code, voltage_volts, voltage_microvolts


try:

    while True:

        raw_code, voltage_v, voltage_uv = read_raw_voltage(
            thermocouple
        )

        print("Raw ADC code:", raw_code)
        print("Input voltage:", voltage_v, "V")
        print("Input voltage:", voltage_uv, "uV")
        print()

        time.sleep(0.5)


except KeyboardInterrupt:
    pass


finally:
    cs.deinit()