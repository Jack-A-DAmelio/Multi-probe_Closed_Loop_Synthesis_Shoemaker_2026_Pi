"""
Directory for one MAX31856 temperature-probe configuration.

The values below record both the Raspberry Pi connection and the
matching MAX31856 sensor connection.

The module only actively creates the CS pin. Power and ground are fixed
supply connections, while board.SPI() automatically uses the Raspberry
Pi default SCK, MISO, and MOSI pins.
"""

TEMP_PROBE_DIRECTORY = {
    "name": "Main Temperature Probe",

    "pins": {
        "power": {
            "board_pin": "3V3",
            "physical_pin": 1,
            "sensor_pin": "VIN",
        },

        "ground": {
            "board_pin": "GND",
            "physical_pin": 6,
            "sensor_pin": "GND",
        },

        "sck": {
            "gpio": 11,
            "board_pin": "SCLK",
            "physical_pin": 23,
            "sensor_pin": "SCK",
        },

        "miso": {
            "gpio": 9,
            "board_pin": "MISO",
            "physical_pin": 21,
            "sensor_pin": "SDO",
        },

        "mosi": {
            "gpio": 10,
            "board_pin": "MOSI",
            "physical_pin": 19,
            "sensor_pin": "SDI",
        },

        "cs": {
            "gpio": 5,
            "board_pin": "D5",
            "physical_pin": 29,
            "sensor_pin": "CS",
        },
    },

    "thermocouple_type": "K",
    "read_interval_seconds": 0.5,
}
