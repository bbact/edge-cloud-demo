"""Temperature alert rules shared by the processor and tests."""

THRESHOLD = 80.0


def judge(temperature: float) -> str:
    if temperature > THRESHOLD:
        return "alert"
    return "normal"


def next_event(previous_status: str | None, temperature: float) -> dict | None:
    """Return a raise/clear event only when the device crosses the threshold."""
    status = judge(temperature)
    if status == "alert" and previous_status != "alert":
        return {"type": "raise", "status": status}
    if status == "normal" and previous_status == "alert":
        return {"type": "clear", "status": status}
    return None
