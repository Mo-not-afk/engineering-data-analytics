"""Optional FastAPI app; imported only when serving the API."""
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException

from .analytics import summarize
from .store import database, initialize, joined_readings

DB_PATH = Path(os.environ.get("ENGINEERING_DB", "data/engineering.db"))
app = FastAPI(title="Engineering Data Analytics API", version="1.0.0")


def get_frame(machine_id: str | None = None):
    try:
        with database(DB_PATH) as db:
            initialize(db)
            return joined_readings(db, machine_id)
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail="Analytics database unavailable") from exc


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/api/readings")
def readings(machine_id: str | None = None, limit: int = 100):
    if not 1 <= limit <= 1000:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 1000")
    frame = get_frame(machine_id).head(limit)
    return frame.astype(object).where(frame.notna(), None).to_dict(orient="records")


@app.get("/api/summary")
def summary(machine_id: str | None = None):
    return summarize(get_frame(machine_id))
