"""Generate a deterministic synthetic two-machine condition-monitoring CSV."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import math
import random

ROOT = Path(__file__).resolve().parent
random.seed(24)
start = datetime(2025, 4, 1, tzinfo=timezone.utc)
ROOT.joinpath("data").mkdir(parents=True, exist_ok=True)
with (ROOT / "data" / "machine_readings.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["timestamp", "machine_id", "voltage_v", "current_a", "temperature_c", "vibration_mm_s", "rpm"])
    for i in range(240):
        for machine, phase in (("pump-01", 0), ("fan-02", 1)):
            t = start + timedelta(minutes=5 * i)
            vibration = 1.4 + .12 * math.sin(i / 9 + phase) + random.gauss(0, .09)
            if machine == "pump-01" and 170 <= i <= 190:  # synthetic bearing-like event for analysis exercises
                vibration += .75
            writer.writerow([t.isoformat(), machine, round(230 + 1.1 * math.sin(i / 12), 2),
                             round((2.4 if phase == 0 else 1.6) + .08 * math.sin(i / 7), 3),
                             round((48 if phase == 0 else 39) + 2 * math.sin(i / 30) + random.gauss(0, .35), 2),
                             round(vibration, 3), round((1450 if phase == 0 else 980) + 10 * math.sin(i / 8), 1)])
