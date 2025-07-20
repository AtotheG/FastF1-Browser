from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import csv
import os
import yaml
import json

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "fastf1.duckdb")
SCHEMA_PATH = os.path.join(os.path.dirname(BASE_DIR), "schema.yaml")
INDEX_PATH = os.path.join(BASE_DIR, "data", "session_index.csv")

app = FastAPI(title="FastF1-browser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/schema")
def get_schema():
    if not os.path.isfile(SCHEMA_PATH):
        raise HTTPException(500, "schema.yaml missing – run cache script.")
    with open(SCHEMA_PATH, encoding="utf8") as f:
        return yaml.safe_load(f)

@app.get("/sessions")
def list_sessions():
    if not os.path.isfile(INDEX_PATH):
        return []
    with open(INDEX_PATH, newline="") as csvfile:
        return list(csv.DictReader(csvfile))

@app.get("/telemetry")
def get_telemetry(session_id: str):
    if not os.path.isfile(DB_PATH):
        raise HTTPException(500, "DuckDB file missing – run cache script.")
    q = "SELECT distance, speed FROM telemetry WHERE session_id = ?"
    with duckdb.connect(DB_PATH, read_only=True) as conn:
        rows = conn.execute(q, [session_id]).fetchall()
    if not rows:
        raise HTTPException(404, "No telemetry for session_id.")
    dist, speed = zip(*rows)
    return {"session_id": session_id, "distance": dist, "speed": speed}
