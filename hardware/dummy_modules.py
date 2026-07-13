import random


class DummyCamera:

    def __init__(self, pin_directory):

        self.pin_directory = pin_directory
        self.counter = 0


    def measure(self):

        self.counter += 1

        # Simulate image output
        return f"dummy_image_{self.counter}.jpg"


    def cleanup(self):

        pass



class DummyScale:

    def __init__(self, pin_directory):

        self.pin_directory = pin_directory


    def measure(self):

        # Simulate weight in grams
        return round(
            random.uniform(0, 100),
            2
        )


    def cleanup(self):

        pass



class DummyThermocouple:

    def __init__(self, pin_directory):

        self.pin_directory = pin_directory


    def measure(self):

        # Simulate temperature in Celsius
        return round(
            random.uniform(20, 100),
            2
        )


    def cleanup(self):

        pass