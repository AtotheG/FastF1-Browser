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

- `/schema` – returns the YAML schema.
- `/sessions` – lists sessions from the cached CSV.
- `/telemetry` – returns telemetry data for a session.
