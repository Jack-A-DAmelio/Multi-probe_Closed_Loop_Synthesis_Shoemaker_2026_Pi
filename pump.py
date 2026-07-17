#!/usr/bin/env python3

"""
DFRobot Peristaltic Pump PWM Control
Raspberry Pi 4 + Blinka pwmio

GPIO18 (BCM18) -> PWM Signal
External power supply powers the pump.
Pi and external supply MUST share GND.
"""

import time
import board
import pwmio

# -------------------------
# Configuration
# -------------------------

PWM_PIN = board.D18       # GPIO18 (Pin 12)
PWM_FREQ = 1000           # Hz
PUMP_SPEED = 0.75         # 0.0 - 1.0

# -------------------------

pump = pwmio.PWMOut(
    PWM_PIN,
    frequency=PWM_FREQ,
    duty_cycle=0
)


def set_speed(speed: float):
    """Set pump speed from 0.0 to 1.0."""
    speed = max(0.0, min(1.0, speed))
    pump.duty_cycle = int(speed * 65535)


def stop():
    """Turn pump completely off."""
    pump.duty_cycle = 0


def cleanup():
    """Safely stop and release PWM."""
    print("\nCleaning up...")
    stop()
    pump.deinit()
    print("Pump stopped.")
    print("PWM released.")


def get_runtime():
    """Prompt the user for pump runtime in seconds."""
    while True:
        try:
            runtime = float(input("How long should the pump run (seconds)? "))
            if runtime <= 0:
                print("Please enter a positive number.")
                continue
            return runtime
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    runtime = get_runtime()

    print(f"\nStarting pump for {runtime} seconds...")
    set_speed(PUMP_SPEED)

    time.sleep(runtime)

    print("Time elapsed. Stopping pump...")
    stop()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt received.")

    finally:
        cleanup()