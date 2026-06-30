# #------------------pinObject.py with GPIO check------------------------
# import board
# import digitalio
#
#
# class Pin:
#     """
#     Blinka/CircuitPython GPIO pin abstraction.
#
#     The user gives a GPIO number like 18.
#     This class converts it into board.D18 internally.
#
#     Important:
#     These are GPIO numbers, not physical board pin numbers.
#     For example, GPIO18 is physical pin 12 on the Raspberry Pi.
#     """
#
#     # ALLOWED_GPIO_PINS = {
#     #     2: board.D2,
#     #     3: board.D3,
#     #     4: board.D4,
#     #     5: board.D5,
#     #     6: board.D6,
#     #     7: board.D7,
#     #     8: board.D8,
#     #     9: board.D9,
#     #     10: board.D10,
#     #     11: board.D11,
#     #     12: board.D12,
#     #     13: board.D13,
#     #     14: board.D14,
#     #     15: board.D15,
#     #     16: board.D16,
#     #     17: board.D17,
#     #     18: board.D18,
#     #     19: board.D19,
#     #     20: board.D20,
#     #     21: board.D21,
#     #     22: board.D22,
#     #     23: board.D23,
#     #     24: board.D24,
#     #     25: board.D25,
#     #     26: board.D26,
#     #     27: board.D27,
#     # }
#
#     def __init__(self, gpio_number: int, direction: str):
#         # if gpio_number not in self.ALLOWED_GPIO_PINS:
#         #     raise ValueError(f"GPIO{gpio_number} is not an allowed GPIO pin.")
#
#         if direction not in ["in", "out"]:
#             raise ValueError("Direction must be either 'in' or 'out'.")
#
#         self.gpio_number = gpio_number
#         self.direction = direction
#
#         # self.board_pin = self.ALLOWED_GPIO_PINS[gpio_number]
#
#         self.board_pin = getattr(board, f"D{gpio_number}")
#
#         self._pin = digitalio.DigitalInOut(self.board_pin)
#
#         if direction == "out":
#             self._pin.direction = digitalio.Direction.OUTPUT
#             self._pin.value = False
#
#         elif direction == "in":
#             self._pin.direction = digitalio.Direction.INPUT
#
#     def set(self, value: bool):
#         if self.direction != "out":
#             raise RuntimeError(f"GPIO{self.gpio_number} is not an output pin.")
#
#         self._pin.value = bool(value)
#
#     def read(self) -> bool:
#         return self._pin.value
#
#     def deinit(self):
#         self._pin.deinit()