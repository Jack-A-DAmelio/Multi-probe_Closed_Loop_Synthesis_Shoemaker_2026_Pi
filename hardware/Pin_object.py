import RPi.GPIO as GPIO


class Pin:
    """
    Hardware pin abstraction with full GPIO encapsulation.
    """

    def __init__(self, address: int, name: str, description: str, mode=GPIO.OUT):
        self.address = address
        self.name = name
        self.description = description
        self.mode = mode

        GPIO.setup(self.address, mode)

        self._last_value = None

    def set(self, value: bool):
        """Write digital value to pin."""
        GPIO.output(self.address, GPIO.HIGH if value else GPIO.LOW)
        self._last_value = value

    def read(self):
        """Read digital value from pin (if configured as input)."""
        value = GPIO.input(self.address)
        self._last_value = value
        return value

    @property
    def last_value(self):
        return self._last_value