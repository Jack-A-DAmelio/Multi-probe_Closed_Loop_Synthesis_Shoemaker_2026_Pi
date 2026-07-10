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

@app.post("/create_modules")
def create_modules():
    return 

@app.get("/measure")
def measure():


    return



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