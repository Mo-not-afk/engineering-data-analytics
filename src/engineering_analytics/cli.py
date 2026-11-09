"""Command-line entry point for importing and serving the sample data."""
import argparse
from pathlib import Path

from .analytics import summarize
from .data import read_csv
from .store import database, ingest, initialize, joined_readings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    load = sub.add_parser("ingest", help="validate CSV and store sensor readings")
    load.add_argument("csv", type=Path)
    load.add_argument("--db", type=Path, default=Path("data/engineering.db"))
    serve = sub.add_parser("serve", help="start the REST API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "ingest":
        frame = read_csv(args.csv)
        with database(args.db) as db:
            initialize(db)
            count = ingest(db, frame)
            print(f"Imported {count} readings. Summary: {summarize(joined_readings(db))}")
        return 0
    try:
        import uvicorn
    except ImportError:
        parser.error("Serving requires optional API dependencies: pip install -e .[api]")
    uvicorn.run("engineering_analytics.api:app", host=args.host, port=args.port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
