# hardware_api/factory.py

from hardware.LED.Three_LED_module import LEDModule


FACTORY_REGISTRY = {
    "led": LEDModule
}


def build_module(name: str, pin_map: dict):
    cls = FACTORY_REGISTRY.get(name)

    if not cls:
        raise ValueError(f"Unknown module: {name}")

    return cls(pin_map)