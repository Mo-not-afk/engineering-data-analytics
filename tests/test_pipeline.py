import tempfile
import unittest
from pathlib import Path

import pandas as pd

from engineering_analytics.analytics import summarize
from engineering_analytics.data import clean_readings, read_csv
from engineering_analytics.store import connect, initialize, ingest, joined_readings


class PipelineTests(unittest.TestCase):
    def test_clean_deduplicates_and_sorts(self):
        source = pd.DataFrame([
            ["2025-01-02T00:00:00Z", "m1", 220, 2, 44, 1.2, 1400],
            ["2025-01-01T00:00:00Z", "m1", 221, 2, 43, 1.1, 1401],
            ["2025-01-02T00:00:00Z", "m1", 222, 2, 45, 1.4, 1400],
        ], columns=["timestamp", "machine_id", "voltage_v", "current_a", "temperature_c", "vibration_mm_s", "rpm"])
        result = clean_readings(source)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["voltage_v"], 221)

    def test_validation_and_missing_file_errors(self):
        with self.assertRaisesRegex(ValueError, "Missing required"):
            clean_readings(pd.DataFrame({"timestamp": []}))
        with self.assertRaises(FileNotFoundError):
            read_csv("missing-file.csv")

    def test_sql_join_ingestion_and_summary(self):
        frame = clean_readings(pd.DataFrame([
            ["2025-01-01T00:00:00Z", "m1", 230, 2, 50, 1.5, 1500],
            ["2025-01-01T00:00:00Z", "m2", 220, 1, 40, 2.5, 1000],
        ], columns=["timestamp", "machine_id", "voltage_v", "current_a", "temperature_c", "vibration_mm_s", "rpm"]))
        with tempfile.TemporaryDirectory() as temp:
            db = connect(Path(temp) / "test.db")
            try:
                initialize(db)
                self.assertEqual(ingest(db, frame), 2)
                joined = joined_readings(db, "m1")
                self.assertEqual(joined.iloc[0]["location"], "Unspecified")
                result = summarize(joined)
                self.assertEqual(result["mean_apparent_power_va"], 460.0)
                self.assertEqual(result["reading_count"], 1)
            finally:
                db.close()

    def test_empty_summary(self):
        self.assertEqual(summarize(pd.DataFrame())["reading_count"], 0)


if __name__ == "__main__":
    unittest.main()
