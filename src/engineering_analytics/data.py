"""Validated ingestion and reproducible synthetic engineering examples."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED = {"timestamp", "machine_id", "voltage_v", "current_a", "temperature_c", "vibration_mm_s", "rpm"}
NUMERIC = REQUIRED - {"timestamp", "machine_id"}


def clean_readings(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate, normalize and deduplicate readings; reject invalid rows clearly."""
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    result = frame.loc[:, sorted(REQUIRED)].copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True, errors="coerce")
    for column in NUMERIC:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = result.dropna(subset=list(REQUIRED)).drop_duplicates(["timestamp", "machine_id"], keep="last")
    if (result[list(NUMERIC)] < 0).any().any():
        raise ValueError("Sensor values and speed must be non-negative")
    if result.empty:
        raise ValueError("No valid readings remain after cleaning")
    return result.sort_values(["machine_id", "timestamp"]).reset_index(drop=True)


def read_csv(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV does not exist: {source}")
    try:
        return clean_readings(pd.read_csv(source))
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse CSV {source}: {exc}") from exc
