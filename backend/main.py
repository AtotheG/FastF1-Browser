from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import csv
import os
import yaml
from pathlib import Path
import re

# If backend is a package, the relative import is correct; otherwise adjust.
try:
    from .scripts.build_session_index import build_session_index
except ImportError:
    build_session_index = None  # Fallback handled below

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR.parent / "schema.yaml"

# These will be set after /config/cache_path
CACHE_DIR: Path | None = None
DB_PATH: Path | None = None
INDEX_PATH: Path | None = BASE_DIR.parent / "session_index.csv"

app = FastAPI(title="FastF1-browser API")


# ---------------------------------------------------------------------------
# Fallback minimal index builder (regex-based) if build_session_index unavailable
# or fails. Expects flat collection of *.ff1pkl named like:
#   2024_2024-06-30_Austrian_Grand_Prix_FP1.ff1pkl
# Adjust the pattern if your naming differs.
# ---------------------------------------------------------------------------
_FALLBACK_PATTERN = re.compile(
    r"(?P<year>\d{4})_(?P<event_date>\d{4}-\d{2}-\d{2})_(?P<event_name>.+)_(?P<sid>FP1|FP2|FP3|SQ|SS|Q|S|R)\.ff1pkl$"
)
_SID_LONG = {
    "FP1": "Practice 1",
    "FP2": "Practice 2",
    "FP3": "Practice 3",
    "SQ": "Sprint Qualifying",
    "SS": "Sprint Shootout",
    "Q": "Qualifying",
    "S": "Sprint",
    "R": "Race",
}


def _fallback_write_session_index(index_path: Path, cache_dir: Path) -> int:
    pkl_files = list(cache_dir.rglob("*.ff1pkl"))
    rows = []
    for p in pkl_files:
        m = _FALLBACK_PATTERN.match(p.name)
        if not m:
            continue
        year = m.group("year")
        event_date = m.group("event_date")
        event_name = m.group("event_name").replace("_", " ")
        sid = m.group("sid")
        session_type = _SID_LONG.get(sid, sid)
        session_id = f"{year}_{event_date}_{event_name}_{sid}"
        rows.append(
            {
                "session_id": session_id,
                "year": year,
                "event_name": event_name,
                "event_date": event_date,
                "session_type": session_type,
                "sid": sid,
            }
        )

    if not rows:
        raise FileNotFoundError("No ff1pkl files matched fallback pattern")

    rows.sort(key=lambda r: (r["year"], r["event_date"], r["sid"]))
    with index_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "session_id",
                "year",
                "event_name",
                "event_date",
                "session_type",
                "sid",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Configuration Endpoint
# ---------------------------------------------------------------------------
@app.post("/config/cache_path")
def set_cache_path(path: str):
    """
    Configure directory holding the FastF1 cache artifacts.

    Expected contents:
      - fastf1.duckdb (DB built by your ingestion script)
      - session_index.csv (else we try to build it)
      - *.ff1pkl (raw cache files; used only for index build if needed)
    """
    cache_dir = Path(path)
    if not cache_dir.is_dir():
        raise HTTPException(status_code=400, detail="Invalid cache directory")

    db_path = cache_dir / "fastf1.duckdb"
    if not db_path.is_file():
        raise HTTPException(status_code=400, detail="Missing fastf1.duckdb in cache directory")

    index_path = cache_dir / "session_index.csv"

    added = 0
    if build_session_index is not None:
        try:
            added = build_session_index(cache_dir, index_path)
        except FileNotFoundError:
            # Fall through to fallback
            pass
        except Exception as e:
            # Unexpected error: continue to fallback
            print(f"[WARN] build_session_index failed: {e!r}")

    if not index_path.is_file():
        # Fallback regex approach
        try:
            added = _fallback_write_session_index(index_path, cache_dir)
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot build session_index.csv: {e}",
            )

    # Final sanity checks
    if not index_path.is_file():
        raise HTTPException(status_code=500, detail="Failed to create session_index.csv")
    if not db_path.is_file():
        raise HTTPException(status_code=500, detail="fastf1.duckdb missing after setup")

    global CACHE_DIR, DB_PATH, INDEX_PATH
    CACHE_DIR = cache_dir
    DB_PATH = db_path
    INDEX_PATH = index_path

    return {
        "cache_dir": str(CACHE_DIR),
        "db": str(DB_PATH),
        "index": str(INDEX_PATH),
        "added": added,
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
@app.get("/schema")
def get_schema():
    if not SCHEMA_PATH.is_file():
        raise HTTPException(status_code=500, detail="schema.yaml missing – add it to repo root.")
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Sessions listing
# ---------------------------------------------------------------------------
@app.get("/sessions")
def list_sessions():
    if INDEX_PATH is None or not Path(INDEX_PATH).is_file():
        raise HTTPException(status_code=500, detail="session_index.csv missing – configure cache.")
    with Path(INDEX_PATH).open(newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


# ---------------------------------------------------------------------------
# Telemetry sample endpoint
# ---------------------------------------------------------------------------
@app.get("/telemetry")
def get_telemetry(session_id: str):
    """
    Return basic distance/speed telemetry for a session.
    Assumes a DuckDB table `telemetry(distance DOUBLE, speed DOUBLE, session_id TEXT)`
    """
    if CACHE_DIR is None or DB_PATH is None:
        raise HTTPException(status_code=400, detail="Cache directory not configured; POST /config/cache_path first.")
    if not DB_PATH.is_file():
        raise HTTPException(status_code=500, detail="DuckDB file missing in cache directory")

    query = "SELECT distance, speed FROM telemetry WHERE session_id = ?"
    with duckdb.connect(str(DB_PATH), read_only=True) as conn:
        rows = conn.execute(query, [session_id]).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No telemetry for session_id")

    distance, speed = zip(*rows) if rows else ([], [])
    return {"session_id": session_id, "distance": distance, "speed": speed}
