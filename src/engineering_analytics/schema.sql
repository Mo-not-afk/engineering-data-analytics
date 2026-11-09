PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS machines (
    machine_id TEXT PRIMARY KEY,
    location TEXT NOT NULL DEFAULT 'Unspecified'
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    voltage_v REAL NOT NULL CHECK (voltage_v >= 0),
    current_a REAL NOT NULL CHECK (current_a >= 0),
    temperature_c REAL NOT NULL CHECK (temperature_c >= 0),
    vibration_mm_s REAL NOT NULL CHECK (vibration_mm_s >= 0),
    rpm REAL NOT NULL CHECK (rpm >= 0),
    PRIMARY KEY (timestamp, machine_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE INDEX IF NOT EXISTS idx_readings_machine_time
    ON sensor_readings(machine_id, timestamp);
