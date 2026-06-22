"""
Controller layer

Author: Undergraduate Research Project
Date: 2026-06-18
Internal Pi-Hardware Version: v0.1

Purpose:
--------
Core runtime controller for the Pi system.

This module is responsible for:
- running the continuous acquisition loop
- buffering sensor data locally in a thread-safe way
- transmitting batched data to the PC server
- managing start/stop lifecycle of streaming
"""

import time
import threading
import requests

import hardware
from controller_state import STATE


# =========================================================
# CONFIGURATION
# =========================================================

# Runtime configuration parameters for streaming behavior
CONFIG = {
    "pc_url": "http://127.0.0.1:8000/ingest",  # PC ingestion endpoint
    "sample_rate_hz": 2,                       # hardware sampling frequency
    "flush_interval_sec": 2.0                  # batch transmission interval
}


# =========================================================
# STREAMING LOOP
# =========================================================

def streaming_loop():
    """
    Main background acquisition loop.

    This function runs in a dedicated thread and continuously:
    - samples hardware sensors
    - applies experiment-level filtering
    - buffers results locally
    - periodically sends batches to PC server

    Notes:
    ------
    This loop is terminated when STATE.streaming_active is set to False.
    """

    print("STREAMING LOOP STARTED")

    # Time between individual sensor reads based on sampling rate
    interval = 1.0 / CONFIG["sample_rate_hz"]

    # Tracks last successful batch transmission time
    last_flush = time.time()

    # Run loop while streaming is active
    while STATE.streaming_active:

        # ---------------------------------------------------------
        # 1. ACQUIRE HARDWARE SNAPSHOT
        # ---------------------------------------------------------

        raw_sample = hardware.read_all_sensors()

        # Filter sensors based on active experiment configuration
        filtered_sample = STATE.filter_enabled_probes(raw_sample)

        # ---------------------------------------------------------
        # 2. BUFFER SAMPLE (THREAD-SAFE OPERATION)
        # ---------------------------------------------------------

        with STATE.buffer_lock:
            STATE.probe_buffer.append({
                "experiment_id": STATE.current_experiment_id,
                "timestamp": raw_sample["timestamp"],
                "sample": filtered_sample
            })

        # ---------------------------------------------------------
        # 3. CHECK IF BUFFER SHOULD BE FLUSHED
        # ---------------------------------------------------------

        if time.time() - last_flush >= CONFIG["flush_interval_sec"]:

            with STATE.buffer_lock:

                # If no data is available, reset timer and continue loop
                if len(STATE.probe_buffer) == 0:
                    last_flush = time.time()
                    continue

                # Copy buffer to avoid race conditions during transmission
                batch = STATE.probe_buffer.copy()
                STATE.probe_buffer.clear()

            # -----------------------------------------------------
            # 4. TRANSMIT DATA TO PC SERVER
            # -----------------------------------------------------

            try:
                requests.post(
                    CONFIG["pc_url"],
                    json={"batch": batch}
                )

                print(f"Sent batch size: {len(batch)}")

            except Exception as e:
                print("Send failed:", e)

                # Restore buffer contents if transmission fails
                with STATE.buffer_lock:
                    STATE.probe_buffer.extend(batch)

            last_flush = time.time()

        # ---------------------------------------------------------
        # 5. ENFORCE SAMPLE RATE
        # ---------------------------------------------------------

        time.sleep(interval)


# =========================================================
# CONTROLLER INTERFACE
# =========================================================

def start_streaming():
    """
    Starts the background streaming thread.

    Returns:
        None
    """

    # Prevent duplicate streaming threads
    if STATE.streaming_active:
        print("Streaming already running")
        return

    STATE.streaming_active = True

    # Start daemon thread so it exits with main process
    STATE.streaming_thread = threading.Thread(
        target=streaming_loop,
        daemon=True
    )

    STATE.streaming_thread.start()


def stop_streaming():
    """
    Stops the streaming loop safely.

    Returns:
        None
    """

    # Signal streaming loop to exit on next iteration
    STATE.streaming_active = False