"""
Pi server (MINIMAL TEST VERSION)

Author: Jack A. D'Amelio
Date: 2026-06-24
Internal Pi-Hardware Version: v0.1

Purpose:
--------
Receives control commands from the PC dashboard and updates
shared controller state (experiment config + streaming control).

Run this script from the above directory with:
python -m server_stuff.pi_server
"""

from fastapi import Body, FastAPI
import server_stuff.pi_controller as controller

from hardware_api.module_registry import MODULE_REGISTRY
from hardware_api.factory import build_module

from fastapi import FastAPI

app = FastAPI()


# =========================================================
# EXPERIMENT CONFIGURATION ENDPOINT
# =========================================================

@app.post("/config")
def set_experiment_config(config: dict = Body(...)):
    """
    Updates experiment configuration from PC dashboard.

    Expected input:
        config (dict):
            {
                "experiment_id": str,
                "enabled_probes": list[str]
            }

    Returns:
        dict: status + echoed configuration
    """

    try:
        # Extract configuration fields safely from request payload
        #first parameter looks for the key, if no such key, the second parameter is given by default
        experiment_id = config.get("experiment_id", None)
        enabled_probes = config.get("enabled_probes", [])
        flush_interval_sec = config.get("flush_interval_sec", "")
        sample_rate_hz = config.get("sample_rate_hz", 1)
        # -----------------------------------------------------
        # UPDATE SHARED CONTROLLER STATE
        # -----------------------------------------------------
        # This state is shared across:
        # - streaming loop
        # - hardware filtering
        # - buffering logic
        controller.STATE.current_experiment_id = experiment_id
        controller.STATE.set_enabled_probes(enabled_probes)
        controller.STATE.flush_interval_sec = flush_interval_sec
        controller.STATE.sample_rate_hz = sample_rate_hz
        # Debug output for runtime verification
        print("\n--- EXPERIMENT CONFIG UPDATED ---")
        print("Experiment ID:", controller.STATE.current_experiment_id)
        print("Enabled probes:", controller.STATE.enabled_probes)
        print("Flush interval (sec):", controller.STATE.flush_interval_sec)
        print("Sample rate (Hz):", controller.STATE.sample_rate_hz)


        return {
            "status": "ok",
            "experiment_id": experiment_id,
            "enabled_probes": enabled_probes,
            "flush_interval_sec": flush_interval_sec,
            "sample_rate_hz": sample_rate_hz
        }

    except Exception as e:
        # Catch unexpected config errors so server doesn't crash
        print("Config error:", e)
        return {"status": "error", "message": str(e)}





@app.get("/modules/{name}/spec")
def get_spec(name: str):
    spec = MODULE_REGISTRY.get(name)

    if not spec:
        return {"status": "error", "message": "unknown module"}

    return {
        "status": "ok",
        "module": spec.name,
        "pins_required": spec.pins_required
    }


@app.post("/modules/{name}/build")
def build(name: str, pin_map: dict):
    """
    Builds any registered module using provided pin mapping.
    """

    if name not in MODULE_REGISTRY:
        return {"status": "error", "message": "unknown module"}

    module = build_module(name, pin_map)
    controller.STATE.active_modules[name] = module
    return {
        "status": "ok",
        "module": name
    }









# =========================================================
# STREAM CONTROL ENDPOINTS
# =========================================================

@app.post("/start")
def start():
    """
    Starts background streaming thread.

    Returns:
        dict: simple status response
    """
    controller.start_streaming()
    return {"status": "started"}


@app.post("/stop")
def stop():
    """
    Stops background streaming loop safely.

    Returns:
        dict: simple status response
    """
    controller.stop_streaming()
    return {"status": "stopped"}

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    """
    Launches the Pi control server.

    Host:
        0.0.0.0
        Allows connections from other machines on the network.

    Port:
        8001
        Must match PI_URL used by the dashboard.
    """

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False
    )