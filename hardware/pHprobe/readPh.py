"""
Read pH measurements from an Atlas Scientific EZO-pH circuit
connected through a USB serial carrier board.
"""

import time
import serial


# Serial device created by the USB carrier board.
SERIAL_PORT = "/dev/ttyUSB0"

# EZO circuits normally use 9600 baud in UART mode.
BAUD_RATE = 9600

# Maximum number of seconds to wait for a response.
READ_TIMEOUT_SECONDS = 2


ser = None

try:
    # Create and open the serial connection.
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=READ_TIMEOUT_SECONDS,
        write_timeout=READ_TIMEOUT_SECONDS,
    )

    # Give the serial connection a moment to initialize.
    time.sleep(1)

    # Remove any old data already waiting in the buffers.
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print(f"Connected to EZO-pH circuit on {SERIAL_PORT}")
    print("Starting pH measurements.")
    print("Press Ctrl+C to stop.\n")

    while True:
        # Clear any unread response from an earlier command.
        ser.reset_input_buffer()

        # The EZO read command is R.
        #
        # Atlas Scientific commands must end with a carriage return.
        ser.write(b"R\r")

        # Make sure the command is sent immediately.
        ser.flush()

        # Give the EZO-pH circuit time to take the measurement.
        time.sleep(0.9)

        # Read until the EZO carriage-return terminator is received.
        response_bytes = ser.read_until(b"\r")

        if not response_bytes:
            print("No response received before the timeout.")
            continue

        # Convert the response from bytes into readable text.
        response_string = response_bytes.decode(
            "ascii",
            errors="replace",
        ).strip()

        print(f"Raw response: {response_bytes}")
        print(f"pH reading: {response_string}\n")

        # Delay before requesting the next reading.
        time.sleep(0.1)

except serial.SerialException as error:
    print(f"Serial communication error: {error}")

except KeyboardInterrupt:
    print("\nMeasurement stopped by user.")

finally:
    if ser is not None and ser.is_open:
        ser.close()
        print("The serial port is closed.")
