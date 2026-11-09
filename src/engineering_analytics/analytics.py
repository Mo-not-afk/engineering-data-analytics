"""Engineering summaries derived from joined sensor readings."""
import pandas as pd


def summarize(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {"reading_count": 0, "machines": 0, "mean_temperature_c": None,
                "p95_vibration_mm_s": None, "mean_apparent_power_va": None}
    power = frame["voltage_v"] * frame["current_a"]
    return {
        "reading_count": int(len(frame)),
        "machines": int(frame["machine_id"].nunique()),
        "mean_temperature_c": round(float(frame["temperature_c"].mean()), 3),
        "p95_vibration_mm_s": round(float(frame["vibration_mm_s"].quantile(.95)), 3),
        "mean_apparent_power_va": round(float(power.mean()), 3),
    }
