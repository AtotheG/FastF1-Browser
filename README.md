# FastF1-Browser
To Interact with F1 data cached using FastF1

## Scripts
- `backend/scripts/prepare_dummy_db.py` generates a small dummy DuckDB for local testing.
- `backend/scripts/reset_db.py` clears any in-memory DB state.

Backend data and cache directories are ignored via `.gitignore`.

## Setup

Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

For local testing you can generate a dummy database before starting the
server:

```bash
python backend/scripts/prepare_dummy_db.py
```

## API Server

Run the FastAPI app locally with:

```bash
uvicorn backend.main:app --reload
```

Run `python backend/scripts/prepare_dummy_db.py` beforehand to create a test
database if you don't already have one.

Available endpoints:

- `/config/cache_path` – POST a directory path to configure the cache.
- `/schema` – returns the YAML schema.
- `/sessions` – lists sessions from `session_index.csv`.
- `/telemetry` – returns telemetry data for a session.

Call `/config/cache_path` before using `/telemetry` so the server knows where to
find `fastf1.duckdb`. `/sessions` reads from the built-in `session_index.csv` by
default.
