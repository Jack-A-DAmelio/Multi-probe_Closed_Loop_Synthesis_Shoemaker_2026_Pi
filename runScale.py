"""
Interactive test program for ScaleModule.

Author: Gabriel Dennis
Date: 2026-07-07

Purpose:
--------
Creates and tests one ScaleModule.

Commands during measurement:
    t + Enter    tare the scale
    c + Enter    calibrate the scale
    q + Enter    quit
"""

import select
import sys
import time

import board

from scaleModule import ScaleModule


def ask_yes_no(question: str) -> bool:
    """
    Ask the user a yes or no question.

    Parameters
    ----------
    question : str
        Question displayed to the user.

    Returns
    -------
    bool
        True for yes.
        False for no.
    """

    while True:

        answer = input(
            f"{question} (y/n): "
        ).strip().lower()

        if answer in ["y", "yes"]:
            return True

        if answer in ["n", "no"]:
            return False

        print("Please enter y or n.")


def get_known_mass() -> float:
    """
    Ask the user for a known calibration mass.

    Returns
    -------
    float
        Known mass in grams.
    """

    while True:

        try:
            known_mass = float(
                input(
                    "Enter the known calibration mass in grams: "
                )
            )

            if known_mass <= 0:
                print(
                    "Mass must be greater than zero."
                )

                continue

            return known_mass

        except ValueError:
            print(
                "Please enter a valid number."
            )


def interactive_calibration(scale: ScaleModule):
    """
    Guide the user through scale calibration.

    Parameters
    ----------
    scale : ScaleModule
        Scale object being calibrated.

    Returns
    -------
    None
    """

    print()
    print("CALIBRATION")
    print()
    print("Remove all mass from the scale.")

    input(
        "Press Enter when the scale is empty..."
    )

    # Store the empty scale reading as the zero point.
    tare_value = scale.tare()

    print(
        f"Tare raw value: {tare_value}"
    )

    # Ask the user for the known mass.
    known_mass = get_known_mass()

    print()

    print(
        f"Place the {known_mass:.3f} gram calibration mass "
        "on the scale."
    )

    input(
        "Press Enter when the calibration mass is stable..."
    )

    # Determine raw ADC counts per gram.
    calibration_factor = scale.calibrate(
        known_mass_grams=known_mass
    )

    print()
    print("Calibration complete.")

    print(
        "Calibration factor: "
        f"{calibration_factor:.6f} raw counts per gram"
    )


# Create the Raspberry Pi's standard I2C bus.
i2c = board.I2C()


# Create one scale module.
scale = ScaleModule(
    i2c_bus=i2c,
    name="TAL221 NAU7802 Scale",
    address=0x2A,
    samples=2,
)


try:
    print("*** SCALE STARTUP ***")
    print()

    print(
        "REMOVE ALL WEIGHT FROM THE SCALE"
    )

    time.sleep(3)

    # Perform the ADC's internal calibration.
    adc_calibration = scale.zero_adc()

    print(
        "ADC internal calibration:",
        adc_calibration["internal"],
    )

    print(
        "ADC offset calibration:",
        adc_calibration["offset"],
    )

    # Establish the initial software zero point.
    tare_value = scale.tare()

    print(
        f"Initial tare raw value: {tare_value}"
    )

    # Ask whether the user wants to perform
    # known-mass calibration.
    if ask_yes_no(
        "Do you want to calibrate the scale?"
    ):
        interactive_calibration(scale)

    print()
    print("READY")
    print()
    print("Commands:")
    print("t + Enter = tare")
    print("c + Enter = calibrate")
    print("q + Enter = quit")
    print()

    while True:

        # Read the scale through the standard
        # Module read() interface.
        measurement = scale.read()

        raw_value = measurement["raw"]
        grams = measurement["grams"]
        kilograms = measurement["kilograms"]

        # Before mass calibration, display raw ADC values.
        if grams is None:

            print(
                f"Raw: {raw_value:10d} | "
                "Scale not mass calibrated"
            )

        # After mass calibration, display all units.
        else:

            print(
                f"Raw: {raw_value:10d} | "
                f"Grams: {grams:10.3f} g | "
                f"Kilograms: {kilograms:10.6f} kg"
            )

        # Check for keyboard input without stopping
        # the scale measurement loop.
        ready_to_read, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            0,
        )

        if ready_to_read:

            command = (
                sys.stdin.readline()
                .strip()
                .lower()
            )

            # Tare command.
            if command == "t":

                tare_value = scale.tare()

                print()
                print("Scale tared.")

                print(
                    f"New tare raw value: {tare_value}"
                )

                print()

            # Calibration command.
            elif command == "c":

                interactive_calibration(scale)

                print()
                print(
                    "Returning to measurement mode."
                )
                print()

            # Quit command.
            elif command == "q":

                print("Stopping...")
                break

            # Ignore empty input but report unknown commands.
            elif command != "":

                print(
                    f"Unknown command: {command}"
                )

        time.sleep(0.5)


except KeyboardInterrupt:
    print("\nStopping...")


finally:

    # Disable the NAU7802 through:
    #
    # ScaleModule
    #       ↓
    # ScaleDevice
    #       ↓
    # NAU7802.enable(False)
    scale.cleanup()