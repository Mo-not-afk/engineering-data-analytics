"""SQLite persistence with explicit transactions and parameterized queries."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
import pandas as pd


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def database(path: str | Path):
    """Close a SQLite connection reliably, including when work raises."""
    connection = connect(path)
    try:
        yield connection
    finally:
        connection.close()


def initialize(connection: sqlite3.Connection) -> None:
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    connection.executescript(schema)


def ingest(connection: sqlite3.Connection, frame: pd.DataFrame) -> int:
    """Insert a cleaned batch atomically, creating machine records as needed."""
    rows = frame.to_dict(orient="records")
    try:
        with connection:
            for machine_id in sorted({str(row["machine_id"]) for row in rows}):
                connection.execute("INSERT OR IGNORE INTO machines(machine_id) VALUES (?)", (machine_id,))
            connection.executemany(
                """INSERT OR REPLACE INTO sensor_readings
                (timestamp, machine_id, voltage_v, current_a, temperature_c, vibration_mm_s, rpm)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [(row["timestamp"].isoformat(), str(row["machine_id"]), float(row["voltage_v"]),
                  float(row["current_a"]), float(row["temperature_c"]), float(row["vibration_mm_s"]), float(row["rpm"]))
                 for row in rows],
            )
    except sqlite3.Error as exc:
        raise RuntimeError(f"Database ingestion failed: {exc}") from exc
    return len(rows)


def joined_readings(connection: sqlite3.Connection, machine_id: str | None = None) -> pd.DataFrame:
    query = """SELECT r.timestamp, r.machine_id, m.location, r.voltage_v, r.current_a,
    r.temperature_c, r.vibration_mm_s, r.rpm
    FROM sensor_readings r JOIN machines m USING(machine_id)"""
    if machine_id is not None:
        query += " WHERE r.machine_id = ?"
        rows = connection.execute(query + " ORDER BY r.timestamp", (machine_id,)).fetchall()
    else:
        rows = connection.execute(query + " ORDER BY r.timestamp", ()).fetchall()
    return pd.DataFrame([dict(row) for row in rows])
