"""
Configuration directory for NAU7802 scale modules.

The pin entries document how the scale is wired. Because ScaleModule uses
board.I2C(), SDA and SCL must describe the Raspberry Pi default I2C pins:
GPIO2 for SDA and GPIO3 for SCL.
"""


SCALE_DIRECTORY = {
    "crystal_growth_scale": {
        "name": "Crystal Growth Scale",
        "pins": {
            "power": {
                "physical": 1,
                "voltage": 3.3,
            },
            "ground": {
                "physical": 6,
            },
            "sda": {
                "gpio": 2,
                "physical": 3,
            },
            "scl": {
                "gpio": 3,
                "physical": 5,
            },
        },

        # The NAU7802 normally has the fixed I2C address 0x2A.
        "i2c_address": 0x2A,

        # Use one active channel because this configuration represents
        # one load cell connected to NAU7802 channel 1.
        "active_channels": 1,
        "channel": 1,

        # Number of raw readings averaged for each reported measurement.
        "samples": 2,
    },
}
