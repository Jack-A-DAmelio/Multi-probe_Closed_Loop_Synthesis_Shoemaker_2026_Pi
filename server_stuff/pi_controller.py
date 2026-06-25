"""
Controller layer

Author: Jack A. D'Amelio
Date: 2026-06-24
Internal Pi-Hardware Version: v0.1
"""

import time
import threading
import requests

import hardware.hardware as hardware
from server_stuff.controller_state import STATE


# =========================================================
# CONSTANTS (NOT CONFIG STATE)
# =========================================================

PC_URL = "http://127.0.0.1:8000/ingest"


# =========================================================
# STREAMING LOOP
# =========================================================

def streaming_loop():
    """
    Main background acquisition loop.
    """

    print("STREAMING LOOP STARTED")

    last_flush = time.time()

    while STATE.streaming_active:

        # ---------------------------------------------------------
        # LIVE SAMPLE RATE (NO CACHE)
        # ---------------------------------------------------------

        sample_rate = STATE.sample_rate_hz
        if sample_rate <= 0:
            print("WARNING: invalid sample_rate_hz =", sample_rate)
            sample_rate = 1.0

        interval = 1.0 / sample_rate

        # ---------------------------------------------------------
        # 1. ACQUIRE HARDWARE SNAPSHOT
        # ---------------------------------------------------------

        raw_sample = hardware.read_all_sensors()

        print(raw_sample)

        filtered_sample = STATE.filter_enabled_probes(raw_sample)

        print(len(filtered_sample), "probes sampled:", filtered_sample)

        # ---------------------------------------------------------
        # 2. BUFFER SAMPLE
        # ---------------------------------------------------------

        with STATE.buffer_lock:
            STATE.probe_buffer.append({
                "experiment_id": STATE.current_experiment_id,
                "timestamp": raw_sample["timestamp"],
                "sample": filtered_sample
            })

        # ---------------------------------------------------------
        # 3. FLUSH LOGIC (LIVE STATE)
        # ---------------------------------------------------------

        flush_interval = STATE.flush_interval_sec
        if flush_interval <= 0:
            flush_interval = 1.0  # safe fallback

        if time.time() - last_flush >= flush_interval:

            with STATE.buffer_lock:

                if len(STATE.probe_buffer) == 0:
                    last_flush = time.time()
                    continue

                batch = STATE.probe_buffer.copy()
                STATE.probe_buffer.clear()

            # -----------------------------------------------------
            # 4. TRANSMIT DATA
            # -----------------------------------------------------

            try:
                requests.post(
                    PC_URL,
                    json={"batch": batch}
                )

                print(f"Sent batch size: {len(batch)}")

            except Exception as e:
                print("Send failed:", e)

                with STATE.buffer_lock:
                    STATE.probe_buffer.extend(batch)

            last_flush = time.time()

        # ---------------------------------------------------------
        # 5. SAMPLE RATE ENFORCEMENT
        # ---------------------------------------------------------

        time.sleep(interval)


# =========================================================
# CONTROLLER INTERFACE
# =========================================================

def start_streaming():

    if STATE.streaming_active:
        print("Streaming already running")
        return

    STATE.streaming_active = True

    STATE.streaming_thread = threading.Thread(
        target=streaming_loop,
        daemon=True
    )

    STATE.streaming_thread.start()


def stop_streaming():
    STATE.streaming_active = False