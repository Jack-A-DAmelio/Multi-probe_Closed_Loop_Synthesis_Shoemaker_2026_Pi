"""
Pi server (MINIMAL TEST VERSION)

Author: Undergraduate Research Project
Date: 2026-06-18
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
        experiment_id = config.get("experiment_id", None)
        enabled_probes = config.get("enabled_probes", [])

        # -----------------------------------------------------
        # UPDATE SHARED CONTROLLER STATE
        # -----------------------------------------------------
        # This state is shared across:
        # - streaming loop
        # - hardware filtering
        # - buffering logic
        controller.STATE.current_experiment_id = experiment_id
        controller.STATE.set_enabled_probes(enabled_probes)

        # Debug output for runtime verification
        print("\n--- EXPERIMENT CONFIG UPDATED ---")
        print("Experiment ID:", experiment_id)
        print("Enabled probes:", enabled_probes)

        return {
            "status": "ok",
            "experiment_id": experiment_id,
            "enabled_probes": enabled_probes
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