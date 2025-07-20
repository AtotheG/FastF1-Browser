from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import csv
import os
import yaml
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR.parent / "schema.yaml"

# Cache configuration; set via /config/cache_path
CACHE_DIR = None
DB_PATH = None
INDEX_PATH = BASE_DIR.parent / "session_index.csv"

app = FastAPI(title="FastF1-browser API")


def _write_session_index(index_path: str, pkl_files):
    """Create a minimal ``session_index.csv`` from ``*.ff1pkl`` files."""
    header = ["session_id", "year", "event_name", "event_date", "session_type", "sid"]
    pattern = re.compile(
        r"(?P<year>\d{4})_(?P<event_date>\d{4}-\d{2}-\d{2})_(?P<event_name>.*)_(?P<sid>FP1|FP2|FP3|Q|R)$"
    )
    type_map = {
        "FP1": "Practice 1",
        "FP2": "Practice 2",
        "FP3": "Practice 3",
        "Q": "Qualifying",
        "R": "Race",
    }

    with open(index_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for pkl in pkl_files:
            stem = pkl.stem
            m = pattern.match(stem)
            if not m:
                continue
            year = m.group("year")
            event_date = m.group("event_date")
            event_name = m.group("event_name").replace("_", " ")
            sid = m.group("sid")
            session_type = type_map.get(sid, sid)
            writer.writerow([stem, year, event_name, event_date, session_type, sid])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/config/cache_path")
def set_cache_path(path: str):
    """Configure directory that stores cached FastF1 data."""
    if not os.path.isdir(path):
        raise HTTPException(400, "Invalid cache directory")
    db_path = os.path.join(path, "fastf1.duckdb")
    index_path = os.path.join(path, "session_index.csv")

    # If the session index does not exist, attempt to create it from any
    # ``*.ff1pkl`` files found in the cache directory. This mirrors how a real
    # FastF1 cache would be initialised.
    if not os.path.isfile(index_path):
        pkl_files = list(Path(path).glob("*.ff1pkl"))
        if pkl_files:
            _write_session_index(index_path, pkl_files)
        else:
            raise HTTPException(400, "Cache directory missing required files")

    if not os.path.isfile(db_path) or not os.path.isfile(index_path):
        raise HTTPException(400, "Cache directory missing required files")
    global CACHE_DIR, DB_PATH, INDEX_PATH
    CACHE_DIR = path
    DB_PATH = db_path
    INDEX_PATH = index_path
    return {"cache_dir": CACHE_DIR}


@app.get("/schema")
def get_schema():
    if not os.path.isfile(SCHEMA_PATH):
        raise HTTPException(500, "schema.yaml missing – run cache script.")
    with open(SCHEMA_PATH, encoding="utf8") as f:
        return yaml.safe_load(f)


@app.get("/sessions")
def list_sessions():
    if not os.path.isfile(INDEX_PATH):
        raise HTTPException(500, "session_index.csv missing")
    with open(INDEX_PATH, newline="") as csvfile:
        return list(csv.DictReader(csvfile))


@app.get("/telemetry")
def get_telemetry(session_id: str):
    if CACHE_DIR is None:
        raise HTTPException(400, "Cache directory not configured")
    if not os.path.isfile(DB_PATH):
        raise HTTPException(500, "DuckDB file missing in cache directory")
    q = "SELECT distance, speed FROM telemetry WHERE session_id = ?"
    with duckdb.connect(DB_PATH, read_only=True) as conn:
        rows = conn.execute(q, [session_id]).fetchall()
    if not rows:
        raise HTTPException(404, "No telemetry for session_id.")
    dist, speed = zip(*rows)
    return {"session_id": session_id, "distance": dist, "speed": speed}
