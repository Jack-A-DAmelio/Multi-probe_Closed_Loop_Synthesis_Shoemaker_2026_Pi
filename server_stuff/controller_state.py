"""
Controller state object.
Author: Jack A. D'Amelio
Date: 2026-06-24
Internal Pi-Hardware Version: v0.1

Purpose:
--------
Stores all runtime state for the Pi controller.

All modules should import STATE and modify attributes
on the shared object rather than creating their own copies.

This acts as the central source of truth for:
- streaming control
- experiment configuration
- buffer management
- hardware probe selection
"""

import threading


# =========================================================
# SHARED STATE OBJECT
# =========================================================

class ControllerState:
    """
    Shared runtime state for Pi controller.

    This object is intentionally mutable and shared across
    multiple modules (server, streaming thread, hardware layer).

    Thread safety is NOT automatic; explicit locks are used
    where concurrent access occurs.
    """

    def __init__(self):

         
        # =========================================================
        # HARDWARE CONFIGURATION
        # =========================================================

        self.active_modules = {}
        # Example:
        # {
        #   "led": LEDModule(...),
        #   "temp": TempModule(...)
        # }

    # =========================================================
    # PROBE FILTERING
    # =========================================================

    def measure(self):
        
        return 0

    # =========================================================
    # CONFIGURATION CONTROL
    # =========================================================

    def add_module(self, module_name):
        return 0


