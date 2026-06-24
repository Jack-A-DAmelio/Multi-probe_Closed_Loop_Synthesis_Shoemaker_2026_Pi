"""
Pi server (MINIMAL TEST VERSION)

Author: Jack A. D'Amelio
Date: 2026-06-24
Internal Pi-Hardware Version: v0.1

Purpose:
--------
Receives control commands from the PC dashboard and updates
shared controller state (experiment config + streaming control).
"""

from fastapi import FastAPI
import pi_controller as controller

app = FastAPI()


# =========================================================
# EXPERIMENT CONFIGURATION ENDPOINT
# =========================================================

@app.post("/config")
def set_experiment_config(config: dict):
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
        flush_interval_sec = config.get("flush_interval_sec", 2.0)
        sample_rate_hz = config.get("sample_rate_hz", 100.0)
        # -----------------------------------------------------
        # UPDATE SHARED CONTROLLER STATE
        # -----------------------------------------------------
        # This state is shared across:
        # - streaming loop
        # - hardware filtering
        # - buffering logic
        controller.STATE.current_experiment_id = experiment_id
        controller.STATE.set_enabled_probes(enabled_probes)
        controller.flush_interval_sec = flush_interval_sec
        controller.sample_rate_hz = sample_rate_hz
        # Debug output for runtime verification
        print("\n--- EXPERIMENT CONFIG UPDATED ---")
        print("Experiment ID:", experiment_id)
        print("Enabled probes:", enabled_probes)
        print("Flush interval (sec):", flush_interval_sec)
        print("Sample rate (Hz):", sample_rate_hz)


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