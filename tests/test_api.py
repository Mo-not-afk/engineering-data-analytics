"""API tests activate when `pip install -e .[test]` provides FastAPI and httpx."""
import os
import tempfile
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
    from engineering_analytics import api
except ImportError:
    TestClient = None
    api = None


@unittest.skipIf(TestClient is None, "Optional FastAPI/httpx test dependencies are unavailable")
class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_db = api.DB_PATH
        api.DB_PATH = Path(cls.temp.name) / "api.db"
        cls.client = TestClient(api.app)

    @classmethod
    def tearDownClass(cls):
        api.DB_PATH = cls.old_db
        cls.temp.cleanup()

    def test_health_and_empty_summary(self):
        self.assertEqual(self.client.get("/healthz").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/api/summary").json()["reading_count"], 0)

    def test_limit_validation(self):
        self.assertEqual(self.client.get("/api/readings?limit=0").status_code, 422)


if __name__ == "__main__":
    unittest.main()
