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
        # STREAMING STATE
        # =========================================================

        # =========================================================
        # PC URL
        # =========================================================
        self.pc_url = "" # PC ingestion endpoint

        self.streaming_active = False
        # Flag checked by streaming loop to determine whether to run

        self.streaming_thread = None
        # Reference to background thread for debugging / lifecycle control

        # =========================================================
        # DATA BUFFER (PI → PC PIPELINE)
        # =========================================================

        self.probe_buffer = []
        # Temporary storage for sensor packets before transmission

        self.buffer_lock = threading.Lock()
        # Prevents race conditions between:
        # - streaming thread (writes)
        # - server endpoint (reads)
        self.flush_interval_sec = 0.0 # flush interval = batch transmission interval
        # =========================================================
        # EXPERIMENT STATE
        # =========================================================
        self.sample_rate_hz = 0.0  # hardware sampling frequency
        self.current_experiment_id = None
        # Set by PC before acquisition begins

        self.experiment_start_time = None
        # Unix timestamp marking start of acquisition

        # =========================================================
        # HARDWARE CONFIGURATION
        # =========================================================

        self.enabled_probes = []
        # List of active sensors included in streaming output
        # Example: ["temperature", "pressure"]

    # =========================================================
    # PROBE FILTERING
    # =========================================================

    def filter_enabled_probes(self, all_sensor_data):
        """
        Filters raw hardware sensor dictionary to only enabled probes.

        Parameters:
            all_sensor_data (dict): full sensor snapshot from hardware layer

        Returns:
            dict: filtered sensor dictionary containing enabled probes only
        """

        # If no probes are enabled, return empty dict to avoid accidental logging
        if not self.enabled_probes:
            return {}

        filtered = {}

        # Only forward sensors explicitly enabled for this experiment
        for probe_name in self.enabled_probes:

            # Safe lookup avoids KeyError if hardware output changes
            if probe_name in all_sensor_data:
                filtered[probe_name] = all_sensor_data[probe_name]

        return filtered

    # =========================================================
    # CONFIGURATION CONTROL
    # =========================================================

    def set_enabled_probes(self, probes):
        """
        Sets active probes for the current experiment.

        Parameters:
            probes (list): list of probe names to enable

        Returns:
            None

        Raises:
            ValueError: if probes is not a list
        """

        # Defensive check prevents silent misconfiguration
        if not isinstance(probes, list):
            raise ValueError("enabled_probes must be a list")

        self.enabled_probes = probes


# =========================================================
# SINGLETON INSTANCE
# =========================================================

STATE = ControllerState()