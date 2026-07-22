"""
Pi server





Receives experiment configuration from PC,
creates hardware modules, performs measurements,
and handles cleanup.
"""

from fastapi import FastAPI, Body
import time




app = FastAPI()


# =========================================================
# PI RUNTIME STATE
# =========================================================


from hardware.balance.scaleModule2 import ScaleModule
from hardware.thermocouple.tempProbeModule2 import TempProbeModule

MODULE_REGISTRY = {


    "scale": ScaleModule,

    "thermocouple": TempProbeModule

}



# =========================================================
# CONFIGURATION
# =========================================================

@app.post("/configure")
def configure_modules(data: dict = Body(...)):

    global PI_MODULES

    # clear previous configuration
    PI_MODULES = {}


    modules = data.get(
        "modules",
        {}
    )


    print(data , "-------") 
    for module_name, module_data in modules.items():


        if module_name not in MODULE_REGISTRY:

            return {
                "error": f"Unknown module: {module_name}"
            }


        module_class = MODULE_REGISTRY[module_name]


        pin_directory = module_data[
            "pin_directory"
        ]


        # Construct hardware object
        module_object = module_class(
            pin_directory
        )


        PI_MODULES[module_name] = module_object



    return {
        "status": "configured",
        "modules": list(PI_MODULES.keys())
    }



# =========================================================
# MEASUREMENT
# =========================================================

@app.post("/measure")
def measure():

    timestamp = time.time()


    measurements = {}


    for name, module in PI_MODULES.items():

        measurements[name] = module.measure()



    return {
        "timestamp": timestamp,
        "measurements": measurements
    }



# =========================================================
# CLEANUP
# =========================================================

@app.post("/cleanup")
def cleanup():

    global PI_MODULES


    for name, module in PI_MODULES.items():

        if hasattr(module, "cleanup"):

            module.cleanup()



    PI_MODULES = {}


    return {
        "status": "cleaned"
    }



# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False
    )
