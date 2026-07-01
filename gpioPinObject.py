import board
import digitalio


class GPIOPin:
    """
    Blinka/CircuitPython GPIO pin abstraction.

    The user gives a GPIO number like 18.
    This class converts it into board.D18 internally.

    Important:
    These are GPIO numbers, not physical board pin numbers.
    For example, GPIO18 is physical pin 12 on the Raspberry Pi.
    """

    def __init__(self, gpio_number: int, direction: str):

        if direction not in ["in", "out"]:
            raise ValueError("Direction must be either 'in' or 'out'.")

        self.gpio_number = gpio_number
        self.direction = direction
        self.board_pin = getattr(board, f"D{gpio_number}")

        self._pin = digitalio.DigitalInOut(self.board_pin)

        if direction == "out":
            self._pin.direction = digitalio.Direction.OUTPUT
            self._pin.value = False

        elif direction == "in":
            self._pin.direction = digitalio.Direction.INPUT

    def set(self, value: bool):
        if self.direction != "out":
            raise RuntimeError(f"GPIO{self.gpio_number} is not an output pin.")
        else:
            self._pin.value = bool(value)

    def read(self) -> bool:
        return self._pin.value

    def deinit(self):
        self._pin.deinit()