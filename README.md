# FastF1-Browser
To Interact with F1 data cached using FastF1

## Scripts
- `backend/scripts/prepare_dummy_db.py` generates a small dummy DuckDB for local testing.
- `backend/scripts/reset_db.py` clears any in-memory DB state.

Backend data and cache directories are ignored via `.gitignore`.

## API Server

Run the FastAPI app locally with:

```bash
uvicorn backend.main:app --reload
```

Available endpoints:

- `/config/cache_path` – POST a directory path to configure the cache.
- `/schema` – returns the YAML schema.
- `/sessions` – lists sessions from `session_index.csv`.
- `/telemetry` – returns telemetry data for a session.

Call `/config/cache_path` before using `/telemetry` so the server knows where to
find `fastf1.duckdb`. `/sessions` reads from the built-in `session_index.csv` by
default.
