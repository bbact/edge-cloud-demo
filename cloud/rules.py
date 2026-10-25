"""Temperature alert rules shared by the processor, API, and tests."""

import os

DEFAULT_THRESHOLD = 80.0
OFFLINE_INTERVALS = 3
THRESHOLD = float(os.environ.get("ALERT_THRESHOLD", DEFAULT_THRESHOLD))


def temperature_value(temperature):
    try:
        return float(temperature)
    except (TypeError, ValueError):
        return None


def judge(temperature) -> str:
    value = temperature_value(temperature)
    if value is None:
        return "normal"
    if value > THRESHOLD:
        return "alert"
    return "normal"


def next_event(previous_status: str | None, temperature) -> dict | None:
    """Return a raise/clear event only when a valid reading crosses the threshold."""
    if temperature_value(temperature) is None:
        return None
    status = judge(temperature)
    if status == "alert" and previous_status != "alert":
        return {"type": "raise", "status": status}
    if status == "normal" and previous_status == "alert":
        return {"type": "clear", "status": status}
    return None


def display_status(record: dict, now: float, interval: float = 2.0) -> str:
    """Mark a device offline after three missed report intervals."""
    try:
        age = float(now) - float(record.get("timestamp"))
    except (TypeError, ValueError):
        return "offline"
    if age > float(interval) * OFFLINE_INTERVALS:
        return "offline"
    status = record.get("status")
    if status in ("normal", "alert"):
        return status
    return "normal"
