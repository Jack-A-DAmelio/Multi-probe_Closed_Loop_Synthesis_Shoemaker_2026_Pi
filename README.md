# Multi-probe Closed-Loop Synthesis: Raspberry Pi

This repository contains the Raspberry Pi-side hardware service for the
multi-probe solution-growth measurement system. The service receives hardware
configuration from the PC, creates the configured sensor modules, collects
measurements, and releases hardware resources when requested.

The PC dashboard, experiment controls, and data storage are maintained in a
separate repository:

- PC: [Multi-probe Closed-Loop Synthesis (PC)](https://github.com/Jack-A-DAmelio/Multi-probe_Closed_Loop_Synthesis_Shoemaker_2026_PC)
- Raspberry Pi: [Multi-probe Closed-Loop Synthesis (Pi)](https://github.com/Jack-A-DAmelio/Multi-probe_Closed_Loop_Synthesis_Shoemaker_2026_Pi)

## How it works

The PC communicates with the Pi over HTTP. The Pi's FastAPI service listens on
port `8001` and currently provides three operations:

1. `/configure` replaces the active sensor configuration and initializes each
   requested hardware module.
2. `/measure` reads each configured module and returns a timestamp and the
   measurements.
3. `/cleanup` asks configured modules to release their resources and clears the
   active configuration.

The PC initiates these calls during experiment setup and collection. The Pi
returns measurement values; the PC is responsible for writing the experiment
CSV and saving camera images.

## Repository layout

```text
hardware/
  balance/        NAU7802 scale module and scale test/calibration scripts (Not done)
  thermocouple/   MAX31856 module and thermocouple test/calibration scripts (Done)
  pHprobe/        Standalone EZO-pH serial scripts (Not done)
  LED/            GPIO pin and LED module code (Done)
  module_abstract.py
                  Shared hardware-module interface

server_stuff/
  pi_server.py    FastAPI service called by the PC
  controller_state.py
                  Separate, minimal controller-state scaffold
```

## Active modules

The server's `MODULE_REGISTRY` currently includes:

- **Thermocouple:** `thermocouple`, implemented by
  `hardware/thermocouple/tempProbeModule2.py` for a MAX31856 amplifier. The
  configuration is a flat dictionary with a nonempty `name`, integer `cs_gpio`,
  and optional `thermocouple_type` (defaults to `K`; supported types are B, E,
  J, K, N, R, S, and T).
- **Scale:** `scale`, implemented by `hardware/balance/scaleModule2.py` for a
  NAU7802 load-cell ADC. Its configuration includes a nonempty `name`, a
  `pins` dictionary with `sda.gpio` set to `2` and `scl.gpio` set to `3`, and
  optional `i2c_address` (integer, default `0x2A`), `samples`, `active_channels`,
  and `channel`.

The pH and LED code is present but is not registered with the API server.
Similarly, the pH reading and calibration scripts operate independently rather
than through the PC's experiment workflow.

## Setup and launch

The repository does not currently include a dependency manifest. On the
Raspberry Pi, prepare an environment with the packages needed by the service and
hardware modules, including FastAPI, Uvicorn, `board`, `digitalio`,
`adafruit_max31856`, and `cedargrove_nau7802`. The standalone pH scripts also
use `pyserial`; the LED GPIO code uses `RPi.GPIO`.

Enable the Raspberry Pi's SPI and I2C interfaces and connect the hardware to the
pins expected by its module. The thermocouple module uses the default SPI bus
and its configured chip-select GPIO. The scale module uses the default I2C bus
(GPIO2 SDA and GPIO3 SCL).

From the repository root, start the API service with:

```bash
python -m server_stuff.pi_server
```

The service binds to `0.0.0.0:8001` so the PC can connect over the network. The
PC's configured Pi address must be reachable on that port.

## API contract

The PC sends a configuration object containing a `modules` mapping. Each entry
must have a `pin_directory` containing the configuration expected by that
module. For example, the shape is:

```json
{
  "modules": {
    "thermocouple": {
      "pin_directory": {
        "name": "Main Temperature Probe",
        "cs_gpio": 5,
        "thermocouple_type": "K"
      }
    }
  }
}
```

`POST /measure` returns a response shaped like:

```json
{
  "timestamp": 1793210000.0,
  "measurements": {
    "thermocouple": 25.0
  }
}
```

The actual measurement values depend on each module's return type. The current
thermocouple module returns temperature in Celsius from `measure()`. The scale
module's `read()` method returns a dictionary with a timestamp, channel, and
raw ADC value.

## Adding a module to the service

1. Implement the hardware interface in `hardware/`, including initialization,
   a `measure()` method, and `cleanup()`.
2. Add the module name and class to `MODULE_REGISTRY` in
   `server_stuff/pi_server.py`.
3. Document its configuration fields and expected measurement output here.
4. Ensure the PC sends a matching `pin_directory` for that module.
5. Test configuration, measurement, and cleanup on the Pi with the hardware
   connected.

## Current integration notes

- The API calls `measure()` on every registered module. The current scale class
  exposes `read()` but not `measure()`, so scale measurements need an adapter
  method or a server-side call change before the scale can be used through
  `/measure`.
- The PC dashboard's scale settings must match the nested field names and types
  required by `ScaleModule`; confirm that configuration mapping before using the
  scale through the full PC-to-Pi workflow.
- pH, LED control, and volume sensing are not currently part of the active API
  registry.
- The service clears `PI_MODULES` when a new configuration is received. Configure
  all desired modules together in one request.

## Related documentation

- PC dashboard, experiment workflow, and output files:
  [PC repository README](https://github.com/Jack-A-DAmelio/Multi-probe_Closed_Loop_Synthesis_Shoemaker_2026_PC)
- Sensor-specific implementation notes are included in the thermocouple and
  scale module docstrings.

Hardware wiring diagrams, a reproducible dependency list, and a complete
deployment and troubleshooting guide should be added as the Pi setup is
finalized.
