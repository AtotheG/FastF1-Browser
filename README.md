# FastF1-Browser
To Interact with F1 data cached using FastF1

## Scripts
- `backend/scripts/prepare_dummy_db.py` generates a small dummy DuckDB for local testing.
- `backend/scripts/reset_db.py` clears any in-memory DB state.
- `backend/scripts/build_session_index.py` builds the `session_index.csv` cache index.

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

- `/config/cache_path` – POST a directory path to configure the cache. This call
  runs `backend/scripts/build_session_index.py` which generates
  `session_index.csv` from any `.ff1pkl` files in the directory.
- `/schema` – returns the YAML schema.
- `/sessions` – lists sessions from `session_index.csv`.
- `/telemetry` – returns telemetry data for a session.

Call `/config/cache_path` before using `/telemetry` so the server knows where to
find `fastf1.duckdb`. The invoked script scans the given folder for `.ff1pkl`
files and writes the discovered sessions to `session_index.csv`. If no such
cache files exist, the endpoint fails with an error. `/sessions` reads from the
built-in `session_index.csv` by default.

## Frontend

The React application lives in `frontend/` and uses Vite.
Install dependencies and start the dev server:

```bash
cd frontend
npm install
npm run dev
```

Run `npm run lint` to check TypeScript code.
