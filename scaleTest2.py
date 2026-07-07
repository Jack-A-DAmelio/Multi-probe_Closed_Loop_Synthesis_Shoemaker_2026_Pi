# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
NAU7802 and TAL221 load cell program.

Features:
- Reads raw ADC values
- Converts readings to grams
- Converts readings to kilograms
- Optional user calibration
- User-selected calibration mass
- Saves calibration for future runs
- Software tare
- Tare reset
- Recalibration while running

Commands:
    t = tare scale
    r = reset tare
    c = calibrate scale
    q = quit
"""

import time
import sys
import select
import json

import board

from cedargrove_nau7802 import NAU7802


# ==================================================
# CALIBRATION FILE
# ==================================================

CALIBRATION_FILE = "tal221_calibration.json"


# ==================================================
# NAU7802 SETUP
# ==================================================

nau7802 = NAU7802(
    board.I2C(),
    address=0x2A,
    active_channels=1
)


# ==================================================
# SCALE VALUES
# ==================================================

# Will be loaded from the calibration file
# or calculated during calibration.
counts_per_gram = None


# Raw value currently treated as zero grams.
tare_raw = 0


# Original zero value recorded when calibration
# or startup zeroing was performed.
startup_zero_raw = 0


# ==================================================
# NAU7802 INTERNAL CALIBRATION
# ==================================================

def zero_channel():
    """
    Perform NAU7802 internal and offset calibration.

    All weight should be removed from the TAL221
    before running this function.
    """

    print(
        "channel {0:1d} calibrate.INTERNAL: {1:5s}".format(
            nau7802.channel,
            str(nau7802.calibrate("INTERNAL"))
        )
    )

    print(
        "channel {0:1d} calibrate.OFFSET:   {1:5s}".format(
            nau7802.channel,
            str(nau7802.calibrate("OFFSET"))
        )
    )

    print(
        f"...channel {nau7802.channel} calibrated"
    )


# ==================================================
# RAW ADC READING
# ==================================================

def read_raw_value(samples=2):
    """
    Read and average consecutive raw ADC values.

    Parameters
    ----------
    samples : int
        Number of raw readings to average.

    Returns
    -------
    int
        Averaged raw ADC value.
    """

    if samples <= 0:
        raise ValueError(
            "samples must be greater than zero"
        )


    sample_sum = 0
    sample_count = samples


    while sample_count > 0:

        # Wait until a new ADC reading is ready
        while not nau7802.available():
            pass


        # Add the raw ADC value
        sample_sum += nau7802.read()


        sample_count -= 1


    return int(
        sample_sum / samples
    )


# ==================================================
# RAW VALUE TO GRAMS
# ==================================================

def raw_to_grams(raw_value):
    """
    Convert a raw ADC reading to grams.

    Parameters
    ----------
    raw_value : int
        Raw ADC reading.

    Returns
    -------
    float
        Calculated mass in grams.
    """

    if counts_per_gram is None:
        raise RuntimeError(
            "Scale has not been calibrated."
        )


    grams = (
        raw_value - tare_raw
    ) / counts_per_gram


    return grams


# ==================================================
# GRAMS TO KILOGRAMS
# ==================================================

def grams_to_kilograms(grams):
    """
    Convert grams to kilograms.
    """

    return grams / 1000.0


# ==================================================
# SAVE CALIBRATION
# ==================================================

def save_calibration():
    """
    Save counts-per-gram calibration data to a file.
    """

    calibration_data = {
        "counts_per_gram": counts_per_gram
    }


    with open(
        CALIBRATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            calibration_data,
            file,
            indent=4
        )


    print(
        f"Calibration saved to {CALIBRATION_FILE}"
    )


# ==================================================
# LOAD CALIBRATION
# ==================================================

def load_calibration():
    """
    Load a previously saved counts-per-gram value.

    Returns
    -------
    float or None
        Saved counts-per-gram value,
        or None if calibration cannot be loaded.
    """

    try:

        with open(
            CALIBRATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            calibration_data = json.load(file)


        loaded_value = float(
            calibration_data["counts_per_gram"]
        )


        if loaded_value == 0:
            raise ValueError(
                "Saved counts_per_gram cannot be zero."
            )


        return loaded_value


    except FileNotFoundError:

        return None


    except (
        KeyError,
        ValueError,
        TypeError,
        json.JSONDecodeError
    ) as error:

        print(
            f"Could not load calibration: {error}"
        )

        return None


# ==================================================
# YES OR NO INPUT
# ==================================================

def ask_yes_no(question):
    """
    Ask the user a yes-or-no question.

    Returns
    -------
    bool
        True for yes.
        False for no.
    """

    while True:

        response = input(
            f"{question} (y/n): "
        ).strip().lower()


        if response in ("y", "yes"):

            return True


        elif response in ("n", "no"):

            return False


        else:

            print(
                "Please enter y or n."
            )


# ==================================================
# GET KNOWN MASS
# ==================================================

def get_known_mass():
    """
    Ask the user for the known calibration mass.

    The mass must be entered in grams.

    Returns
    -------
    float
        Known mass in grams.
    """

    while True:

        response = input(
            "\nEnter exact calibration mass in grams: "
        )


        try:

            known_mass = float(response)


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


# ==================================================
# CALIBRATE SCALE
# ==================================================

def calibrate_scale(samples=50):
    """
    Calibrate the TAL221 using a user-selected
    known reference mass.

    The function:
    1. Measures the unloaded raw value.
    2. Asks for the known mass.
    3. Measures the loaded raw value.
    4. Calculates counts per gram.
    5. Saves the calibration.
    """

    global counts_per_gram
    global startup_zero_raw
    global tare_raw


    print("\n====================================")
    print("SCALE CALIBRATION")
    print("====================================")


    # ----------------------------------------------
    # MEASURE ZERO LOAD
    # ----------------------------------------------

    print(
        "\nRemove all objects from the scale."
    )


    input(
        "Press Enter when the scale is empty and stable..."
    )


    print(
        "\nMeasuring zero value..."
    )


    zero_raw = read_raw_value(
        samples=samples
    )


    print(
        f"Zero raw value: {zero_raw}"
    )


    # ----------------------------------------------
    # ASK FOR KNOWN MASS
    # ----------------------------------------------

    known_mass_grams = get_known_mass()


    # ----------------------------------------------
    # MEASURE KNOWN MASS
    # ----------------------------------------------

    print(
        f"\nPlace exactly {known_mass_grams:.3f} g "
        "on the scale."
    )


    input(
        "Press Enter when the mass is stable..."
    )


    print(
        "\nMeasuring calibration mass..."
    )


    loaded_raw = read_raw_value(
        samples=samples
    )


    print(
        f"Loaded raw value: {loaded_raw}"
    )


    # ----------------------------------------------
    # CALCULATE RAW CHANGE
    # ----------------------------------------------

    raw_difference = (
        loaded_raw - zero_raw
    )


    if raw_difference == 0:

        raise RuntimeError(
            "Calibration failed because the raw "
            "reading did not change."
        )


    # ----------------------------------------------
    # CALCULATE COUNTS PER GRAM
    # ----------------------------------------------

    counts_per_gram = (
        raw_difference / known_mass_grams
    )


    print("\nCalibration results:")


    print(
        f"Known mass: "
        f"{known_mass_grams:.3f} g"
    )


    print(
        f"Zero raw value: "
        f"{zero_raw}"
    )


    print(
        f"Loaded raw value: "
        f"{loaded_raw}"
    )


    print(
        f"Raw difference: "
        f"{raw_difference}"
    )


    print(
        f"Counts per gram: "
        f"{counts_per_gram:.6f}"
    )


    # ----------------------------------------------
    # SAVE CALIBRATION
    # ----------------------------------------------

    save_calibration()


    # ----------------------------------------------
    # REMOVE CALIBRATION MASS
    # ----------------------------------------------

    print(
        "\nRemove the calibration mass from the scale."
    )


    input(
        "Press Enter when the scale is empty and stable..."
    )


    print(
        "\nEstablishing new zero..."
    )


    startup_zero_raw = read_raw_value(
        samples=samples
    )


    tare_raw = startup_zero_raw


    print(
        f"Startup zero raw value: "
        f"{startup_zero_raw}"
    )


    print(
        "\nCalibration complete."
    )


# ==================================================
# TARE SCALE
# ==================================================

def tare_scale(samples=20):
    """
    Set the current load equal to zero grams.

    The raw ADC reading remains unchanged.
    Only the mass calculation zero point changes.
    """

    global tare_raw


    print(
        "\nTaring scale..."
    )


    tare_raw = read_raw_value(
        samples=samples
    )


    print(
        "Scale tared."
    )


    print(
        f"New tare raw value: {tare_raw}"
    )


# ==================================================
# RESET TARE
# ==================================================

def reset_tare():
    """
    Reset the tare back to the startup zero value.
    """

    global tare_raw


    tare_raw = startup_zero_raw


    print(
        "\nTare reset."
    )


    print(
        f"Zero restored to raw value: "
        f"{tare_raw}"
    )


# ==================================================
# CHECK USER COMMAND
# ==================================================

def check_user_command():
    """
    Check for user commands without blocking the
    measurement loop.

    Commands
    --------
    t : tare scale
    r : reset tare
    c : recalibrate scale
    q : quit

    Returns
    -------
    bool
        True to continue.
        False to quit.
    """

    readable, _, _ = select.select(
        [sys.stdin],
        [],
        [],
        0
    )


    if not readable:

        return True


    command = (
        sys.stdin.readline()
        .strip()
        .lower()
    )


    # ----------------------------------------------
    # TARE
    # ----------------------------------------------

    if command == "t":

        tare_scale()


    # ----------------------------------------------
    # RESET TARE
    # ----------------------------------------------

    elif command == "r":

        reset_tare()


    # ----------------------------------------------
    # RECALIBRATE
    # ----------------------------------------------

    elif command == "c":

        calibrate_scale()


    # ----------------------------------------------
    # QUIT
    # ----------------------------------------------

    elif command == "q":

        return False


    # ----------------------------------------------
    # EMPTY INPUT
    # ----------------------------------------------

    elif command == "":

        pass


    # ----------------------------------------------
    # UNKNOWN COMMAND
    # ----------------------------------------------

    else:

        print(
            "\nUnknown command."
        )

        print(
            "Use t, r, c, or q."
        )


    return True


# ==================================================
# INITIALIZE NAU7802
# ==================================================

print(
    "*** Initialize TAL221 load cell"
)


# Enable digital and analog systems
enabled = nau7802.enable(True)


print(
    "Digital and analog power enabled:",
    enabled
)


# Select Channel 1
nau7802.channel = 1


# ==================================================
# NAU7802 INTERNAL CALIBRATION
# ==================================================

print(
    "\nREMOVE ALL WEIGHT FROM THE SCALE"
)


print(
    "Internal calibration begins in 3 seconds."
)


time.sleep(3)


zero_channel()


time.sleep(1)


# ==================================================
# LOAD EXISTING SCALE CALIBRATION
# ==================================================

counts_per_gram = load_calibration()


if counts_per_gram is not None:

    print(
        "\nSaved scale calibration found."
    )


    print(
        f"Saved counts per gram: "
        f"{counts_per_gram:.6f}"
    )


    recalibrate = ask_yes_no(
        "Do you want to calibrate the scale?"
    )


    if recalibrate:

        calibrate_scale()


    else:

        print(
            "\nUsing saved calibration."
        )


        print(
            "Remove all weight from the scale."
        )


        input(
            "Press Enter when the scale is empty..."
        )


        startup_zero_raw = read_raw_value(
            samples=20
        )


        tare_raw = startup_zero_raw


        print(
            f"Startup zero raw value: "
            f"{startup_zero_raw}"
        )


else:

    print(
        "\nNo saved scale calibration was found."
    )


    print(
        "The scale must be calibrated before "
        "grams and kilograms can be calculated."
    )


    calibrate_scale()


# ==================================================
# READY
# ==================================================

print("\n====================================")

print("READY")

print("====================================")


print("\nCommands:")

print("t = tare scale")

print("r = reset tare")

print("c = recalibrate scale")

print("q = quit")


# ==================================================
# MAIN LOOP
# ==================================================

running = True


try:

    while running:

        # ------------------------------------------
        # READ RAW ADC VALUE
        # ------------------------------------------

        raw_value = read_raw_value(
            samples=2
        )


        # ------------------------------------------
        # CONVERT RAW TO GRAMS
        # ------------------------------------------

        grams = raw_to_grams(
            raw_value
        )


        # ------------------------------------------
        # CONVERT GRAMS TO KILOGRAMS
        # ------------------------------------------

        kilograms = grams_to_kilograms(
            grams
        )


        # ------------------------------------------
        # DISPLAY VALUES
        # ------------------------------------------

        print("\n=====")


        print(
            f"raw value: "
            f"{raw_value}"
        )


        print(
            f"mass: "
            f"{grams:.3f} g"
        )


        print(
            f"mass: "
            f"{kilograms:.6f} kg"
        )


        # ------------------------------------------
        # CHECK USER COMMAND
        # ------------------------------------------

        running = check_user_command()


        time.sleep(0.25)


except KeyboardInterrupt:

    print(
        "\nProgram stopped by user."
    )


finally:

    nau7802.enable(False)


    print(
        "NAU7802 powered down."
    )