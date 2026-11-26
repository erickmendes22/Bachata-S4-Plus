"""Single source of truth for the two validated native APK core artifacts."""
import json
import re
from pathlib import Path

PINS_PATH = Path(__file__).with_name("reuse_core.json")

def read_pins(path=PINS_PATH):
    pins = json.loads(path.read_text(encoding="utf-8"))
    for key in ("run", "sotc_run"):
        if type(pins.get(key)) is not int or pins[key] <= 0:
            raise ValueError(f"Invalid core run pin: {key}")
    for key in ("revision", "sotc_revision"):
        value = pins.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
            raise ValueError(f"Invalid core revision pin: {key}")
    if pins["run"] == pins["sotc_run"] or pins["revision"] == pins["sotc_revision"]:
        raise ValueError("The dedicated SotC core must have its own validated artifact")
    return pins

def require_revision(raw, expected, label):
    marker = f"BACHATA_CORE_REVISION={expected}".encode("ascii")
    if marker not in raw:
        raise ValueError(f"{label} revision mismatch; expected {expected}")

if __name__ == "__main__":
    p = read_pins()
    print(p["run"], p["revision"], p["sotc_run"], p["sotc_revision"])
